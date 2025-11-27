from bot.lib.log import log
from bot.lib.test_constants import TEST_USER_IDS


class MockUser:
    
    def __init__(self, user_id: int) -> None:
        self.id = user_id
        self.name = f"test_user_{user_id}"
        self.mention = f"<@{user_id}>"

    async def send(self, message: str) -> None:
        log(f"[MOCK] Sending DM to user {self.id}: {message}")
        return None


class MockReady:
    
    @staticmethod
    def auto_ready_mock_users(bestof: int) -> None:
        from bot.lib.player_queue import PlayerContext
        
        match bestof:
            case 1:
                ready_set = PlayerContext._best_of_1_ready
            case 3:
                ready_set = PlayerContext._best_of_3_ready
            case 5:
                ready_set = PlayerContext._best_of_5_ready
            case _:
                return
        
        # Add all test users to ready set
        for user_id in TEST_USER_IDS:
            ready_set.add(user_id)
        
        log(f"[MOCK] Auto-marked {len(TEST_USER_IDS)} test users as ready for BO{bestof}")


class MockTeamBalancer:
    
    MY_USER_ID = 406530579547291651
    
    @staticmethod
    def balance_teams_mock(player_ids: list[int]) -> tuple[list[int], list[int]]:
        # Create 2 teams with MY_USER_ID as team1 captain.
        # Team1: MY_USER_ID + first 4 test users
        # Team2: remaining test users
        team1 = [MockTeamBalancer.MY_USER_ID] + TEST_USER_IDS[:4]
        team2 = TEST_USER_IDS[4:9]
        return team1, team2
    
    @staticmethod
    def pick_captain_mock(team_ids: list[int]) -> int:
        # Get captain - always MY_USER_ID if in team, else first player
        if MockTeamBalancer.MY_USER_ID in team_ids:
            return MockTeamBalancer.MY_USER_ID
        return team_ids[0]
    
    @staticmethod
    def get_first_pick_mock() -> bool:
        # Always give team1 (with MY_USER_ID) first pick
        return True
