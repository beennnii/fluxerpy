"""
Main client for Fluxer API
"""

from typing import Optional, List, Dict, Callable
from .http import HTTPClient
from .models import User, Guild, Channel, Member, Role, Message, Reaction


class Client:
    """
    Main client for interacting with the Fluxer API.
    Similar to discord.py's Client class.

    Example:
        ```python
        import fluxerpy3
        import asyncio

        client = fluxerpy3.Client(token="your_bot_token")

        async def main():
            async with client:
                me = await client.get_me()
                print(f"Logged in as: {me.username}")

                # List all guilds the bot is in
                guilds = await client.get_guilds()
                for guild in guilds:
                    print(f"Guild: {guild.name}")

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.fluxer.app/v1",
    ):
        """
        Initialize the Fluxer client.

        Args:
            token: Bot token for authentication
            base_url: Base URL for the API (default: https://api.fluxer.app/v1)
        """
        self.token = token
        self.base_url = base_url
        self.http = HTTPClient(base_url=base_url, token=token)
        self._event_handlers: Dict[str, List[Callable]] = {}

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def start(self):
        """Start the client and initialize the HTTP session"""
        await self.http.start()

    async def close(self):
        """Close the client and cleanup resources"""
        await self.http.close()

    # ------------------------------------------------------------------
    # Event system
    # ------------------------------------------------------------------

    def event(self, func: Callable):
        """
        Decorator to register event handlers.

        Example:
            ```python
            @client.event
            async def on_message_create(message):
                print(f"New message: {message.content}")
            ```
        """
        event_name = func.__name__
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(func)
        return func

    async def dispatch(self, event_name: str, *args, **kwargs):
        """Dispatch an event to all registered handlers"""
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                await handler(*args, **kwargs)
            except Exception as e:
                print(f"Error in event handler {event_name}: {e}")

    # ------------------------------------------------------------------
    # User endpoints
    # ------------------------------------------------------------------

    async def get_me(self) -> User:
        """
        Get the currently authenticated bot user.

        Returns:
            User object representing the bot account
        """
        data = await self.http.get("users/@me")
        return User(data, client=self)

    async def get_user(self, user_id: str) -> User:
        """
        Get a user by their ID.

        Args:
            user_id: The Snowflake ID of the user

        Returns:
            User object
        """
        data = await self.http.get(f"users/{user_id}")
        return User(data, client=self)

    async def get_user_by_username(self, username: str) -> User:
        """
        Lookup a user by their username.

        Args:
            username: The username to search for

        Returns:
            User object
        """
        data = await self.http.get(f"users/username/{username}")
        return User(data, client=self)

    # ------------------------------------------------------------------
    # Guild endpoints
    # ------------------------------------------------------------------

    async def get_guilds(self) -> List[Guild]:
        """
        Get all guilds (servers) the bot is a member of.

        Returns:
            List of Guild objects
        """
        data = await self.http.get("users/@me/guilds")
        guilds = data if isinstance(data, list) else []
        return [Guild(g, client=self) for g in guilds]

    async def get_guild(self, guild_id: str) -> Guild:
        """
        Get a specific guild by ID.

        Args:
            guild_id: The ID of the guild

        Returns:
            Guild object
        """
        data = await self.http.get(f"guilds/{guild_id}")
        return Guild(data, client=self)

    async def get_guild_channels(self, guild_id: str) -> List[Channel]:
        """
        Get all channels in a guild.

        Args:
            guild_id: The ID of the guild

        Returns:
            List of Channel objects
        """
        data = await self.http.get(f"guilds/{guild_id}/channels")
        channels = data if isinstance(data, list) else []
        return [Channel(c, client=self) for c in channels]

    async def get_guild_members(self, guild_id: str, limit: int = 100) -> List[Member]:
        """
        List members of a guild.

        Args:
            guild_id: The ID of the guild
            limit: Maximum number of members to return (max 1000)

        Returns:
            List of Member objects
        """
        data = await self.http.get(
            f"guilds/{guild_id}/members",
            params={"limit": limit},
        )
        members = data if isinstance(data, list) else []
        for m in members:
            m.setdefault("guild_id", guild_id)
        return [Member(m, client=self) for m in members]

    async def get_guild_member(self, guild_id: str, user_id: str) -> Member:
        """
        Get a specific member of a guild.

        Args:
            guild_id: The ID of the guild
            user_id: The ID of the user

        Returns:
            Member object
        """
        data = await self.http.get(f"guilds/{guild_id}/members/{user_id}")
        data.setdefault("guild_id", guild_id)
        return Member(data, client=self)

    async def get_guild_roles(self, guild_id: str) -> List[Role]:
        """
        Get all roles in a guild.

        Args:
            guild_id: The ID of the guild

        Returns:
            List of Role objects
        """
        data = await self.http.get(f"guilds/{guild_id}/roles")
        roles = data if isinstance(data, list) else []
        return [Role(r, client=self) for r in roles]

    async def kick_member(
        self,
        guild_id: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Kick a member from a guild.

        Args:
            guild_id: The ID of the guild
            user_id: The ID of the user to kick
            reason: Optional audit log reason

        Returns:
            True if successful
        """
        headers = {"X-Audit-Log-Reason": reason} if reason else {}
        await self.http.delete(
            f"guilds/{guild_id}/members/{user_id}",
            headers=headers,
        )
        return True

    async def ban_member(
        self,
        guild_id: str,
        user_id: str,
        reason: Optional[str] = None,
        delete_message_seconds: int = 0,
    ) -> bool:
        """
        Ban a user from a guild.

        Args:
            guild_id: The ID of the guild
            user_id: The ID of the user to ban
            reason: Optional audit log reason
            delete_message_seconds: How many seconds of recent messages to delete (0–604800)

        Returns:
            True if successful
        """
        headers = {"X-Audit-Log-Reason": reason} if reason else {}
        payload: Dict = {}
        if delete_message_seconds:
            payload["delete_message_seconds"] = delete_message_seconds
        await self.http.put(
            f"guilds/{guild_id}/bans/{user_id}",
            json=payload or None,
            headers=headers,
        )
        return True

    async def unban_member(self, guild_id: str, user_id: str) -> bool:
        """
        Unban a user from a guild.

        Args:
            guild_id: The ID of the guild
            user_id: The ID of the user to unban

        Returns:
            True if successful
        """
        await self.http.delete(f"guilds/{guild_id}/bans/{user_id}")
        return True

    # ------------------------------------------------------------------
    # Channel endpoints
    # ------------------------------------------------------------------

    async def get_channel(self, channel_id: str) -> Channel:
        """
        Get a channel by its ID.

        Args:
            channel_id: The ID of the channel

        Returns:
            Channel object
        """
        data = await self.http.get(f"channels/{channel_id}")
        return Channel(data, client=self)

    async def create_channel(
        self,
        guild_id: str,
        name: str,
        channel_type: int = 0,
        topic: Optional[str] = None,
        parent_id: Optional[str] = None,
        nsfw: bool = False,
    ) -> Channel:
        """
        Create a new channel in a guild.

        Args:
            guild_id: The ID of the guild
            name: The channel name
            channel_type: Channel type (0=text, 2=voice, 4=category)
            topic: Optional channel topic
            parent_id: Optional parent category ID
            nsfw: Whether the channel is NSFW

        Returns:
            The created Channel object
        """
        payload: Dict = {"name": name, "type": channel_type, "nsfw": nsfw}
        if topic:
            payload["topic"] = topic
        if parent_id:
            payload["parent_id"] = parent_id
        data = await self.http.post(f"guilds/{guild_id}/channels", json=payload)
        return Channel(data, client=self)

    async def delete_channel(self, channel_id: str) -> bool:
        """
        Delete a channel.

        Args:
            channel_id: The ID of the channel to delete

        Returns:
            True if successful
        """
        await self.http.delete(f"channels/{channel_id}")
        return True

    # ------------------------------------------------------------------
    # Message endpoints
    # ------------------------------------------------------------------

    async def get_channel_messages(self, channel_id: str, limit: int = 50) -> List[Message]:
        """
        Fetch recent messages from a channel.

        Args:
            channel_id: The ID of the channel
            limit: Maximum number of messages to return (default 50, max 100)

        Returns:
            List of Message objects (newest first)
        """
        data = await self.http.get(
            f"channels/{channel_id}/messages",
            params={"limit": limit},
        )
        messages = data if isinstance(data, list) else []
        return [Message(m, client=self) for m in messages]

    async def get_message(self, channel_id: str, message_id: str) -> Message:
        """
        Get a specific message from a channel.

        Args:
            channel_id: The ID of the channel
            message_id: The ID of the message

        Returns:
            Message object
        """
        data = await self.http.get(f"channels/{channel_id}/messages/{message_id}")
        return Message(data, client=self)

    async def send_message(self, channel_id: str, content: str) -> Message:
        """
        Send a message to a channel.

        Args:
            channel_id: The ID of the channel
            content: The message text

        Returns:
            The created Message object
        """
        data = await self.http.post(
            f"channels/{channel_id}/messages",
            json={"content": content},
        )
        msg = Message(data, client=self)
        await self.dispatch("on_message_create", msg)
        return msg

    async def edit_message(
        self, channel_id: str, message_id: str, content: str
    ) -> Message:
        """
        Edit a message.

        Args:
            channel_id: The ID of the channel
            message_id: The ID of the message to edit
            content: New message content

        Returns:
            The updated Message object
        """
        data = await self.http.patch(
            f"channels/{channel_id}/messages/{message_id}",
            json={"content": content},
        )
        return Message(data, client=self)

    async def delete_message(self, channel_id: str, message_id: str) -> bool:
        """
        Delete a message.

        Args:
            channel_id: The ID of the channel the message is in
            message_id: The ID of the message to delete

        Returns:
            True if successful
        """
        await self.http.delete(f"channels/{channel_id}/messages/{message_id}")
        return True

    # ------------------------------------------------------------------
    # Reaction endpoints
    # ------------------------------------------------------------------

    async def add_reaction(
        self, channel_id: str, message_id: str, emoji: str
    ) -> bool:
        """
        Add a reaction to a message.

        Args:
            channel_id: The ID of the channel
            message_id: The ID of the message
            emoji: The emoji string (e.g. '👍' or 'name:id' for custom emojis)

        Returns:
            True if successful
        """
        from urllib.parse import quote
        await self.http.put(
            f"channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}/@me"
        )
        return True

    async def remove_reaction(
        self,
        channel_id: str,
        message_id: str,
        emoji: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Remove a reaction from a message.

        Args:
            channel_id: The ID of the channel
            message_id: The ID of the message
            emoji: The emoji to remove
            user_id: The user whose reaction to remove (None = own reaction)

        Returns:
            True if successful
        """
        from urllib.parse import quote
        target = user_id if user_id else "@me"
        await self.http.delete(
            f"channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}/{target}"
        )
        return True

    # ------------------------------------------------------------------
    # Gateway
    # ------------------------------------------------------------------

    async def get_gateway_url(self) -> str:
        """
        Fetch the recommended WebSocket gateway URL from the API.

        Returns:
            wss:// URL string
        """
        data = await self.http.get("gateway/bot")
        return data["url"]

    def create_gateway_client(self, intents: int = 0) -> "GatewayClient":
        """
        Create a GatewayClient that shares this client's token.

        Call ``await client.get_gateway_url()`` first to get the URL,
        then pass it to the returned GatewayClient.

        Returns:
            A new GatewayClient instance
        """
        from .gateway import GatewayClient, Intents
        return GatewayClient(
            token=self.token,
            gateway_url="",  # set by the caller after get_gateway_url()
            intents=intents or Intents.DEFAULT,
        )
