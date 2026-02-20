"""
Data models for Fluxer API
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class BaseModel:
    """Base class for all models"""
    
    def __init__(self, data: Dict[str, Any], client=None):
        self._data = data
        self._client = client
        
    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
        
    @property
    def id(self) -> str:
        """The unique ID of the object"""
        return self._data.get("id", "")


class User(BaseModel):
    """Represents a Fluxer user"""
    
    @property
    def username(self) -> str:
        """The user's username"""
        return self._data.get("username", "")
        
    @property
    def display_name(self) -> Optional[str]:
        """The user's display name"""
        return self._data.get("displayName")
        
    @property
    def bio(self) -> Optional[str]:
        """The user's bio/description"""
        return self._data.get("bio")
        
    @property
    def avatar_url(self) -> Optional[str]:
        """URL of the user's avatar"""
        return self._data.get("avatarUrl")
        
    @property
    def follower_count(self) -> int:
        """Number of followers"""
        return self._data.get("followerCount", 0)
        
    @property
    def following_count(self) -> int:
        """Number of users being followed"""
        return self._data.get("followingCount", 0)
        
    @property
    def post_count(self) -> int:
        """Number of posts"""
        return self._data.get("postCount", 0)
        
    @property
    def created_at(self) -> Optional[datetime]:
        """When the user account was created"""
        timestamp = self._data.get("createdAt")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None
        
    async def follow(self):
        """Follow this user"""
        if self._client:
            return await self._client.follow_user(self.id)
            
    async def unfollow(self):
        """Unfollow this user"""
        if self._client:
            return await self._client.unfollow_user(self.id)
            
    async def get_posts(self, limit: int = 20):
        """Get posts by this user"""
        if self._client:
            return await self._client.get_user_posts(self.id, limit=limit)
        return []


class Post(BaseModel):
    """Represents a Fluxer post"""
    
    @property
    def content(self) -> str:
        """The post content/text"""
        return self._data.get("content", "")
        
    @property
    def author_id(self) -> str:
        """ID of the post author"""
        return self._data.get("authorId", "")
        
    @property
    def author(self) -> Optional[User]:
        """The post author (if available)"""
        author_data = self._data.get("author")
        if author_data:
            return User(author_data, self._client)
        return None
        
    @property
    def like_count(self) -> int:
        """Number of likes"""
        return self._data.get("likeCount", 0)
        
    @property
    def comment_count(self) -> int:
        """Number of comments"""
        return self._data.get("commentCount", 0)
        
    @property
    def repost_count(self) -> int:
        """Number of reposts"""
        return self._data.get("repostCount", 0)
        
    @property
    def created_at(self) -> Optional[datetime]:
        """When the post was created"""
        timestamp = self._data.get("createdAt")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None
        
    @property
    def media_urls(self) -> List[str]:
        """List of media URLs attached to the post"""
        return self._data.get("mediaUrls", [])
        
    async def like(self):
        """Like this post"""
        if self._client:
            return await self._client.like_post(self.id)
            
    async def unlike(self):
        """Unlike this post"""
        if self._client:
            return await self._client.unlike_post(self.id)
            
    async def repost(self):
        """Repost this post"""
        if self._client:
            return await self._client.repost(self.id)
            
    async def delete(self):
        """Delete this post"""
        if self._client:
            return await self._client.delete_post(self.id)
            
    async def get_comments(self, limit: int = 20):
        """Get comments on this post"""
        if self._client:
            return await self._client.get_post_comments(self.id, limit=limit)
        return []
        
    async def comment(self, content: str):
        """Comment on this post"""
        if self._client:
            return await self._client.create_comment(self.id, content)


class Comment(BaseModel):
    """Represents a comment on a post"""
    
    @property
    def content(self) -> str:
        """The comment content/text"""
        return self._data.get("content", "")
        
    @property
    def author_id(self) -> str:
        """ID of the comment author"""
        return self._data.get("authorId", "")
        
    @property
    def author(self) -> Optional[User]:
        """The comment author (if available)"""
        author_data = self._data.get("author")
        if author_data:
            return User(author_data, self._client)
        return None
        
    @property
    def post_id(self) -> str:
        """ID of the post this comment belongs to"""
        return self._data.get("postId", "")
        
    @property
    def like_count(self) -> int:
        """Number of likes"""
        return self._data.get("likeCount", 0)
        
    @property
    def created_at(self) -> Optional[datetime]:
        """When the comment was created"""
        timestamp = self._data.get("createdAt")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None
        
    async def like(self):
        """Like this comment"""
        if self._client:
            return await self._client.like_comment(self.id)
            
    async def unlike(self):
        """Unlike this comment"""
        if self._client:
            return await self._client.unlike_comment(self.id)
            
    async def delete(self):
        """Delete this comment"""
        if self._client:
            return await self._client.delete_comment(self.id)


class Message(BaseModel):
    """Represents a message in a Fluxer channel (guild text channel)"""

    @property
    def content(self) -> str:
        """The message text"""
        return self._data.get("content", "")

    @property
    def channel_id(self) -> str:
        """ID of the channel this message belongs to"""
        return self._data.get("channel_id", "")

    @property
    def author(self) -> Optional["User"]:
        """The message author (if available)"""
        author_data = self._data.get("author")
        if author_data:
            return User(author_data, self._client)
        return None

    @property
    def post_id(self) -> str:
        """Alias for id – keeps backward compatibility with Comment-based moderation logic"""
        return self.id

    @property
    def created_at(self) -> Optional[datetime]:
        """When the message was sent"""
        timestamp = self._data.get("timestamp") or self._data.get("created_at")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None

    async def delete(self):
        """Delete this message"""
        if self._client:
            return await self._client.delete_message(self.channel_id, self.id)

    async def reply(self, content: str):
        """Send a message to the same channel"""
        if self._client:
            return await self._client.send_message(self.channel_id, content)

    async def comment(self, content: str):
        """Alias for reply() – keeps backward compatibility with Post-based moderation logic"""
        return await self.reply(content)

    async def get_comments(self, limit: int = 20) -> list:
        """No-op – messages don't have comments; exists for interface compatibility"""
        return []
