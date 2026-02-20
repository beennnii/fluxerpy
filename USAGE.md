# fluxerpy3 – Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Client Basics](#client-basics)
4. [User Operations](#user-operations)
5. [Guild Operations](#guild-operations)
6. [Channel Operations](#channel-operations)
7. [Message Operations](#message-operations)
8. [Reaction Operations](#reaction-operations)
9. [Member & Moderation](#member--moderation)
10. [Gateway (Real-time Events)](#gateway-real-time-events)
11. [Error Handling](#error-handling)
12. [Best Practices](#best-practices)

---

## Installation

```bash
pip install -r requirements.txt
# or in development mode:
pip install -e .
```

---

## Authentication

fluxerpy3 authenticates with a **bot token**. Never use a user account token.

```python
import fluxerpy3

client = fluxerpy3.Client(token="your_bot_token_here")
```

Store tokens in environment variables, not in source code:

```python
import os
client = fluxerpy3.Client(token=os.environ["FLUXER_TOKEN"])
```

---

## Client Basics

### Context manager (recommended)

```python
import asyncio
import fluxerpy3

async def main():
    async with fluxerpy3.Client(token="your_bot_token") as client:
        me = await client.get_me()
        print(f"Logged in as: {me.username} (bot={me.bot})")

asyncio.run(main())
```

### Manual lifecycle

```python
client = fluxerpy3.Client(token="your_bot_token")
await client.start()
# ... use the client ...
await client.close()
```

---

## User Operations

### Get the bot user

```python
me = await client.get_me()
print(me.username, me.id, me.bot)
```

### Look up any user

```python
# by ID
user = await client.get_user("user_id_here")
print(user.display_name, user.avatar_url)
```

---

## Guild Operations

### List all guilds

```python
guilds = await client.get_guilds()
for guild in guilds:
    print(f"{guild.name}  ({guild.member_count} members)")
```

### Get a specific guild

```python
guild = await client.get_guild("guild_id")
print(guild.description, guild.preferred_locale)
```

### List roles

```python
roles = await client.get_guild_roles(guild.id)
for role in sorted(roles, key=lambda r: r.position, reverse=True):
    print(f"[{role.position}] @{role.name}  color={hex(role.color)}")
```

---

## Channel Operations

### List channels

```python
channels = await client.get_guild_channels(guild.id)
for ch in channels:
    if ch.is_text_channel:
        print(f"#{ch.name}  topic={ch.topic}")
    elif ch.is_voice_channel:
        print(f"🔊 {ch.name}")
    elif ch.is_category:
        print(f"📁 {ch.name}")
```

### Get a single channel

```python
channel = await client.get_channel("channel_id")
```

### Create / delete a channel

```python
new_ch = await client.create_channel(
    guild.id,
    name="bot-log",
    channel_type=0,          # 0=text, 2=voice, 4=category
    topic="Bot activity log",
)

await client.delete_channel(new_ch.id)
# or via the object:
await new_ch.delete()
```

---

## Message Operations

### Fetch messages

```python
messages = await client.get_channel_messages("channel_id", limit=50)
for msg in messages:
    ts = msg.created_at.strftime("%H:%M") if msg.created_at else "?"
    print(f"[{ts}] {msg.author}: {msg.content}")
```

### Send a message

```python
msg = await client.send_message("channel_id", "Hello! 👋")
```

### Edit a message

```python
edited = await client.edit_message("channel_id", msg.id, "Hello (edited)!")
# or:
edited = await msg.edit("Hello (edited)!")
```

### Delete a message

```python
await client.delete_message("channel_id", msg.id)
# or:
await msg.delete()
```

### Reply in the same channel

```python
await msg.reply("I saw your message!")
```

---

## Reaction Operations

```python
# Add a reaction (Unicode or custom "name:id")
await client.add_reaction("channel_id", msg.id, "👍")
await msg.add_reaction("🔥")

# Remove own reaction
await client.remove_reaction("channel_id", msg.id, "👍")
await msg.remove_reaction("👍")

# Remove another user's reaction
await client.remove_reaction("channel_id", msg.id, "👍", user_id="user_id")

# Read reactions on a message
for reaction in msg.reactions:
    print(f"{reaction.emoji}  ×{reaction.count}  (me={reaction.me})")
```

---

## Member & Moderation

### List members

```python
members = await client.get_guild_members(guild.id, limit=100)
for m in members:
    print(f"{m.display_name}  joined={m.joined_at}")
```

### Get a specific member

```python
member = await client.get_guild_member(guild.id, "user_id")
print(member.nick, member.roles)
```

### Kick / ban / unban

```python
# Kick
await client.kick_member(guild.id, "user_id", reason="Rule violation")
await member.kick(reason="Rule violation")

# Ban (with optional message cleanup: 0–604800 seconds)
await client.ban_member(guild.id, "user_id", reason="Spam", delete_message_seconds=86400)
await member.ban(reason="Spam", delete_message_seconds=86400)

# Unban
await client.unban_member(guild.id, "user_id")
```

---

## Gateway (Real-time Events)

The `GatewayClient` maintains a persistent WebSocket connection and fires
events just like discord.py's event system.

### Full example

```python
import asyncio
import os
import fluxerpy3
from fluxerpy3 import Intents

TOKEN = os.environ["FLUXER_TOKEN"]

async def on_ready(data):
    user = data.get("user", {})
    print(f"[READY] {user.get('username')}")

async def on_message_create(data):
    if data.get("author", {}).get("bot"):
        return  # ignore other bots
    content = data.get("content", "")
    print(f"[MSG] {data['author']['username']}: {content}")

async def on_guild_member_add(data):
    user = data.get("user", {})
    print(f"[JOIN] {user.get('username')} joined {data.get('guild_id')}")

async def main():
    async with fluxerpy3.Client(token=TOKEN) as rest:
        gateway_url = await rest.get_gateway_url()

    gw = fluxerpy3.GatewayClient(
        token=TOKEN,
        gateway_url=gateway_url,
        intents=Intents.DEFAULT,
    )
    gw.on("READY",            on_ready)
    gw.on("MESSAGE_CREATE",   on_message_create)
    gw.on("GUILD_MEMBER_ADD", on_guild_member_add)

    print("Connecting to gateway...")
    await gw.connect()   # runs until interrupted

asyncio.run(main())
```

### Available gateway events

| Event | When fired |
|-------|------------|
| `READY` | Successful login |
| `MESSAGE_CREATE` | New message in a visible channel |
| `MESSAGE_UPDATE` | Message edited |
| `MESSAGE_DELETE` | Message deleted |
| `GUILD_CREATE` | Bot joins a guild / guild becomes available |
| `GUILD_UPDATE` | Guild settings changed |
| `GUILD_DELETE` | Bot removed from a guild |
| `GUILD_MEMBER_ADD` | User joins a guild |
| `GUILD_MEMBER_UPDATE` | Member role/nick changed |
| `GUILD_MEMBER_REMOVE` | User leaves / is removed from a guild |
| `CHANNEL_CREATE` | Channel created |
| `CHANNEL_UPDATE` | Channel edited |
| `CHANNEL_DELETE` | Channel deleted |

---

## Error Handling

```python
from fluxerpy3 import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError,
)

try:
    async with fluxerpy3.Client(token=token) as client:
        member = await client.get_guild_member(guild_id, user_id)
except AuthenticationError:
    print("Invalid bot token")
except NotFoundError:
    print("Guild or member not found")
except RateLimitError as e:
    print(f"Rate limited – retry after {e.retry_after}s")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
```

---

## Best Practices

### 1. Always use the context manager

```python
async with fluxerpy3.Client(token=token) as client:
    ...
```

### 2. Retry on rate limits

```python
async def with_retry(coro, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await coro
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(e.retry_after or 60)
```

### 3. Concurrent requests

```python
import asyncio

# Fetch multiple guilds concurrently
guilds = await asyncio.gather(*[client.get_guild(gid) for gid in guild_ids])
```

### 4. Use a REST client inside gateway handlers

Gateway handlers only receive raw `dict` payloads. Use the REST `Client`
for follow-up API calls:

```python
async def on_message_create(data):
    if data.get("content") == "!info":
        channel_id = data["channel_id"]
        async with fluxerpy3.Client(token=TOKEN) as rest:
            await rest.send_message(channel_id, "pong!")
```

### 5. Log errors properly

```python
import logging
logger = logging.getLogger(__name__)

try:
    msg = await client.send_message(channel_id, content)
except Exception as e:
    logger.error("Failed to send message: %s", e, exc_info=True)
```

