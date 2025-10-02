from bot.lib.convex_client import client
from bot.lib.log import log
import time


class VetosServiceImpl:

    @staticmethod
    def create(match_id: str, team_id: str, action: str, order: int) -> str:
        """Create a veto action, returns veto ID"""
        try:
            result = client.mutation(
                "vetos:create",
                {
                    "matchId": match_id,
                    "teamId": team_id,
                    "action": action,
                    "order": order,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Veto created: match={match_id}, team={team_id}, action={action}, order={order}")
            return result
        except Exception as e:
            log(f"Error creating veto: {e}")
            raise

    @staticmethod
    def create_batch(match_id: str, veto_sequence: list[dict]) -> list[str]:
        """Create multiple vetos from sequence"""
        result_ids = []
        for veto_step in veto_sequence:
            veto_id = VetosServiceImpl.create(
                match_id=match_id,
                team_id=veto_step["team_id"],
                action=veto_step["action"].value,
                order=veto_step["order"]
            )
            result_ids.append(veto_id)
        return result_ids
