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

Contributions are welcome! Please open a Pull Request.


### Event Handling

```python
client = fluxerpy3.Client(token="your_token_here")

@client.event
async def on_post_created(post):
    print(f"New post created: {post.content}")

async def main():
    async with client:
        # Creating a post will trigger the event
        await client.create_post("Test post")

asyncio.run(main())
```

## API Reference

### Client

The main client class for interacting with the Fluxer API.

**Methods:**
- `get_me()` - Get the currently authenticated user
- `get_user(user_id)` - Get a user by ID
- `get_user_by_username(username)` - Get a user by username
- `follow_user(user_id)` - Follow a user
- `unfollow_user(user_id)` - Unfollow a user
- `get_feed(limit)` - Get the user's feed
- `get_post(post_id)` - Get a post by ID
- `create_post(content, media_urls)` - Create a new post
- `delete_post(post_id)` - Delete a post
- `like_post(post_id)` - Like a post
- `unlike_post(post_id)` - Unlike a post
- `repost(post_id)` - Repost a post
- `get_post_comments(post_id, limit)` - Get comments on a post
- `create_comment(post_id, content)` - Create a comment
- `delete_comment(comment_id)` - Delete a comment
- `like_comment(comment_id)` - Like a comment
- `unlike_comment(comment_id)` - Unlike a comment

### Models

#### User

Represents a Fluxer user.

**Properties:**
- `id` - User ID
- `username` - Username
- `display_name` - Display name
- `bio` - User bio
- `avatar_url` - Avatar URL
- `follower_count` - Number of followers
- `following_count` - Number of users being followed
- `post_count` - Number of posts
- `created_at` - Account creation date

**Methods:**
- `follow()` - Follow this user
- `unfollow()` - Unfollow this user
- `get_posts(limit)` - Get posts by this user

#### Post

Represents a Fluxer post.

**Properties:**
- `id` - Post ID
- `content` - Post content
- `author_id` - Author's user ID
- `author` - Author user object
- `like_count` - Number of likes
- `comment_count` - Number of comments
- `repost_count` - Number of reposts
- `created_at` - Post creation date
- `media_urls` - List of media URLs

**Methods:**
- `like()` - Like this post
- `unlike()` - Unlike this post
- `repost()` - Repost this post
- `delete()` - Delete this post
- `get_comments(limit)` - Get comments
- `comment(content)` - Add a comment

#### Comment

Represents a comment on a post.

**Properties:**
- `id` - Comment ID
- `content` - Comment content
- `author_id` - Author's user ID
- `author` - Author user object
- `post_id` - ID of the post
- `like_count` - Number of likes
- `created_at` - Comment creation date

**Methods:**
- `like()` - Like this comment
- `unlike()` - Unlike this comment
- `delete()` - Delete this comment

## Error Handling

```python
import fluxerpy3
from fluxerpy3 import AuthenticationError, NotFoundError, RateLimitError

try:
    async with fluxerpy3.Client(token="invalid_token") as client:
        await client.get_me()
except AuthenticationError:
    print("Invalid authentication token")
except NotFoundError:
    print("Resource not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
