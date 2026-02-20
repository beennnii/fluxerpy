"""
WebSocket Gateway client for Fluxer API.

Follows the Discord-compatible Gateway protocol used by Fluxer.
Handles: connect, identify, heartbeat, resume, reconnect, event dispatch.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Any, Callable, Dict, List, Optional

import aiohttp

_log = logging.getLogger("fluxerpy3.gateway")
if not _log.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter("[fluxerpy3.gateway] %(levelname)s %(message)s"))
    _log.addHandler(_handler)
_log.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# Gateway opcodes (Discord-compatible)
# ---------------------------------------------------------------------------
class Opcode:
    DISPATCH          = 0
    HEARTBEAT         = 1
    IDENTIFY          = 2
    PRESENCE_UPDATE   = 3
    RESUME            = 6
    RECONNECT         = 7
    INVALID_SESSION   = 9
    HELLO             = 10
    HEARTBEAT_ACK     = 11

# ---------------------------------------------------------------------------
# Gateway intents
# ---------------------------------------------------------------------------
class Intents:
    GUILDS           = 1 << 0   # guild create/update/delete, channel events
    GUILD_MEMBERS    = 1 << 1   # member join/leave/update
    GUILD_MESSAGES   = 1 << 9   # MESSAGE_CREATE / UPDATE / DELETE in guilds
    MESSAGE_CONTENT  = 1 << 15  # access to message.content field

    # Sensible default: guilds + messages + message content
    DEFAULT = GUILDS | GUILD_MESSAGES | MESSAGE_CONTENT


class GatewayClient:
    """
    Manages a single WebSocket connection to the Fluxer Gateway.

    Usage::

        gw = GatewayClient(token="Bot TOKEN", gateway_url="wss://...")
        gw.on("MESSAGE_CREATE", my_handler)   # async def my_handler(data): ...
        await gw.connect()
    """

    def __init__(
        self,
        token: str,
        gateway_url: str,
        intents: int = Intents.DEFAULT,
        shard_id: int = 0,
        shard_count: int = 1,
    ):
        self.token = token
        self.gateway_url = gateway_url
        self.intents = intents
        self.shard_id = shard_id
        self.shard_count = shard_count

        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._heartbeat_interval: float = 41.25  # seconds; overridden on HELLO
        self._last_sequence: Optional[int] = None
        self._session_id: Optional[str] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._closed = False

        # event_name -> list of async callbacks
        self._handlers: Dict[str, List[Callable]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def on(self, event: str, handler: Callable):
        """Register an async handler for a gateway event (e.g. 'MESSAGE_CREATE')."""
        self._handlers.setdefault(event.upper(), []).append(handler)

    async def connect(self):
        """Connect to the gateway and run until closed or a fatal error."""
        self._closed = False
        connector = aiohttp.TCPConnector(family=2)  # force IPv4
        self._session = aiohttp.ClientSession(connector=connector)
        try:
            await self._run()
        finally:
            await self._cleanup()

    async def close(self):
        """Gracefully close the gateway connection."""
        self._closed = True
        if self._ws and not self._ws.closed:
            await self._ws.close()

    async def update_presence(self, status: str = "online", activity: Optional[Dict] = None):
        """
        Send a Presence Update to the gateway.

        status: "online" | "idle" | "dnd" | "invisible"
        activity: optional dict, e.g. {"name": "Listening to commands", "type": 2}
        """
        payload: Dict[str, Any] = {
            "op": Opcode.PRESENCE_UPDATE,
            "d": {
                "since": None,
                "activities": [activity] if activity else [],
                "status": status,
                "afk": False,
            },
        }
        await self._send(payload)

    # ------------------------------------------------------------------
    # Internal – connection loop
    # ------------------------------------------------------------------

    async def _run(self):
        resume = False
        while not self._closed:
            url = self.gateway_url
            if "?" not in url:
                url += "?v=1&encoding=json"

            _log.info("Connecting to gateway: %s", url)
            try:
                async with self._session.ws_connect(url) as ws:
                    self._ws = ws
                    if resume and self._session_id and self._last_sequence is not None:
                        await self._resume()
                        resume = False
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            should_resume = await self._handle_message(data)
                            if should_resume:
                                resume = True
                                break  # reconnect with RESUME
                        elif msg.type in (
                            aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR,
                        ):
                            _log.warning("WebSocket closed/error: %s", msg)
                            break
            except Exception as exc:
                _log.error("Gateway connection error: %s", exc, exc_info=True)

            if self._closed:
                break

            self._stop_heartbeat()
            backoff = 5
            _log.info("Reconnecting in %ds...", backoff)
            await asyncio.sleep(backoff)

    async def _handle_message(self, data: Dict) -> bool:
        """
        Handle a gateway message.
        Returns True when a RESUME reconnect is needed.
        """
        op = data.get("op")
        payload = data.get("d")
        seq = data.get("s")
        event_name = data.get("t")

        if seq is not None:
            self._last_sequence = seq

        if op == Opcode.HELLO:
            self._heartbeat_interval = payload["heartbeat_interval"] / 1000
            _log.debug("HELLO received, heartbeat interval: %.2fs", self._heartbeat_interval)
            self._start_heartbeat()
            await self._identify()

        elif op == Opcode.HEARTBEAT_ACK:
            _log.debug("Heartbeat ACK")

        elif op == Opcode.HEARTBEAT:
            await self._send_heartbeat()

        elif op == Opcode.DISPATCH:
            if event_name == "READY":
                self._session_id = payload.get("session_id")
                user = payload.get("user", {})
                _log.info(
                    "Gateway READY – logged in as %s#%s",
                    user.get("username", "?"),
                    user.get("discriminator", "0"),
                )
                # Immediately set presence to online
                await self.update_presence(status="online")
                await self._dispatch("READY", payload)
            else:
                await self._dispatch(event_name, payload)

        elif op == Opcode.RECONNECT:
            _log.info("Server requested reconnect (RESUME)")
            return True  # signal reconnect

        elif op == Opcode.INVALID_SESSION:
            resumable = bool(payload)
            _log.warning("Invalid session (resumable=%s)", resumable)
            if not resumable:
                self._session_id = None
                self._last_sequence = None
            await asyncio.sleep(3)
            return True

        return False

    # ------------------------------------------------------------------
    # Internal – sending
    # ------------------------------------------------------------------

    async def _send(self, payload: Dict):
        if self._ws and not self._ws.closed:
            await self._ws.send_str(json.dumps(payload))

    async def _identify(self):
        payload = {
            "op": Opcode.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "os": "windows",
                    "browser": "fluxerpy3",
                    "device": "fluxerpy3",
                },
                "presence": {
                    "since": None,
                    "activities": [],
                    "status": "online",
                    "afk": False,
                },
                "shard": [self.shard_id, self.shard_count],
            },
        }
        _log.debug("Sending IDENTIFY")
        await self._send(payload)

    async def _resume(self):
        payload = {
            "op": Opcode.RESUME,
            "d": {
                "token": self.token,
                "session_id": self._session_id,
                "seq": self._last_sequence,
            },
        }
        _log.debug("Sending RESUME (seq=%s)", self._last_sequence)
        await self._send(payload)

    # ------------------------------------------------------------------
    # Internal – heartbeat
    # ------------------------------------------------------------------

    def _start_heartbeat(self):
        self._stop_heartbeat()
        self._heartbeat_task = asyncio.ensure_future(self._heartbeat_loop())

    def _stop_heartbeat(self):
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
        self._heartbeat_task = None

    async def _heartbeat_loop(self):
        # Jitter: wait a random portion of the interval before the first beat
        import random
        await asyncio.sleep(self._heartbeat_interval * random.random())
        while True:
            await self._send_heartbeat()
            await asyncio.sleep(self._heartbeat_interval)

    async def _send_heartbeat(self):
        payload = {"op": Opcode.HEARTBEAT, "d": self._last_sequence}
        _log.debug("Sending heartbeat (seq=%s)", self._last_sequence)
        await self._send(payload)

    # ------------------------------------------------------------------
    # Internal – event dispatch
    # ------------------------------------------------------------------

    async def _dispatch(self, event_name: str, data: Any):
        handlers = self._handlers.get(event_name, [])
        for handler in handlers:
            try:
                await handler(data)
            except Exception as exc:
                _log.error(
                    "Error in handler for %s: %s", event_name, exc, exc_info=True
                )

    # ------------------------------------------------------------------
    # Internal – cleanup
    # ------------------------------------------------------------------

    async def _cleanup(self):
        self._stop_heartbeat()
        if self._session and not self._session.closed:
            await self._session.close()
