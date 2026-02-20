"""
Example showing member and channel interactions in fluxerpy3
"""

import asyncio
import os
import fluxerpy3


BOT_TOKEN = os.environ.get("FLUXER_TOKEN", "your_bot_token_here")

# Replace with real IDs from your Fluxer guild
GUILD_ID   = "your_guild_id_here"
CHANNEL_ID = "your_channel_id_here"
USER_ID    = "target_user_id_here"


async def main():
    async with fluxerpy3.Client(token=BOT_TOKEN) as client:

        # ── Bot information ──────────────────────────────────
        me = await client.get_me()
        print(f"Bot account : {me.username} (id={me.id}, bot={me.bot})")

        # ── Guild information ────────────────────────────────
        guild = await client.get_guild(GUILD_ID)
        print(f"\nGuild       : {guild.name}")
        print(f"Members     : ~{guild.member_count}")
        print(f"Description : {guild.description or 'none'}")

        # ── Roles ────────────────────────────────────────────
        roles = await client.get_guild_roles(GUILD_ID)
        print(f"\nRoles ({len(roles)}):")
        for role in sorted(roles, key=lambda r: r.position, reverse=True):
            print(f"  [{role.position:>3}] @{role.name}")

        # ── Member lookup ─────────────────────────────────────
        try:
            member = await client.get_guild_member(GUILD_ID, USER_ID)
            print(f"\nMember      : {member.display_name}")
            print(f"Joined      : {member.joined_at}")
            print(f"Roles       : {member.roles}")
        except fluxerpy3.NotFoundError:
            print(f"\nUser {USER_ID} is not a member of this guild.")

        # ── Channel messages ──────────────────────────────────
        print(f"\nFetching messages from channel {CHANNEL_ID}...")
        messages = await client.get_channel_messages(CHANNEL_ID, limit=10)
        print(f"Last {len(messages)} messages:")
        for msg in messages:
            author = str(msg.author) if msg.author else "unknown"
            ts = msg.created_at.strftime("%H:%M") if msg.created_at else "?"
            print(f"  [{ts}] {author}: {msg.content[:60]}")

        # ── Send a message ────────────────────────────────────
        sent = await client.send_message(CHANNEL_ID, "Hello from fluxerpy3! 👋")
        print(f"\nSent message id : {sent.id}")

        # ── React to the sent message ─────────────────────────
        await client.add_reaction(CHANNEL_ID, sent.id, "👍")
        print("Added 👍 reaction")

        # ── Edit and then delete the message ──────────────────
        await asyncio.sleep(1)
        edited = await client.edit_message(CHANNEL_ID, sent.id, "(edited) Hello! ✏️")
        print(f"Edited message  : {edited.content}")

        await asyncio.sleep(1)
        await client.delete_message(CHANNEL_ID, sent.id)
        print("Deleted message")


if __name__ == "__main__":
    asyncio.run(main())
