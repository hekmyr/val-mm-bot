from typing import TypedDict
from discord import Member, User
from bot.lib.convex_client import client
from bot.lib.exceptions import BotException
from bot.lib.log import log


class UserDto(TypedDict):
    _id: str
    _creationTime: float
    discordId: str
    username: str
    updateTime: int


class UsersServiceImpl:

    @staticmethod
    def find_by_id(user_id: str) -> UserDto | None:
        try:
            result: UserDto | None = client.query("users:findById", {"userId": user_id})
            return result
        except Exception as e:
            raise BotException("USER_NOT_FOUND") from e

    @staticmethod
    def find_by_discord_id(discord_id: int) -> UserDto | None:
        try:
            result: UserDto | None = client.query("users:findByDiscordId", {"discordId": str(discord_id)})
            return result
        except Exception as e:
            raise BotException("USER_NOT_FOUND") from e

    @staticmethod
    def createOrFind(user: User | Member) -> int:
        try:
            result = client.mutation(
                "users:createOrFind",
                {
                    "discordId": str(user.id),
                    "username": user.name
                }
            )
            return result
        except Exception as e:
            raise
