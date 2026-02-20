"""
Advanced example showing error handling and best practices with fluxerpy3
"""

import asyncio
import logging
import os
from typing import List
from fluxerpy3 import (
    Client,
    Guild,
    Channel,
    Message,
    Member,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def retry_on_rate_limit(coro, max_retries: int = 3):
    """
    Retry a coroutine on rate limit errors.

    Args:
        coro: The coroutine to retry
        max_retries: Maximum number of retries

    Returns:
        The result of the coroutine
    """
    for attempt in range(max_retries):
        try:
            return await coro
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = e.retry_after or 60
            logger.warning(
                f"Rate limited, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(wait_time)


async def scan_channel_messages(
    client: Client, channel: Channel, keyword: str
) -> List[Message]:
    """
    Fetch messages from a channel and filter by a keyword.

    Args:
        client: The Fluxer client
        channel: The channel to scan
        keyword: Filter keyword

    Returns:
        List of matching Message objects
    """
    try:
        messages = await retry_on_rate_limit(
            client.get_channel_messages(channel.id, limit=100)
        )
        matches = [m for m in messages if keyword.lower() in m.content.lower()]
        logger.info(
            f"Found {len(matches)} messages containing '{keyword}' in #{channel.name}"
        )
        return matches
    except APIError as e:
        logger.error(f"API error while scanning #{channel.name}: {e}")
        return []


async def display_guild_info(client: Client, guild: Guild):
    """
    Print detailed information about a guild.

    Args:
        client: The Fluxer client
        guild: The guild to inspect
    """
    try:
        channels = await retry_on_rate_limit(client.get_guild_channels(guild.id))
        roles = await retry_on_rate_limit(client.get_guild_roles(guild.id))

        text_channels = [c for c in channels if c.is_text_channel]
        voice_channels = [c for c in channels if c.is_voice_channel]
        categories = [c for c in channels if c.is_category]

        logger.info(
            f"""
Guild: {guild.name} (id={guild.id})
  Members    : ~{guild.member_count}
  Description: {guild.description or 'none'}
  Locale     : {guild.preferred_locale}
  Text channels  : {len(text_channels)}
  Voice channels : {len(voice_channels)}
  Categories     : {len(categories)}
  Roles          : {len(roles)}
"""
        )

        logger.info("Roles:")
        for role in sorted(roles, key=lambda r: r.position, reverse=True):
            logger.info(f"  [{role.position:>3}] {role.name}")

    except NotFoundError:
        logger.error(f"Guild {guild.id} not found")
    except Exception as e:
        logger.error(f"Error fetching guild info: {e}")


async def main():
    """Main function demonstrating advanced usage"""

    # Use an environment variable instead of hardcoding the token
    token = os.environ.get("FLUXER_TOKEN", "your_bot_token_here")

    try:
        async with Client(token=token) as client:
            try:
                me = await client.get_me()
                logger.info(f"Logged in as @{me.username} (bot={me.bot})")
            except AuthenticationError:
                logger.error("Authentication failed. Check your bot token.")
                return

            guilds = await client.get_guilds()
            logger.info(f"Bot is in {len(guilds)} guild(s)")

            for guild in guilds:
                await display_guild_info(client, guild)

                # Scan the first text channel for a keyword
                channels = await client.get_guild_channels(guild.id)
                text_channels = [c for c in channels if c.is_text_channel]
                if text_channels:
                    matches = await scan_channel_messages(
                        client, text_channels[0], keyword="hello"
                    )
                    if matches:
                        logger.info(
                            f"Sample match: [{matches[0].author}] {matches[0].content}"
                        )

                # Small delay between guilds
                await asyncio.sleep(0.5)

            logger.info("Session completed successfully!")

    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
