from enum import Enum
from bot.lib.log import log


class VetoAction(Enum):
    BAN = "ban"
    PICK = "pick"
    SIDE_PICK = "side_pick"


class VetoPhase:
    
    def __init__(self, order: int, team_number: int, action: VetoAction) -> None:
        self.order = order
        self.team_number = team_number
        self.action = action
    
    def __repr__(self) -> str:
        return f"VetoPhase(order={self.order}, team={self.team_number}, action={self.action.value})"


class VetoSequenceBO3:
    PHASES = [
        VetoPhase(order=1, team_number=1, action=VetoAction.BAN),
        VetoPhase(order=2, team_number=2, action=VetoAction.BAN),
        VetoPhase(order=3, team_number=1, action=VetoAction.PICK),
        VetoPhase(order=4, team_number=2, action=VetoAction.SIDE_PICK),
        VetoPhase(order=5, team_number=2, action=VetoAction.PICK),
        VetoPhase(order=6, team_number=1, action=VetoAction.SIDE_PICK),
        VetoPhase(order=7, team_number=1, action=VetoAction.BAN),
        VetoPhase(order=8, team_number=2, action=VetoAction.BAN),
    ]


class VetoStateMachine:
    
    def __init__(self, match_id: str, best_of: int) -> None:
        self.match_id = match_id
        self.best_of = best_of
        self.current_order = 1
        self.banned_maps = set()
        self.picked_maps = []  # List of (team_number, map_id, order) tuples
        self.side_picks = {}  # Map of picked_map_id -> side
        self.is_complete = False
        
        if best_of == 3:
            self.sequence = VetoSequenceBO3.PHASES
        else:
            raise ValueError(f"BO{best_of} veto not implemented yet")
    
    def get_current_phase(self) -> VetoPhase | None:
        if self.is_complete or self.current_order > len(self.sequence):
            return None
        return self.sequence[self.current_order - 1]
    
    def get_available_maps(self, all_maps: list[dict]) -> list[dict]:
        banned_or_picked = self.banned_maps | set(m[1] for m in self.picked_maps)
        return [m for m in all_maps if m["_id"] not in banned_or_picked]
    
    def ban_map(self, map_id: str) -> bool:
        phase = self.get_current_phase()
        if not phase:
            log(f"Veto already complete for match {self.match_id}")
            return False
        
        if phase.action != VetoAction.BAN:
            log(f"Current phase is {phase.action.value}, not ban")
            return False
        
        if map_id in self.banned_maps:
            log(f"Map {map_id} already banned")
            return False
        
        self.banned_maps.add(map_id)
        self.current_order += 1
        log(f"Match {self.match_id}: Team {phase.team_number} banned map {map_id}")
        return True
    
    def pick_map(self, map_id: str) -> bool:
        phase = self.get_current_phase()
        if not phase:
            log(f"Veto already complete for match {self.match_id}")
            return False
        
        if phase.action != VetoAction.PICK:
            log(f"Current phase is {phase.action.value}, not pick")
            return False
        
        if map_id in self.banned_maps:
            log(f"Map {map_id} is banned")
            return False
        
        if any(m[1] == map_id for m in self.picked_maps):
            log(f"Map {map_id} already picked")
            return False
        
        self.picked_maps.append((phase.team_number, map_id, phase.order))
        self.current_order += 1
        log(f"Match {self.match_id}: Team {phase.team_number} picked map {map_id}")
        return True
    
    def pick_side(self, side: str) -> bool:
        phase = self.get_current_phase()
        if not phase:
            log(f"Veto already complete for match {self.match_id}")
            return False
        
        if phase.action != VetoAction.SIDE_PICK:
            log(f"Current phase is {phase.action.value}, not side_pick")
            return False
        
        if side not in ["ATK", "DEF"]:
            log(f"Invalid side: {side}")
            return False
        
        if not self.picked_maps:
            log("No map picked yet")
            return False
        
        last_picked_map_id = self.picked_maps[-1][1]
        self.side_picks[last_picked_map_id] = side
        self.current_order += 1
        log(f"Match {self.match_id}: Team {phase.team_number} chose {side} for map {last_picked_map_id}")
        return True
    
    def get_remaining_map(self, all_maps: list[dict]) -> dict | None:
        if not self.is_complete:
            log("Veto not complete yet")
            return None
        
        banned_or_picked = self.banned_maps | set(m[1] for m in self.picked_maps)
        remaining = [m for m in all_maps if m["_id"] not in banned_or_picked]
        
        if len(remaining) == 1:
            return remaining[0]
        return None
    
    def mark_complete(self) -> bool:
        if self.current_order > len(self.sequence):
            self.is_complete = True
            log(f"Match {self.match_id}: Veto complete")
            return True
        return False
    
    def get_state_summary(self) -> dict:
        phase = self.get_current_phase()
        return {
            "match_id": self.match_id,
            "best_of": self.best_of,
            "is_complete": self.is_complete,
            "current_order": self.current_order,
            "current_phase": phase,
            "banned_maps": list(self.banned_maps),
            "picked_maps": self.picked_maps,
            "side_picks": self.side_picks,
        }
