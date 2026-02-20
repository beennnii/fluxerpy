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


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(BaseModel):
    """Represents a Fluxer user account"""

    @property
    def username(self) -> str:
        """The user's username (unique)"""
        return self._data.get("username", "")

    @property
    def discriminator(self) -> str:
        """The user's tag/discriminator (e.g. '0' on newer platforms)"""
        return self._data.get("discriminator", "0")

    @property
    def display_name(self) -> Optional[str]:
        """The user's display/global name"""
        return self._data.get("displayName") or self._data.get("global_name")

    @property
    def avatar_url(self) -> Optional[str]:
        """URL of the user's avatar"""
        return self._data.get("avatarUrl") or self._data.get("avatar")

    @property
    def bot(self) -> bool:
        """Whether this user is a bot account"""
        return bool(self._data.get("bot", False))

    @property
    def status(self) -> Optional[str]:
        """The user's current presence status (online/idle/dnd/offline)"""
        return self._data.get("status")

    @property
    def created_at(self) -> Optional[datetime]:
        """When the user account was created"""
        timestamp = self._data.get("createdAt") or self._data.get("created_at")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None

    def __str__(self) -> str:
        tag = f"#{self.discriminator}" if self.discriminator and self.discriminator != "0" else ""
        return f"{self.username}{tag}"


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------

class Role(BaseModel):
    """Represents a role in a Fluxer guild"""

    @property
    def name(self) -> str:
        """The role's name"""
        return self._data.get("name", "")

    @property
    def color(self) -> int:
        """The role's color as an integer (0 = no color)"""
        return self._data.get("color", 0)

    @property
    def permissions(self) -> int:
        """Bitfield of permissions granted by this role"""
        return int(self._data.get("permissions", 0))

    @property
    def position(self) -> int:
        """The role's position in the hierarchy (higher = more powerful)"""
        return self._data.get("position", 0)

    @property
    def mentionable(self) -> bool:
        """Whether the role can be mentioned by regular members"""
        return bool(self._data.get("mentionable", False))

    @property
    def hoist(self) -> bool:
        """Whether the role is displayed separately in the member list"""
        return bool(self._data.get("hoist", False))

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# Member
# ---------------------------------------------------------------------------

class Member(BaseModel):
    """Represents a guild member (user + guild-specific data)"""

    @property
    def user(self) -> Optional[User]:
        """The underlying User account"""
        user_data = self._data.get("user")
        if user_data:
            return User(user_data, self._client)
        return None

    @property
    def nick(self) -> Optional[str]:
        """The member's server nickname (None if not set)"""
        return self._data.get("nick")

    @property
    def display_name(self) -> str:
        """Nick if set, otherwise the user's global display name or username"""
        if self.nick:
            return self.nick
        u = self.user
        return (u.display_name or u.username) if u else ""

    @property
    def guild_id(self) -> str:
        """ID of the guild this member belongs to"""
        return self._data.get("guild_id", "")

    @property
    def roles(self) -> List[str]:
        """List of role IDs assigned to this member"""
        return self._data.get("roles", [])

    @property
    def joined_at(self) -> Optional[datetime]:
        """When the member joined the guild"""
        timestamp = self._data.get("joined_at")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None

    @property
    def deaf(self) -> bool:
        """Whether the member is server-deafened in voice channels"""
        return bool(self._data.get("deaf", False))

    @property
    def mute(self) -> bool:
        """Whether the member is server-muted in voice channels"""
        return bool(self._data.get("mute", False))

    async def kick(self, reason: Optional[str] = None):
        """Kick this member from the guild"""
        if self._client:
            return await self._client.kick_member(self.guild_id, self.id, reason=reason)

    async def ban(self, reason: Optional[str] = None, delete_message_seconds: int = 0):
        """Ban this member from the guild"""
        if self._client:
            return await self._client.ban_member(
                self.guild_id, self.id,
                reason=reason,
                delete_message_seconds=delete_message_seconds,
            )

    def __repr__(self):
        u = self.user
        tag = str(u) if u else self.id
        return f"<Member {tag} guild_id={self.guild_id}>"


# ---------------------------------------------------------------------------
# Channel
# ---------------------------------------------------------------------------

