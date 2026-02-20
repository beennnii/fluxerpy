"""
Basic example of using fluxerpy3
"""

import asyncio
import fluxerpy3


async def main():
    # Create a client with your bot token
    client = fluxerpy3.Client(token="your_bot_token_here")

    try:
        await client.start()

        # Get the bot user
        me = await client.get_me()
        print(f"Logged in as: {me.username} (bot={me.bot})")

        # List all guilds (servers) the bot is in
        print("\nGuilds:")
        guilds = await client.get_guilds()
        for guild in guilds:
            print(f"  - {guild.name} (id={guild.id}, members={guild.member_count})")

        if not guilds:
            print("  (bot is not in any guild)")
            return

        # Inspect the first guild
        guild = guilds[0]
        print(f"\nChannels in '{guild.name}':")
        channels = await client.get_guild_channels(guild.id)
        for channel in channels:
            if channel.is_text_channel:
                topic = f" – {channel.topic}" if channel.topic else ""
                print(f"  #{channel.name}{topic}")

        # Find the first text channel and fetch recent messages
        text_channels = [c for c in channels if c.is_text_channel]
        if text_channels:
            channel = text_channels[0]
            print(f"\nLast 5 messages in #{channel.name}:")
            messages = await client.get_channel_messages(channel.id, limit=5)
            for msg in messages:
                author = str(msg.author) if msg.author else "unknown"
                print(f"  [{author}] {msg.content}")

            # Send a message
            sent = await client.send_message(channel.id, "Hello from fluxerpy3! 🚀")
            print(f"\nSent message: {sent.id}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
