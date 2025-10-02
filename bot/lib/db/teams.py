from bot.lib.convex_client import client
from bot.lib.log import log
import time


class TeamsServiceImpl:

    @staticmethod
    def find_by_id(team_id: str) -> dict:
        """Get team by ID"""
        try:
            result = client.query("teams:findById", {"teamId": team_id})
            return result
        except Exception as e:
            log(f"Error fetching team {team_id}: {e}")
            raise

    @staticmethod
    def find_by_thread_id(thread_id: str) -> dict:
        """Get team by Discord thread ID"""
        try:
            result = client.query("teams:findByThreadId", {"threadId": thread_id})
            return result
        except Exception as e:
            log(f"Error fetching team by thread {thread_id}: {e}")
            raise

    @staticmethod
    def create(name: str, captain_id: str, has_first_pick: bool) -> str:
        """Create a team, returns team ID"""
        try:
            result = client.mutation(
                "teams:create",
                {
                    "name": name,
                    "captainId": captain_id,
                    "hasFirstPick": has_first_pick,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Team '{name}' created with captain {captain_id}")
            return result
        except Exception as e:
            log(f"Error creating team {name}: {e}")
            raise