class Channel(BaseModel):
    """Represents a guild channel (text, voice, category, …)"""

    # Channel type constants (Discord-compatible)
    GUILD_TEXT     = 0
    DM             = 1
    GUILD_VOICE    = 2
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5

    @property
    def name(self) -> str:
        """The channel's name"""
        return self._data.get("name", "")

    @property
    def type(self) -> int:
        """Channel type integer (0 = text, 2 = voice, 4 = category, …)"""
        return self._data.get("type", 0)

    @property
    def guild_id(self) -> str:
        """ID of the guild this channel belongs to"""
        return self._data.get("guild_id", "")

    @property
    def topic(self) -> Optional[str]:
        """The channel topic/description"""
        return self._data.get("topic")

    @property
    def position(self) -> int:
        """The channel's sort order position"""
        return self._data.get("position", 0)

    @property
    def parent_id(self) -> Optional[str]:
        """ID of the parent category, if any"""
        return self._data.get("parent_id")

    @property
    def nsfw(self) -> bool:
        """Whether the channel is marked as NSFW"""
        return bool(self._data.get("nsfw", False))

    @property
    def is_text_channel(self) -> bool:
        """True if this is a plain text channel"""
        return self.type == self.GUILD_TEXT

    @property
    def is_voice_channel(self) -> bool:
        """True if this is a voice channel"""
        return self.type == self.GUILD_VOICE

    @property
    def is_category(self) -> bool:
        """True if this is a category"""
        return self.type == self.GUILD_CATEGORY

    async def send(self, content: str) -> "Message":
        """Send a message to this channel"""
        if self._client:
            return await self._client.send_message(self.id, content)
        raise RuntimeError("Channel has no client attached")

    async def get_messages(self, limit: int = 50) -> List["Message"]:
        """Fetch recent messages from this channel"""
        if self._client:
            return await self._client.get_channel_messages(self.id, limit=limit)
        return []

    async def delete(self):
        """Delete this channel"""
        if self._client:
            return await self._client.delete_channel(self.id)

    def __str__(self) -> str:
        return f"#{self.name}"


# ---------------------------------------------------------------------------
# Guild
# ---------------------------------------------------------------------------

class Guild(BaseModel):
    """Represents a Fluxer guild (server)"""

    @property
    def name(self) -> str:
        """The guild's name"""
        return self._data.get("name", "")

    @property
    def icon_url(self) -> Optional[str]:
        """URL of the guild's icon"""
        return self._data.get("iconUrl") or self._data.get("icon")

    @property
    def owner_id(self) -> str:
        """ID of the guild owner"""
        return self._data.get("owner_id", "")

    @property
    def member_count(self) -> int:
        """Approximate member count"""
        return (
            self._data.get("member_count")
            or self._data.get("memberCount")
            or self._data.get("approximate_member_count")
            or self._data.get("approximateMemberCount")
            or 0
        )

    @property
    def description(self) -> Optional[str]:
        """The guild's description"""
        return self._data.get("description")

    @property
    def preferred_locale(self) -> str:
        """Preferred locale of the guild (e.g. 'en-US', 'de')"""
        return self._data.get("preferred_locale", "en-US")

    @property
    def created_at(self) -> Optional[datetime]:
        """When the guild was created"""
        timestamp = self._data.get("createdAt") or self._data.get("created_at")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None

    async def get_channels(self) -> List[Channel]:
        """Fetch all channels in this guild"""
        if self._client:
            return await self._client.get_guild_channels(self.id)
        return []

    async def get_members(self, limit: int = 100) -> List[Member]:
        """Fetch members of this guild"""
        if self._client:
            return await self._client.get_guild_members(self.id, limit=limit)
        return []

    async def get_member(self, user_id: str) -> Optional[Member]:
        """Fetch a single member by user ID"""
        if self._client:
            return await self._client.get_guild_member(self.id, user_id)
        return None

    async def get_roles(self) -> List[Role]:
        """Fetch all roles in this guild"""
        if self._client:
            return await self._client.get_guild_roles(self.id)
        return []

    async def ban_member(self, user_id: str, reason: Optional[str] = None, delete_message_seconds: int = 0):
        """Ban a user from this guild"""
        if self._client:
            return await self._client.ban_member(
                self.id, user_id,
                reason=reason,
                delete_message_seconds=delete_message_seconds,
            )

    async def unban_member(self, user_id: str):
        """Unban a user from this guild"""
        if self._client:
            return await self._client.unban_member(self.id, user_id)

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# Reaction
# ---------------------------------------------------------------------------

