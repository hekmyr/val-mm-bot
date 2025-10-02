from discord import Member, User
from bot.lib.convex_client import client
from bot.lib.log import log


class UsersServiceImpl:

    @staticmethod
    def find_by_id(user_id: str) -> dict:
        """Get user by Convex ID"""
        try:
            result = client.query("users:findById", {"userId": user_id})
            return result
        except Exception as e:
            log(f"Error fetching user {user_id}: {e}")
            raise

    @staticmethod
    def find_by_discord_id(discord_id: str) -> dict:
        """Get user by Discord ID"""
        try:
            result = client.query("users:findByDiscordId", {"discordId": discord_id})
            return result
        except Exception as e:
            log(f"Error fetching user by Discord ID {discord_id}: {e}")
            raise

    @staticmethod
    def createOrFind(user: User | Member) -> int:
        """Create or find user, returns user ID"""
        try:
            result = client.mutation(
                "users:createOrFind",
                {
                    "discordId": str(user.id),
                    "username": user.name
                }
            )
            log(f"User {user.name} (ID: {user.id}) created/found")
            return result
        except Exception as e:
            log(f"Error creating/finding user {user.id}: {e}")
            raise
