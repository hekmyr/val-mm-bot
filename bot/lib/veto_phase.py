from enum import Enum
from typing import TypedDict

class VetoAction(Enum):
    BAN = "ban"
    PICK = "pick"
    SIDE_PICK = "side_pick"

class VetoPhaseDict(TypedDict):
    team: str
    action: VetoAction
    round: int
    description: str

class VetoPhase:
    
    @staticmethod
    def get_veto_sequence(best_of: int, team_a_has_first_pick: bool) -> list[VetoPhaseDict]:
        if best_of == 1:
            return VetoPhase._bo1_sequence()
        elif best_of == 3:
            return VetoPhase._bo3_sequence()
        elif best_of == 5:
            return VetoPhase._bo5_sequence()
        return []
    
    @staticmethod
    def _bo1_sequence() -> list[VetoPhaseDict]:
        return [
            {"team": "A", "action": VetoAction.BAN, "round": 1, "description": "Team A bans map"},
            {"team": "B", "action": VetoAction.BAN, "round": 1, "description": "Team B bans map"},
            {"team": "A", "action": VetoAction.BAN, "round": 2, "description": "Team A bans map"},
            {"team": "B", "action": VetoAction.BAN, "round": 2, "description": "Team B bans map"},
            {"team": "A", "action": VetoAction.BAN, "round": 3, "description": "Team A bans map"},
            {"team": "B", "action": VetoAction.BAN, "round": 3, "description": "Team B bans map"},
            {"team": "A", "action": VetoAction.SIDE_PICK, "round": 1, "description": "Team A picks side (ATK/DEF)"},
        ]
    
    @staticmethod
    def _bo3_sequence() -> list[VetoPhaseDict]:
        return [
            {"team": "A", "action": VetoAction.BAN, "round": 1, "description": "Team A bans map"},
            {"team": "B", "action": VetoAction.BAN, "round": 1, "description": "Team B bans map"},
            {"team": "A", "action": VetoAction.PICK, "round": 1, "description": "Team A picks map 1"},
            {"team": "B", "action": VetoAction.SIDE_PICK, "round": 1, "description": "Team B picks side for map 1"},
            {"team": "B", "action": VetoAction.PICK, "round": 2, "description": "Team B picks map 2"},
            {"team": "A", "action": VetoAction.SIDE_PICK, "round": 2, "description": "Team A picks side for map 2"},
            {"team": "A", "action": VetoAction.BAN, "round": 2, "description": "Team A bans map"},
            {"team": "B", "action": VetoAction.BAN, "round": 2, "description": "Team B bans map"},
            {"team": "A", "action": VetoAction.SIDE_PICK, "round": 3, "description": "Team A picks side for map 3 (decider)"},
        ]
    
    @staticmethod
    def _bo5_sequence() -> list[VetoPhaseDict]:
        return [
            {"team": "A", "action": VetoAction.BAN, "round": 1, "description": "Team A bans map"},
            {"team": "B", "action": VetoAction.BAN, "round": 1, "description": "Team B bans map"},
            {"team": "A", "action": VetoAction.PICK, "round": 1, "description": "Team A picks map 1"},
            {"team": "B", "action": VetoAction.SIDE_PICK, "round": 1, "description": "Team B picks side for map 1"},
            {"team": "B", "action": VetoAction.PICK, "round": 2, "description": "Team B picks map 2"},
            {"team": "A", "action": VetoAction.SIDE_PICK, "round": 2, "description": "Team A picks side for map 2"},
            {"team": "A", "action": VetoAction.PICK, "round": 3, "description": "Team A picks map 3"},
            {"team": "B", "action": VetoAction.SIDE_PICK, "round": 3, "description": "Team B picks side for map 3"},
            {"team": "B", "action": VetoAction.PICK, "round": 4, "description": "Team B picks map 4"},
            {"team": "A", "action": VetoAction.SIDE_PICK, "round": 4, "description": "Team A picks side for map 4"},
            {"team": "B", "action": VetoAction.SIDE_PICK, "round": 5, "description": "Team B picks side for map 5 (decider)"},
        ]
