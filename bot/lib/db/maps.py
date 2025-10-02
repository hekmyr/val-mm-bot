from bot.lib.convex_client import client
from bot.lib.exceptions import BotException
from bot.lib.log import log
import time


class MapsServiceImpl:

    @staticmethod
    def seed_maps() -> dict:
        """Seed all Valorant maps into database"""
        try:
            result = client.mutation("maps:seedMaps", {})
            log(f"Maps seeding result: {result}")
            return result
        except Exception as e:
            log(f"Error seeding maps: {e}")
            raise

    @staticmethod
    def get_all_maps() -> list:
        """Get all maps"""
        try:
            result = client.query("maps:list", {})
            return result
        except Exception as e:
            log(f"Error fetching all maps: {e}")
            raise

    @staticmethod
    def get_active_maps() -> list:
        """Get only active (enabled) maps"""
        try:
            result = client.query("maps:getActive", {})
            return result
        except Exception as e:
            log(f"Error fetching active maps: {e}")
            raise

    @staticmethod
    def get_map_by_name(name: str) -> dict:
        """Get a specific map by name"""
        try:
            result = client.query("maps:getByName", {"name": name})
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
        """Create a new map"""
        try:
            result = client.mutation(
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
