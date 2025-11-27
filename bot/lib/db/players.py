from bot.lib.convex_client import client
from bot.lib.log import log
import time


class PlayersServiceImpl:

    @staticmethod
    def create(team_id: str, user_id: str) -> str:
        try:
            result = client.mutation(
                "players:create",
                {
                    "teamId": team_id,
                    "userId": user_id,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Player {user_id} added to team {team_id}")
            return result
        except Exception as e:
            log(f"Error adding player to team: {e}")
            raise

    @staticmethod
    def create_batch(team_id: str, user_ids: list[str]) -> list[str]:
        result_ids = []
        for user_id in user_ids:
            result_id = PlayersServiceImpl.create(team_id, user_id)
            result_ids.append(result_id)
        return result_ids
