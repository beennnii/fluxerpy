"""
Basic tests for fluxerpy
"""

import pytest
import asyncio
from fluxerpy import Client, User, Post, Comment
from fluxerpy.errors import FluxerException, AuthenticationError, NotFoundError


def test_client_initialization():
    """Test that the client can be initialized"""
    client = Client(token="test_token")
    assert client.token == "test_token"
    assert client.base_url == "https://api.fluxer.app/v1"


def test_client_custom_base_url():
    """Test that the client can be initialized with a custom base URL"""
    client = Client(token="test_token", base_url="https://custom.api.com")
    assert client.base_url == "https://custom.api.com"


def test_user_model():
    """Test User model initialization"""
    data = {
        "id": "user123",
        "username": "testuser",
        "displayName": "Test User",
        "bio": "This is a test bio",
        "followerCount": 100,
        "followingCount": 50,
    }
    user = User(data)
    assert user.id == "user123"
    assert user.username == "testuser"
    assert user.display_name == "Test User"
    assert user.bio == "This is a test bio"
    assert user.follower_count == 100
    assert user.following_count == 50


def test_post_model():
    """Test Post model initialization"""
    data = {
        "id": "post123",
        "content": "Test post content",
        "authorId": "user123",
        "likeCount": 10,
        "commentCount": 5,
        "repostCount": 2,
    }
    post = Post(data)
    assert post.id == "post123"
    assert post.content == "Test post content"
    assert post.author_id == "user123"
    assert post.like_count == 10
    assert post.comment_count == 5
    assert post.repost_count == 2


def test_comment_model():
    """Test Comment model initialization"""
    data = {
        "id": "comment123",
        "content": "Test comment",
        "authorId": "user123",
        "postId": "post123",
        "likeCount": 3,
    }
    comment = Comment(data)
    assert comment.id == "comment123"
    assert comment.content == "Test comment"
    assert comment.author_id == "user123"
    assert comment.post_id == "post123"
    assert comment.like_count == 3


def test_exceptions():
    """Test that custom exceptions exist"""
    assert issubclass(AuthenticationError, FluxerException)
    assert issubclass(NotFoundError, FluxerException)


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test that the client can be used as a context manager"""
    client = Client(token="test_token")
    async with client:
        assert client.http.session is not None
    # Session should be closed after exiting context
    assert client.http.session is None or client.http.session.closed
