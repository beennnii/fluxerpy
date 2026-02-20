"""
Fluxer.py - A Python wrapper for the Fluxer.web API
Similar to discord.py architecture
"""

from .client import Client
from .models import User, Post, Comment
from .errors import FluxerException, AuthenticationError, NotFoundError, RateLimitError

__version__ = "0.1.1"
__author__ = "beennnii"
__all__ = [
    "Client",
    "User",
    "Post",
    "Comment",
    "FluxerException",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
]
