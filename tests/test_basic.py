"""
Basic tests for fluxerpy3
"""

import pytest
from fluxerpy3 import Client, User, Guild, Channel, Member, Role, Message, Reaction
from fluxerpy3.errors import FluxerException, AuthenticationError, NotFoundError, APIError


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def test_client_initialization():
    """Client can be initialized with a token"""
    client = Client(token="test_token")
    assert client.token == "test_token"
    assert client.base_url == "https://api.fluxer.app/v1"


def test_client_custom_base_url():
    """Client accepts a custom base URL"""
    client = Client(token="test_token", base_url="https://custom.api.com")
    assert client.base_url == "https://custom.api.com"


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------

def test_user_model():
    """User model exposes its properties correctly"""
    data = {
        "id": "user123",
        "username": "testuser",
        "displayName": "Test User",
        "discriminator": "1234",
        "bot": False,
        "status": "online",
    }
    user = User(data)
    assert user.id == "user123"
    assert user.username == "testuser"
    assert user.display_name == "Test User"
    assert user.discriminator == "1234"
    assert user.bot is False
    assert user.status == "online"
    assert str(user) == "testuser#1234"


def test_user_bot_flag():
    """User.bot is True for bot accounts"""
    user = User({"id": "1", "username": "mybot", "bot": True})
    assert user.bot is True


# ---------------------------------------------------------------------------
# Guild model
# ---------------------------------------------------------------------------

def test_guild_model():
    """Guild model exposes its properties correctly"""
    data = {
        "id": "guild123",
        "name": "Test Server",
        "owner_id": "user123",
        "member_count": 42,
        "description": "A test guild",
        "preferred_locale": "de",
    }
    guild = Guild(data)
    assert guild.id == "guild123"
    assert guild.name == "Test Server"
    assert guild.owner_id == "user123"
    assert guild.member_count == 42
    assert guild.description == "A test guild"
    assert guild.preferred_locale == "de"
    assert str(guild) == "Test Server"


# ---------------------------------------------------------------------------
# Channel model
# ---------------------------------------------------------------------------

def test_channel_model_text():
    """Channel model correctly identifies a text channel"""
    data = {
        "id": "chan1",
        "name": "general",
        "type": Channel.GUILD_TEXT,
        "guild_id": "guild123",
        "topic": "General discussion",
        "position": 0,
    }
    channel = Channel(data)
    assert channel.id == "chan1"
    assert channel.name == "general"
    assert channel.is_text_channel is True
    assert channel.is_voice_channel is False
    assert channel.is_category is False
    assert channel.topic == "General discussion"
    assert str(channel) == "#general"


def test_channel_model_voice():
    """Channel model correctly identifies a voice channel"""
    data = {"id": "vc1", "name": "Voice Lounge", "type": Channel.GUILD_VOICE, "guild_id": "guild123"}
    channel = Channel(data)
    assert channel.is_voice_channel is True
    assert channel.is_text_channel is False


def test_channel_model_category():
    """Channel model correctly identifies a category"""
    data = {"id": "cat1", "name": "INFORMATION", "type": Channel.GUILD_CATEGORY, "guild_id": "guild123"}
    channel = Channel(data)
    assert channel.is_category is True


# ---------------------------------------------------------------------------
# Member model
# ---------------------------------------------------------------------------

def test_member_model():
    """Member model exposes user and guild-specific data"""
    data = {
        "id": "user123",
        "guild_id": "guild123",
        "nick": "Server Nick",
        "roles": ["role1", "role2"],
        "joined_at": "2024-01-01T00:00:00Z",
        "user": {
            "id": "user123",
            "username": "testuser",
            "discriminator": "0",
        },
    }
    member = Member(data)
    assert member.nick == "Server Nick"
    assert member.display_name == "Server Nick"
    assert member.guild_id == "guild123"
    assert "role1" in member.roles
    assert member.user is not None
    assert member.user.username == "testuser"


def test_member_display_name_fallback():
    """Member.display_name falls back to username when no nick is set"""
    data = {
        "id": "user123",
        "guild_id": "guild123",
        "nick": None,
        "roles": [],
        "user": {"id": "user123", "username": "fallbackuser", "displayName": "Fallback"},
    }
    member = Member(data)
    assert member.display_name == "Fallback"


# ---------------------------------------------------------------------------
# Role model
# ---------------------------------------------------------------------------

def test_role_model():
    """Role model exposes its properties correctly"""
    data = {
        "id": "role123",
        "name": "Moderator",
        "color": 0xFF0000,
        "permissions": "8",
        "position": 5,
        "mentionable": True,
        "hoist": True,
    }
    role = Role(data)
    assert role.id == "role123"
    assert role.name == "Moderator"
    assert role.color == 0xFF0000
    assert role.permissions == 8
    assert role.position == 5
    assert role.mentionable is True
    assert role.hoist is True
    assert str(role) == "Moderator"


# ---------------------------------------------------------------------------
# Message model
# ---------------------------------------------------------------------------

def test_message_model():
    """Message model exposes its properties correctly"""
    data = {
        "id": "msg123",
        "content": "Hello, world!",
        "channel_id": "chan1",
        "guild_id": "guild123",
        "timestamp": "2024-06-01T12:00:00Z",
        "author": {
            "id": "user123",
            "username": "testuser",
            "discriminator": "0",
        },
    }
    msg = Message(data)
    assert msg.id == "msg123"
    assert msg.content == "Hello, world!"
    assert msg.channel_id == "chan1"
    assert msg.guild_id == "guild123"
    assert msg.author is not None
    assert msg.author.username == "testuser"
    assert msg.created_at is not None


def test_message_reactions():
    """Message.reactions returns Reaction objects"""
    data = {
        "id": "msg1",
        "content": "hi",
        "channel_id": "c1",
        "reactions": [
            {"emoji": {"name": "👍", "id": None}, "count": 3, "me": False},
            {"emoji": {"name": "flame", "id": "999"}, "count": 1, "me": True},
        ],
    }
    msg = Message(data)
    assert len(msg.reactions) == 2
    assert msg.reactions[0].count == 3
    assert msg.reactions[0].emoji == "👍"
    assert msg.reactions[1].me is True


# ---------------------------------------------------------------------------
# Reaction model
# ---------------------------------------------------------------------------

def test_reaction_model():
    """Reaction model exposes emoji, count, and me"""
    data = {"emoji": {"name": "🔥", "id": None}, "count": 7, "me": True}
    reaction = Reaction(data)
    assert reaction.emoji == "🔥"
    assert reaction.count == 7
    assert reaction.me is True


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

def test_exceptions_hierarchy():
    """Custom exceptions inherit from FluxerException"""
    assert issubclass(AuthenticationError, FluxerException)
    assert issubclass(NotFoundError, FluxerException)
    assert issubclass(APIError, FluxerException)


def test_rate_limit_error():
    """RateLimitError carries retry_after"""
    from fluxerpy3.errors import RateLimitError
    err = RateLimitError("Too fast", retry_after=30)
    assert err.retry_after == 30


def test_authentication_error():
    """AuthenticationError carries response_body"""
    err = AuthenticationError("Unauthorized", response_body='{"error":"invalid_token"}')
    assert "invalid_token" in err.response_body


# ---------------------------------------------------------------------------
# Async context manager
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_client_context_manager():
    """Client works as an async context manager"""
    client = Client(token="test_token")
    async with client:
        assert client.http.session is not None
    # Session should be closed after exiting context
    assert client.http.session is None or client.http.session.closed
