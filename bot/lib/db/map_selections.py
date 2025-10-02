from bot.lib.convex_client import client
from bot.lib.log import log
import time


class MapSelectionsServiceImpl:

    @staticmethod
    def create(veto_id: str, map_id: str) -> str:
        """Create a map selection for a veto, returns selection ID"""
        try:
            result = client.mutation(
                "mapSelections:create",
                {
                    "vetoId": veto_id,
                    "mapId": map_id,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Map selection created: veto={veto_id}, map={map_id}")
            return result
        except Exception as e:
            log(f"Error creating map selection: {e}")
            raise
