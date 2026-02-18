# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-17

### Added
- Initial release of Fluxerpy3 API wrapper
- `Client` class for interacting with Fluxer API
- `HTTPClient` for handling HTTP requests with proper error handling
- Data models: `User`, `Post`, `Comment`
- Custom exception classes: `FluxerException`, `AuthenticationError`, `NotFoundError`, `RateLimitError`, `APIError`
- Event system for extensibility (similar to discord.py)
- Comprehensive documentation and usage guide
- Example scripts demonstrating basic usage, event handling, and user interactions
- Unit tests with pytest and pytest-asyncio
- Full type hints support
- Async/await support using aiohttp

### Features
- User operations: get user, follow/unfollow, get user posts
- Post operations: create, delete, like/unlike, repost, get feed
- Comment operations: create, delete, like/unlike, get comments
- Context manager support for proper resource cleanup
- Rate limiting handling with retry-after support
- Authentication via Bearer token
- Customizable base URL for API endpoints

[0.1.0]: https://github.com/beennnii/fluxerpy/releases/tag/v0.1.0
