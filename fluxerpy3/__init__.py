"""
Fluxer.py - A Python wrapper for the Fluxer API
Similar to discord.py architecture
"""

from .client import Client
from .models import User, Guild, Channel, Member, Role, Message, Reaction
from .errors import FluxerException, AuthenticationError, NotFoundError, RateLimitError, APIError
from .gateway import GatewayClient, Intents

__version__ = "0.2.0"
__author__ = "beennnii"
__all__ = [
    "Client",
    "User",
    "Guild",
    "Channel",
    "Member",
    "Role",
    "Message",
    "Reaction",
    "GatewayClient",
    "Intents",
    "FluxerException",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
]
