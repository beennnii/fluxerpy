# fluxerpy3

A Python wrapper for the Fluxer API, inspired by discord.py's design.
Fluxer is a Discord-like platform with guilds, channels, and messages.

## Features

- **Async/await support** – Built with modern Python async/await syntax
- **Easy to use** – Simple and intuitive API similar to discord.py
- **Type hints** – Full type hint support for better IDE integration
- **Gateway support** – Real-time WebSocket events (MESSAGE_CREATE, GUILD_MEMBER_ADD, …)
- **Rich models** – `Guild`, `Channel`, `Member`, `Role`, `Message`, `Reaction`
- **Error handling** – Custom exceptions for different error scenarios

## Installation

```bash
pip install fluxerpy3
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

```python
import asyncio
import fluxerpy3

async def main():
    async with fluxerpy3.Client(token="your_bot_token") as client:
        # Get the bot user
        me = await client.get_me()
        print(f"Logged in as: {me.username}")

        # List all guilds (servers)
        guilds = await client.get_guilds()
        for guild in guilds:
            print(f"  {guild.name} – {guild.member_count} members")

        # Send a message
        await client.send_message("channel_id_here", "Hello from fluxerpy3! 🚀")

asyncio.run(main())
```

## Usage Examples

### Guild & Channel Operations

```python
# Get a specific guild
guild = await client.get_guild("guild_id")

# Get all channels in a guild
channels = await client.get_guild_channels(guild.id)
text_channels = [c for c in channels if c.is_text_channel]

# Get recent messages from a channel
messages = await client.get_channel_messages("channel_id", limit=50)
for msg in messages:
    print(f"{msg.author}: {msg.content}")

# Create a new channel
new_channel = await client.create_channel(guild.id, "bot-log", topic="Bot activity log")
```

### Message Operations

```python
# Send a message
msg = await client.send_message("channel_id", "Hello!")

# Edit a message
edited = await client.edit_message("channel_id", msg.id, "Hello (edited)!")

# Delete a message
await client.delete_message("channel_id", msg.id)

# Convenience methods on Message objects
await msg.reply("Replying in the same channel")
await msg.edit("Updated content")
await msg.delete()
```

### Reaction Operations

```python
# Add a reaction
await client.add_reaction("channel_id", msg.id, "👍")

# Remove own reaction
await client.remove_reaction("channel_id", msg.id, "👍")

# Remove another user's reaction
await client.remove_reaction("channel_id", msg.id, "👍", user_id="user_id")

# Via Message object
await msg.add_reaction("🔥")
```

### Member & Moderation Operations

```python
# List members
members = await client.get_guild_members(guild.id, limit=100)

# Get a specific member
member = await client.get_guild_member(guild.id, "user_id")
print(f"{member.display_name} – roles: {member.roles}")

# Kick / ban / unban
await client.kick_member(guild.id, "user_id", reason="Rule violation")
await client.ban_member(guild.id, "user_id", reason="Spam", delete_message_seconds=86400)
await client.unban_member(guild.id, "user_id")

# Convenience methods on Member
await member.kick(reason="Rule violation")
await member.ban(reason="Spam")
```

### Gateway (Real-time Events)

```python
import asyncio
import fluxerpy3
from fluxerpy3 import Intents

async def on_message_create(data):
    author = data.get("author", {})
    print(f"{author.get('username')}: {data.get('content')}")

async def main():
    async with fluxerpy3.Client(token="your_bot_token") as rest:
        gateway_url = await rest.get_gateway_url()

    gw = fluxerpy3.GatewayClient(
        token="your_bot_token",
        gateway_url=gateway_url,
        intents=Intents.DEFAULT,
    )
    gw.on("MESSAGE_CREATE", on_message_create)
    await gw.connect()

asyncio.run(main())
```

## API Reference

### Client

**User methods:**
- `get_me()` – Get the authenticated bot user
- `get_user(user_id)` – Get a user by ID
- `get_user_by_username(username)` – Look up a user by username

**Guild methods:**
- `get_guilds()` – List all guilds the bot is in
- `get_guild(guild_id)` – Get a specific guild
- `get_guild_channels(guild_id)` – List channels in a guild
- `get_guild_members(guild_id, limit)` – List members
- `get_guild_member(guild_id, user_id)` – Get a specific member
- `get_guild_roles(guild_id)` – List roles
- `kick_member(guild_id, user_id, reason)` – Kick a member
- `ban_member(guild_id, user_id, reason, delete_message_seconds)` – Ban a user
- `unban_member(guild_id, user_id)` – Unban a user

**Channel methods:**
- `get_channel(channel_id)` – Get a channel
- `create_channel(guild_id, name, channel_type, topic, parent_id, nsfw)` – Create a channel
- `delete_channel(channel_id)` – Delete a channel

**Message methods:**
- `get_channel_messages(channel_id, limit)` – Fetch messages
- `get_message(channel_id, message_id)` – Fetch one message
- `send_message(channel_id, content)` – Send a message
- `edit_message(channel_id, message_id, content)` – Edit a message
- `delete_message(channel_id, message_id)` – Delete a message

**Reaction methods:**
- `add_reaction(channel_id, message_id, emoji)` – Add a reaction
- `remove_reaction(channel_id, message_id, emoji, user_id)` – Remove a reaction

**Gateway:**
- `get_gateway_url()` – Fetch WSS gateway URL
- `create_gateway_client(intents)` – Create a `GatewayClient`

### Models

| Model | Key properties |
|-------|----------------|
| `User` | `username`, `discriminator`, `display_name`, `avatar_url`, `bot`, `status` |
| `Guild` | `name`, `icon_url`, `owner_id`, `member_count`, `description` |
| `Channel` | `name`, `type`, `guild_id`, `topic`, `is_text_channel`, `is_voice_channel`, `is_category` |
| `Member` | `user`, `nick`, `display_name`, `guild_id`, `roles`, `joined_at` |
| `Role` | `name`, `color`, `permissions`, `position`, `mentionable`, `hoist` |
| `Message` | `content`, `channel_id`, `guild_id`, `author`, `member`, `created_at`, `reactions`, `attachments` |
| `Reaction` | `emoji`, `count`, `me` |

## Error Handling

```python
from fluxerpy3 import AuthenticationError, NotFoundError, RateLimitError, APIError

try:
    async with fluxerpy3.Client(token="invalid") as client:
        await client.get_me()
except AuthenticationError:
    print("Invalid bot token")
except NotFoundError:
    print("Resource not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
```

## License

MIT License – see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
