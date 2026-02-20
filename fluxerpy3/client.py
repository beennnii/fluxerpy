"""
Main client for Fluxer API
"""

from typing import Optional, List, Dict, Callable
from .http import HTTPClient
from .models import User, Post, Comment, Message


class Client:
    """
    Main client for interacting with the Fluxer API.
    Similar to discord.py's Client class.
    
    Example:
        ```python
        import fluxerpy3
        import asyncio
        
        client = fluxerpy3.Client(token="your_token_here")
        
        async def main():
            await client.start()
            
            # Get current user
            me = await client.get_me()
            print(f"Logged in as: {me.username}")
            
            # Get feed
            posts = await client.get_feed()
            for post in posts:
                print(f"{post.author.username}: {post.content}")
            
            await client.close()
        
        asyncio.run(main())
        ```
    """
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.fluxer.app/v1"):
        """
        Initialize the Fluxer client
        
        Args:
            token: Authentication token for the Fluxer API
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
        
    def event(self, func: Callable):
        """
        Decorator to register event handlers
        
        Example:
            ```python
            @client.event
            async def on_post_created(post):
                print(f"New post: {post.content}")
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
                
    # User endpoints
    
    async def get_me(self) -> User:
        """
        Get the currently authenticated user
        
        Returns:
            User object representing the authenticated user
        """
        data = await self.http.get("users/@me")
        return User(data, client=self)
        
    async def get_user(self, user_id: str) -> User:
        """
        Get a user by ID
        
        Args:
            user_id: The ID of the user to fetch
            
        Returns:
            User object
        """
        data = await self.http.get(f"users/{user_id}")
        return User(data, client=self)
        
    async def get_user_by_username(self, username: str) -> User:
        """
        Get a user by username
        
        Args:
            username: The username to search for
            
        Returns:
            User object
        """
        data = await self.http.get(f"users/username/{username}")
        return User(data, client=self)
        
    async def follow_user(self, user_id: str) -> bool:
        """
        Follow a user
        
        Args:
            user_id: The ID of the user to follow
            
        Returns:
            True if successful
        """
        await self.http.post(f"users/{user_id}/follow")
        return True
        
    async def unfollow_user(self, user_id: str) -> bool:
        """
        Unfollow a user
        
        Args:
            user_id: The ID of the user to unfollow
            
        Returns:
            True if successful
        """
        await self.http.delete(f"users/{user_id}/follow")
        return True
        
    async def get_user_posts(self, user_id: str, limit: int = 20) -> List[Post]:
        """
        Get posts by a specific user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of posts to return
            
        Returns:
            List of Post objects
        """
        data = await self.http.get(f"users/{user_id}/posts", params={"limit": limit})
        return [Post(post_data, client=self) for post_data in data.get("posts", [])]
        
    # Post endpoints
    
    async def get_feed(self, limit: int = 20) -> List[Post]:
        """
        Get the user's feed
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of Post objects
        """
        data = await self.http.get("feed", params={"limit": limit})
        return [Post(post_data, client=self) for post_data in data.get("posts", [])]
        
    async def get_post(self, post_id: str) -> Post:
        """
        Get a post by ID
        
        Args:
            post_id: The ID of the post to fetch
            
        Returns:
            Post object
        """
        data = await self.http.get(f"posts/{post_id}")
        return Post(data, client=self)
        
    async def create_post(self, content: str, media_urls: Optional[List[str]] = None) -> Post:
        """
        Create a new post
        
        Args:
            content: The post content/text
            media_urls: Optional list of media URLs to attach
            
        Returns:
            The created Post object
        """
        payload = {"content": content}
        if media_urls:
            payload["mediaUrls"] = media_urls
            
        data = await self.http.post("posts", json=payload)
        post = Post(data, client=self)
        await self.dispatch("on_post_created", post)
        return post
        
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post
        
        Args:
            post_id: The ID of the post to delete
            
        Returns:
            True if successful
        """
        await self.http.delete(f"posts/{post_id}")
        return True
        
    async def like_post(self, post_id: str) -> bool:
        """
        Like a post
        
        Args:
            post_id: The ID of the post to like
            
        Returns:
            True if successful
        """
        await self.http.post(f"posts/{post_id}/like")
        return True
        
    async def unlike_post(self, post_id: str) -> bool:
        """
        Unlike a post
        
        Args:
            post_id: The ID of the post to unlike
            
        Returns:
            True if successful
        """
        await self.http.delete(f"posts/{post_id}/like")
        return True
        
    async def repost(self, post_id: str) -> Post:
        """
        Repost a post
        
        Args:
            post_id: The ID of the post to repost
            
        Returns:
            The repost as a Post object
        """
        data = await self.http.post(f"posts/{post_id}/repost")
        return Post(data, client=self)
        
    # Comment endpoints
    
    async def get_post_comments(self, post_id: str, limit: int = 20) -> List[Comment]:
        """
        Get comments on a post
        
        Args:
            post_id: The ID of the post
            limit: Maximum number of comments to return
            
        Returns:
            List of Comment objects
        """
        data = await self.http.get(f"posts/{post_id}/comments", params={"limit": limit})
        return [Comment(comment_data, client=self) for comment_data in data.get("comments", [])]
        
    async def create_comment(self, post_id: str, content: str) -> Comment:
        """
        Create a comment on a post
        
        Args:
            post_id: The ID of the post to comment on
            content: The comment content/text
            
        Returns:
            The created Comment object
        """
        payload = {"content": content}
        data = await self.http.post(f"posts/{post_id}/comments", json=payload)
        return Comment(data, client=self)
        
    async def delete_comment(self, comment_id: str) -> bool:
        """
        Delete a comment
        
        Args:
            comment_id: The ID of the comment to delete
            
        Returns:
            True if successful
        """
        await self.http.delete(f"comments/{comment_id}")
        return True
        
    async def like_comment(self, comment_id: str) -> bool:
        """
        Like a comment
        
        Args:
            comment_id: The ID of the comment to like
            
        Returns:
            True if successful
        """
        await self.http.post(f"comments/{comment_id}/like")
        return True
        
    async def unlike_comment(self, comment_id: str) -> bool:
        """
        Unlike a comment
        
        Args:
            comment_id: The ID of the comment to unlike
            
        Returns:
            True if successful
        """
        await self.http.delete(f"comments/{comment_id}/like")
        return True

    # Guild endpoints

    async def get_guilds(self) -> List[Dict]:
        """
        Get all guilds the authenticated user/bot is a member of

        Returns:
            List of guild data dicts
        """
        data = await self.http.get("users/@me/guilds")
        return data if isinstance(data, list) else []

    async def get_guild_channels(self, guild_id: str) -> List[Dict]:
        """
        Get all channels in a guild

        Args:
            guild_id: The ID of the guild

        Returns:
            List of channel data dicts
        """
        data = await self.http.get(f"guilds/{guild_id}/channels")
        return data if isinstance(data, list) else []

    # Channel / Message endpoints

    async def get_channel_messages(self, channel_id: str, limit: int = 50) -> List[Message]:
        """
        Get recent messages from a channel

        Args:
            channel_id: The ID of the channel
            limit: Maximum number of messages to return (default 50)

        Returns:
            List of Message objects (newest first)
        """
        data = await self.http.get(
            f"channels/{channel_id}/messages",
            params={"limit": limit},
        )
        messages = data if isinstance(data, list) else []
        return [Message(m, client=self) for m in messages]

    async def send_message(self, channel_id: str, content: str) -> Message:
        """
        Send a message to a channel

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
        return Message(data, client=self)

    async def delete_message(self, channel_id: str, message_id: str) -> bool:
        """
        Delete a message

        Args:
            channel_id: The ID of the channel the message is in
            message_id: The ID of the message to delete

        Returns:
            True if successful
        """
        await self.http.delete(f"channels/{channel_id}/messages/{message_id}")
        return True
