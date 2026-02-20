"""
Example showing gateway event handling in fluxerpy3.

The GatewayClient maintains a real-time WebSocket connection to the Fluxer
gateway and fires events just like discord.py.
"""

import asyncio
import os
import fluxerpy3
from fluxerpy3 import Intents


BOT_TOKEN = os.environ.get("FLUXER_TOKEN", "your_bot_token_here")
BOT_PREFIX = "!"


async def on_ready(data: dict):
    """Fired once when the gateway handshake completes."""
    user = data.get("user", {})
    print(f"[READY] Logged in as {user.get('username')} (id={user.get('id')})")
    guilds = data.get("guilds", [])
    print(f"[READY] Visible guilds: {len(guilds)}")


async def on_message_create(data: dict):
    """Fired for every new message the bot can see."""
    content: str = data.get("content", "")
    author = data.get("author", {})
    channel_id: str = data.get("channel_id", "")

    # Ignore messages from bots
    if author.get("bot"):
        return

    print(f"[MESSAGE] {author.get('username')}: {content}")

    # Simple command handler
    if content.startswith(BOT_PREFIX):
        command = content[len(BOT_PREFIX):].strip().lower()

        if command == "ping":
            # Use the REST client to reply
            async with fluxerpy3.Client(token=BOT_TOKEN) as rest:
                await rest.send_message(channel_id, "Pong! 🏓")

        elif command == "info":
            guild_id = data.get("guild_id")
            if guild_id:
                async with fluxerpy3.Client(token=BOT_TOKEN) as rest:
                    guild = await rest.get_guild(guild_id)
                    await rest.send_message(
                        channel_id,
                        f"**{guild.name}** – ~{guild.member_count} members",
                    )


async def on_guild_member_add(data: dict):
    """Fired when a user joins a guild."""
    user = data.get("user", {})
    guild_id = data.get("guild_id", "")
    print(f"[MEMBER JOIN] {user.get('username')} joined guild {guild_id}")


async def main():
    # 1. Fetch the gateway URL via REST
    async with fluxerpy3.Client(token=BOT_TOKEN) as rest:
        gateway_url = await rest.get_gateway_url()
        print(f"Gateway URL: {gateway_url}")

    # 2. Create and configure the gateway client
    gw = fluxerpy3.GatewayClient(
        token=BOT_TOKEN,
        gateway_url=gateway_url,
        intents=Intents.DEFAULT,
    )

    # 3. Register event handlers
    gw.on("READY", on_ready)
    gw.on("MESSAGE_CREATE", on_message_create)
    gw.on("GUILD_MEMBER_ADD", on_guild_member_add)

    # 4. Connect – runs until interrupted
    print("Connecting to gateway...")
    await gw.connect()


if __name__ == "__main__":
    asyncio.run(main())
