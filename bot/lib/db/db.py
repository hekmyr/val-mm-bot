from .users import UsersServiceImpl
from .teams import TeamsServiceImpl
from .players import PlayersServiceImpl
from .matches import MatchesServiceImpl
from .vetos import VetosServiceImpl

class DbServiceImpl():
    users: UsersServiceImpl = UsersServiceImpl()
    teams: TeamsServiceImpl = TeamsServiceImpl()
    players: PlayersServiceImpl = PlayersServiceImpl()
    matches: MatchesServiceImpl = MatchesServiceImpl()
    vetos: VetosServiceImpl = VetosServiceImpl()

db = DbServiceImpl()