class Reaction(BaseModel):
    """Represents a reaction on a message"""

    @property
    def emoji(self) -> str:
        """The emoji used for the reaction (e.g. '👍' or 'custom_name:12345')"""
        emoji_data = self._data.get("emoji", {})
        if isinstance(emoji_data, dict):
            name = emoji_data.get("name", "")
            eid = emoji_data.get("id")
            return f"{name}:{eid}" if eid else name
        return str(emoji_data)

    @property
    def count(self) -> int:
        """How many users reacted with this emoji"""
        return self._data.get("count", 0)

    @property
    def me(self) -> bool:
        """Whether the current user has added this reaction"""
        return bool(self._data.get("me", False))

    def __repr__(self):
        return f"<Reaction emoji={self.emoji!r} count={self.count}>"


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

class Message(BaseModel):
    """Represents a message in a Fluxer channel"""

    @property
    def content(self) -> str:
        """The message text content"""
        return self._data.get("content", "")

    @property
    def channel_id(self) -> str:
        """ID of the channel this message was sent in"""
        return self._data.get("channel_id", "")

    @property
    def guild_id(self) -> Optional[str]:
        """ID of the guild this message belongs to (None for DMs)"""
        return self._data.get("guild_id")

    @property
    def author(self) -> Optional[User]:
        """The user who sent this message"""
        author_data = self._data.get("author")
        if author_data:
            return User(author_data, self._client)
        return None

    @property
    def member(self) -> Optional[Member]:
        """Guild member data for the author (only present in guild messages)"""
        member_data = self._data.get("member")
        if member_data and self.guild_id:
            member_data.setdefault("guild_id", self.guild_id)
            if self._data.get("author"):
                member_data.setdefault("user", self._data["author"])
            return Member(member_data, self._client)
        return None

    @property
    def created_at(self) -> Optional[datetime]:
        """When the message was sent"""
        timestamp = self._data.get("timestamp") or self._data.get("created_at")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None

    @property
    def edited_at(self) -> Optional[datetime]:
        """When the message was last edited (None if never edited)"""
        timestamp = self._data.get("edited_timestamp") or self._data.get("edited_at")
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return None

    @property
    def reactions(self) -> List[Reaction]:
        """List of reactions on this message"""
        return [Reaction(r, self._client) for r in self._data.get("reactions", [])]

    @property
    def pinned(self) -> bool:
        """Whether this message is pinned in its channel"""
        return bool(self._data.get("pinned", False))

    @property
    def attachments(self) -> List[Dict[str, Any]]:
        """List of file attachment dicts"""
        return self._data.get("attachments", [])

    @property
    def embeds(self) -> List[Dict[str, Any]]:
        """List of embed dicts"""
        return self._data.get("embeds", [])

    async def reply(self, content: str) -> "Message":
        """Send a message to the same channel"""
        if self._client:
            return await self._client.send_message(self.channel_id, content)
        raise RuntimeError("Message has no client attached")

    async def delete(self):
        """Delete this message"""
        if self._client:
            return await self._client.delete_message(self.channel_id, self.id)

    async def edit(self, content: str) -> "Message":
        """Edit this message's content"""
        if self._client:
            return await self._client.edit_message(self.channel_id, self.id, content)
        raise RuntimeError("Message has no client attached")

    async def add_reaction(self, emoji: str):
        """Add a reaction to this message"""
        if self._client:
            return await self._client.add_reaction(self.channel_id, self.id, emoji)

    async def remove_reaction(self, emoji: str, user_id: Optional[str] = None):
        """Remove a reaction from this message"""
        if self._client:
            return await self._client.remove_reaction(self.channel_id, self.id, emoji, user_id=user_id)

    def __repr__(self):
        author = str(self.author) if self.author else "unknown"
        preview = self.content[:40] + "…" if len(self.content) > 40 else self.content
        return f"<Message id={self.id} author={author!r} content={preview!r}>"
