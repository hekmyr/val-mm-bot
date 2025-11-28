from .users import UsersServiceImpl
from .teams import TeamsServiceImpl
from .players import PlayersServiceImpl
from .matches import MatchesServiceImpl
from .vetos import VetosServiceImpl
from .map_selections import MapSelectionsServiceImpl
from .side_selections import SideSelectionsServiceImpl

class DbServiceImpl():
    users: UsersServiceImpl = UsersServiceImpl()
    teams: TeamsServiceImpl = TeamsServiceImpl()
    players: PlayersServiceImpl = PlayersServiceImpl()
    matches: MatchesServiceImpl = MatchesServiceImpl()
    vetos: VetosServiceImpl = VetosServiceImpl()
    map_selections: MapSelectionsServiceImpl = MapSelectionsServiceImpl()
    side_selections: SideSelectionsServiceImpl = SideSelectionsServiceImpl()

db = DbServiceImpl()
