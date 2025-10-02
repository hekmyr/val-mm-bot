from bot.lib.convex_client import client
from bot.lib.log import log
import time


class SideSelectionsServiceImpl:

    @staticmethod
    def create(veto_id: str, side: str) -> str:
        """Create a side selection for a veto, returns selection ID"""
        try:
            result = client.mutation(
                "sideSelections:create",
                {
                    "vetoId": veto_id,
                    "side": side,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Side selection created: veto={veto_id}, side={side}")
            return result
        except Exception as e:
            log(f"Error creating side selection: {e}")
            raise
