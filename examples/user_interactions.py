"""
Example showing user interactions
"""

import asyncio
import fluxerpy3


async def main():
    async with fluxerpy3.Client(token="your_token_here") as client:
        # Search for a user by username
        user = await client.get_user_by_username("example_user")
        print(f"Found user: {user.username}")
        print(f"Display name: {user.display_name}")
        print(f"Bio: {user.bio}")
        
        # Follow the user
        await user.follow()
        print(f"Now following {user.username}")
        
        # Get their posts
        posts = await user.get_posts(limit=10)
        print(f"\nRecent posts from {user.username}:")
        for post in posts:
            print(f"  - {post.content[:50]}...")
            
        # Like their latest post
        if posts:
            latest_post = posts[0]
            await latest_post.like()
            print(f"\nLiked post: {latest_post.id}")
            
            # Comment on the post
            comment = await latest_post.comment("Great post! 👍")
            print(f"Added comment: {comment.id}")


if __name__ == "__main__":
    asyncio.run(main())
