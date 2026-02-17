"""
Basic example of using fluxerpy
"""

import asyncio
import fluxerpy


async def main():
    # Create a client with your authentication token
    client = fluxerpy.Client(token="your_token_here")
    
    try:
        # Start the client
        await client.start()
        
        # Get current user
        me = await client.get_me()
        print(f"Logged in as: {me.username}")
        print(f"Followers: {me.follower_count}")
        print(f"Following: {me.following_count}")
        
        # Get feed
        print("\nFetching feed...")
        posts = await client.get_feed(limit=5)
        
        for post in posts:
            author = post.author
            if author:
                print(f"\n@{author.username}: {post.content}")
                print(f"  Likes: {post.like_count} | Comments: {post.comment_count}")
        
        # Create a post
        new_post = await client.create_post("Hello from fluxerpy! 🚀")
        print(f"\nCreated post: {new_post.id}")
        
    finally:
        # Close the client when done
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
