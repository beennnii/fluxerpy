# fluxerpy

A Python wrapper for the Fluxer.web API, inspired by discord.py's design.

## Features

- **Async/await support** - Built with modern Python async/await syntax
- **Easy to use** - Simple and intuitive API similar to discord.py
- **Type hints** - Full type hint support for better IDE integration
- **Event system** - Register event handlers for various actions
- **Comprehensive models** - User, Post, and Comment models with rich properties
- **Error handling** - Custom exceptions for different error scenarios

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

```python
import asyncio
import fluxerpy

async def main():
    # Create a client with your authentication token
    client = fluxerpy.Client(token="your_token_here")
    
    async with client:
        # Get current user
        me = await client.get_me()
        print(f"Logged in as: {me.username}")
        
        # Get feed
        posts = await client.get_feed(limit=10)
        for post in posts:
            print(f"{post.author.username}: {post.content}")
        
        # Create a post
        new_post = await client.create_post("Hello from fluxerpy! 🚀")
        print(f"Created post: {new_post.id}")

asyncio.run(main())
```

## Usage Examples

### User Operations

```python
# Get a user by username
user = await client.get_user_by_username("example_user")

# Follow/unfollow a user
await user.follow()
await user.unfollow()

# Get user's posts
posts = await user.get_posts(limit=20)
```

### Post Operations

```python
# Create a post
post = await client.create_post("Hello world!")

# Like/unlike a post
await post.like()
await post.unlike()

# Repost a post
await post.repost()

# Delete a post
await post.delete()

# Get comments
comments = await post.get_comments()
```

### Comment Operations

```python
# Comment on a post
comment = await post.comment("Great post!")

# Like a comment
await comment.like()

# Delete a comment
await comment.delete()
```

### Event Handling

```python
client = fluxerpy.Client(token="your_token_here")

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
import fluxerpy
from fluxerpy import AuthenticationError, NotFoundError, RateLimitError

try:
    async with fluxerpy.Client(token="invalid_token") as client:
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
