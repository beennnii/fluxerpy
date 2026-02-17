# Fluxerpy - Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Client Basics](#client-basics)
4. [User Operations](#user-operations)
5. [Post Operations](#post-operations)
6. [Comment Operations](#comment-operations)
7. [Event System](#event-system)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

## Installation

Install the package and its dependencies:

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Authentication

To use the Fluxer API, you need an authentication token. Create a client with your token:

```python
import fluxerpy

client = fluxerpy.Client(token="your_token_here")
```

## Client Basics

### Using the Client

The client should be properly initialized and closed. Use it as a context manager:

```python
import asyncio
import fluxerpy

async def main():
    async with fluxerpy.Client(token="your_token") as client:
        me = await client.get_me()
        print(f"Logged in as: {me.username}")

asyncio.run(main())
```

Or manually manage the lifecycle:

```python
client = fluxerpy.Client(token="your_token")
await client.start()
# ... use the client
await client.close()
```

### Get Current User

```python
me = await client.get_me()
print(f"Username: {me.username}")
print(f"Display Name: {me.display_name}")
print(f"Followers: {me.follower_count}")
```

## User Operations

### Get User by ID

```python
user = await client.get_user("user_id_here")
```

### Get User by Username

```python
user = await client.get_user_by_username("example_user")
print(f"User: {user.username}")
print(f"Bio: {user.bio}")
```

### Follow/Unfollow Users

```python
# Follow a user
await client.follow_user(user.id)
# or
await user.follow()

# Unfollow a user
await client.unfollow_user(user.id)
# or
await user.unfollow()
```

### Get User's Posts

```python
posts = await client.get_user_posts(user.id, limit=20)
# or
posts = await user.get_posts(limit=20)

for post in posts:
    print(f"{post.content}")
```

## Post Operations

### Get Feed

```python
posts = await client.get_feed(limit=20)
for post in posts:
    if post.author:
        print(f"@{post.author.username}: {post.content}")
```

### Get a Specific Post

```python
post = await client.get_post("post_id_here")
```

### Create a Post

```python
# Simple text post
post = await client.create_post("Hello world!")

# Post with media
post = await client.create_post(
    "Check out this image!",
    media_urls=["https://example.com/image.jpg"]
)
```

### Like/Unlike Posts

```python
# Like a post
await client.like_post(post.id)
# or
await post.like()

# Unlike a post
await client.unlike_post(post.id)
# or
await post.unlike()
```

### Repost

```python
repost = await client.repost(post.id)
# or
repost = await post.repost()
```

### Delete a Post

```python
await client.delete_post(post.id)
# or
await post.delete()
```

## Comment Operations

### Get Comments on a Post

```python
comments = await client.get_post_comments(post.id, limit=20)
# or
comments = await post.get_comments(limit=20)

for comment in comments:
    if comment.author:
        print(f"{comment.author.username}: {comment.content}")
```

### Create a Comment

```python
comment = await client.create_comment(post.id, "Great post!")
# or
comment = await post.comment("Great post!")
```

### Like/Unlike Comments

```python
# Like a comment
await client.like_comment(comment.id)
# or
await comment.like()

# Unlike a comment
await client.unlike_comment(comment.id)
# or
await comment.unlike()
```

### Delete a Comment

```python
await client.delete_comment(comment.id)
# or
await comment.delete()
```

## Event System

The event system allows you to respond to actions:

```python
client = fluxerpy.Client(token="your_token")

@client.event
async def on_post_created(post):
    print(f"New post: {post.content}")
    # Automatically like posts you create
    await post.like()

async def main():
    async with client:
        # This will trigger the on_post_created event
        await client.create_post("Test post")

asyncio.run(main())
```

## Error Handling

Handle different types of errors:

```python
from fluxerpy import (
    Client,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError
)

async def main():
    try:
        async with Client(token="your_token") as client:
            user = await client.get_user("invalid_id")
    except AuthenticationError:
        print("Authentication failed - check your token")
    except NotFoundError:
        print("User not found")
    except RateLimitError as e:
        print(f"Rate limited! Retry after {e.retry_after} seconds")
    except APIError as e:
        print(f"API error: {e}, Status: {e.status_code}")
```

## Best Practices

### 1. Use Context Managers

Always use the client as a context manager to ensure proper cleanup:

```python
async with fluxerpy.Client(token="your_token") as client:
    # your code here
```

### 2. Handle Rate Limits

Implement retry logic for rate limits:

```python
import asyncio
from fluxerpy import RateLimitError

async def with_retry(coro, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await coro
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = e.retry_after or 60
            print(f"Rate limited, waiting {wait_time}s...")
            await asyncio.sleep(wait_time)
```

### 3. Batch Operations

When performing multiple operations, batch them efficiently:

```python
# Get multiple users concurrently
users = await asyncio.gather(*[
    client.get_user(user_id)
    for user_id in user_ids
])
```

### 4. Use Type Hints

Enable better IDE support with type hints:

```python
from typing import List
from fluxerpy import Client, Post

async def get_popular_posts(client: Client, limit: int = 10) -> List[Post]:
    posts = await client.get_feed(limit=limit)
    return sorted(posts, key=lambda p: p.like_count, reverse=True)
```

### 5. Log Errors

Implement proper logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    user = await client.get_user(user_id)
except Exception as e:
    logger.error(f"Failed to get user {user_id}: {e}")
```

## Complete Example

Here's a complete example that demonstrates various features:

```python
import asyncio
import logging
from fluxerpy import Client, RateLimitError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    async with Client(token="your_token") as client:
        # Get current user
        me = await client.get_me()
        logger.info(f"Logged in as @{me.username}")
        
        # Get feed and interact
        posts = await client.get_feed(limit=10)
        
        for post in posts:
            try:
                # Like posts with more than 5 likes
                if post.like_count > 5:
                    await post.like()
                    logger.info(f"Liked post by @{post.author.username}")
                
                # Comment on popular posts
                if post.like_count > 20:
                    await post.comment("Great content! 🔥")
                    logger.info(f"Commented on post {post.id}")
                    
            except RateLimitError as e:
                logger.warning(f"Rate limited, waiting {e.retry_after}s")
                await asyncio.sleep(e.retry_after or 60)
            except Exception as e:
                logger.error(f"Error processing post {post.id}: {e}")
        
        # Create a summary post
        summary = f"Just interacted with {len(posts)} posts! 🚀"
        await client.create_post(summary)

if __name__ == "__main__":
    asyncio.run(main())
```
