"""
Advanced example showing error handling and best practices
"""

import asyncio
import logging
from typing import List
from fluxerpy import (
    Client,
    Post,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def retry_on_rate_limit(coro, max_retries=3):
    """
    Retry a coroutine on rate limit errors
    
    Args:
        coro: The coroutine to retry
        max_retries: Maximum number of retries
        
    Returns:
        The result of the coroutine
    """
    for attempt in range(max_retries):
        try:
            return await coro
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = e.retry_after or 60
            logger.warning(f"Rate limited, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(wait_time)


async def process_feed_with_filters(client: Client, min_likes: int = 10) -> List[Post]:
    """
    Process feed and filter posts by engagement
    
    Args:
        client: The Fluxer client
        min_likes: Minimum number of likes to consider a post
        
    Returns:
        List of filtered posts
    """
    try:
        posts = await retry_on_rate_limit(client.get_feed(limit=50))
        
        # Filter posts by likes
        popular_posts = [post for post in posts if post.like_count >= min_likes]
        logger.info(f"Found {len(popular_posts)} posts with at least {min_likes} likes")
        
        return popular_posts
        
    except APIError as e:
        logger.error(f"API error while fetching feed: {e}")
        return []


async def engage_with_posts(client: Client, posts: List[Post]):
    """
    Engage with a list of posts (like and comment)
    
    Args:
        client: The Fluxer client
        posts: List of posts to engage with
    """
    for post in posts:
        try:
            # Like the post
            await retry_on_rate_limit(post.like())
            logger.info(f"Liked post by @{post.author.username if post.author else 'unknown'}")
            
            # Comment on really popular posts
            if post.like_count > 50:
                comment_text = "Great content! 🔥"
                await retry_on_rate_limit(post.comment(comment_text))
                logger.info(f"Commented on popular post {post.id}")
            
            # Small delay between actions
            await asyncio.sleep(1)
            
        except NotFoundError:
            logger.warning(f"Post {post.id} not found, may have been deleted")
        except Exception as e:
            logger.error(f"Error engaging with post {post.id}: {e}")


async def get_user_stats(client: Client, username: str):
    """
    Get and display user statistics
    
    Args:
        client: The Fluxer client
        username: Username to lookup
    """
    try:
        user = await retry_on_rate_limit(client.get_user_by_username(username))
        
        logger.info(f"""
User Stats for @{user.username}:
- Display Name: {user.display_name or 'Not set'}
- Bio: {user.bio or 'No bio'}
- Followers: {user.follower_count}
- Following: {user.following_count}
- Posts: {user.post_count}
- Created: {user.created_at}
        """)
        
        # Get user's recent posts
        posts = await retry_on_rate_limit(user.get_posts(limit=5))
        logger.info(f"\nRecent posts from @{user.username}:")
        for i, post in enumerate(posts, 1):
            logger.info(f"{i}. {post.content[:50]}... ({post.like_count} likes)")
            
    except NotFoundError:
        logger.error(f"User @{username} not found")
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")


async def main():
    """Main function demonstrating advanced usage"""
    
    # Get token from environment or configuration
    token = "your_token_here"  # In production, use environment variables
    
    try:
        async with Client(token=token) as client:
            # Get current user
            try:
                me = await client.get_me()
                logger.info(f"Successfully logged in as @{me.username}")
            except AuthenticationError:
                logger.error("Authentication failed. Please check your token.")
                return
            
            # Get and process feed
            logger.info("Fetching and processing feed...")
            popular_posts = await process_feed_with_filters(client, min_likes=10)
            
            # Engage with popular posts
            if popular_posts:
                logger.info(f"Engaging with {len(popular_posts)} popular posts...")
                await engage_with_posts(client, popular_posts[:5])  # Limit to 5 posts
            
            # Get stats for a specific user
            await get_user_stats(client, "example_user")
            
            # Create a summary post
            summary = f"Just processed {len(popular_posts)} posts! 🚀"
            try:
                new_post = await retry_on_rate_limit(client.create_post(summary))
                logger.info(f"Created summary post: {new_post.id}")
            except Exception as e:
                logger.error(f"Failed to create summary post: {e}")
            
            logger.info("Session completed successfully!")
            
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
