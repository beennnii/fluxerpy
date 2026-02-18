"""
Example showing event handling in fluxerpy3
"""

import asyncio
import fluxerpy3


client = fluxerpy3.Client(token="your_token_here")


@client.event
async def on_post_created(post):
    """Called when a new post is created"""
    print(f"New post created: {post.content}")


async def main():
    async with client:
        # Get current user
        me = await client.get_me()
        print(f"Logged in as: {me.username}")
        
        # Create a post (this will trigger the on_post_created event)
        await client.create_post("Testing event handlers! 🎉")
        
        # Keep the client running for a bit
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
