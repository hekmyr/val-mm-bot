from typing import TypedDict
from bot.lib.convex_client import client
from bot.lib.exceptions import BotException
from bot.lib.log import log
import time


class MapDto(TypedDict):
    _id: str
    _creationTime: float
    name: str
    isEnabled: bool
    updateTime: int


class SeedMapItem(TypedDict):
    name: str
    id: str


class SeedMapsResult(TypedDict, total=False):
    message: str
    count: int
    previousCount: int
    added: int
    maps: list[SeedMapItem]


class MapsServiceImpl:

    @staticmethod
    def seed_maps() -> SeedMapsResult:
        try:
            result: SeedMapsResult = client.mutation("maps:seedMaps", {})
            log(f"Maps seeding result: {result}")
            return result
        except Exception as e:
            log(f"Error seeding maps: {e}")
            raise

    @staticmethod
    def get_all_maps() -> list[MapDto]:
        try:
            result: list[MapDto] = client.query("maps:list", {})
            return result
        except Exception as e:
            log(f"Error fetching all maps: {e}")
            raise

    @staticmethod
    def get_active_maps() -> list[MapDto]:
        try:
            result: list[MapDto] = client.query("maps:getActive", {})
            return result
        except Exception as e:
            log(f"Error fetching active maps: {e}")
            raise

    @staticmethod
    def get_map_by_name(name: str) -> MapDto | None:
        try:
            result: MapDto | None = client.query("maps:getByName", {"name": name})
            return result
        except Exception as e:
            log(f"Error fetching map {name}: {e}")
            raise

    @staticmethod
    def validate() -> bool:
        try:
            return client.query("maps:validate", {})
        except Exception as e:
            raise BotException("COULD_NOT_VALIDATE_MAPS")

    @staticmethod
    def create_map(name: str, is_enabled: bool) -> str:
        try:
            result: str = client.mutation(
                "maps:create",
                {
                    "name": name,
                    "isEnabled": is_enabled,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Map '{name}' created")
            return result
        except Exception as e:
            log(f"Error creating map {name}: {e}")
            raise
