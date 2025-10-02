from bot.lib.convex_client import client
from bot.lib.log import log
import time


class MatchesServiceImpl:

    @staticmethod
    def find_by_id(match_id: str) -> dict:
        """Get match by ID"""
        try:
            result = client.query("matches:findById", {"matchId": match_id})
            return result
        except Exception as e:
            log(f"Error fetching match {match_id}: {e}")
            raise

    @staticmethod
    def find_by_thread_id(thread_id: str) -> dict:
        """Get match by Discord thread ID"""
        try:
            result = client.query("matches:findByThreadId", {"threadId": thread_id})
            return result
        except Exception as e:
            log(f"Error fetching match by thread {thread_id}: {e}")
            raise

    @staticmethod
    def create(team1_id: str, team2_id: str, best_of: int) -> str:
        """Create a match, returns match ID"""
        try:
            result = client.mutation(
                "matches:create",
                {
                    "team1": team1_id,
                    "team2": team2_id,
                    "bestOf": best_of,
                    "status": "veto_phase",
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Match created: {team1_id} vs {team2_id} (BO{best_of})")
            return result
        except Exception as e:
            log(f"Error creating match: {e}")
            raise

    @staticmethod
    def update_thread_id(match_id: str, thread_id: str) -> None:
        """Update match with Discord thread ID"""
        try:
            client.mutation(
                "matches:updateThreadId",
                {
                    "matchId": match_id,
                    "threadId": thread_id,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Match {match_id} thread ID updated to {thread_id}")
        except Exception as e:
            log(f"Error updating match thread: {e}")
            raise

    @staticmethod
    def update_status(match_id: str, status: str) -> None:
        """Update match status"""
        try:
            client.mutation(
                "matches:updateStatus",
                {
                    "matchId": match_id,
                    "status": status,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Match {match_id} status updated to {status}")
        except Exception as e:
            log(f"Error updating match status: {e}")
            raise

    @staticmethod
    def set_score(match_id: str, team1_score: int, team2_score: int) -> None:
        try:
            client.mutation(
                "matches:setScore",
                {
                    "matchId": match_id,
                    "team1Score": team1_score,
                    "team2Score": team2_score,
                    "updateTime": int(time.time() * 1000)
                }
            )
            log(f"Match {match_id} score set to {team1_score}-{team2_score}")
        except Exception as e:
            log(f"Error setting match score: {e}")
            raise
