from discord import Member, User
from lib.db import db

PLAYER_REQUIRED = 1
class PlayerContext:
    users: dict[int, User | Member | None] = {}
    _bestOf1: list[int] = [ 1419316584639369276, 1419317168817967145, 1419317384363249814, 1419317623451025659, 1419317778325962802, 1419317955703083099, 1419318214835437638, 1419318377251471565, 1419318576627712013 ]
    _bestOf3: list[int] = []
    _bestOf5: list[int] = []
    _userIdToBestOf: dict[int, int] = {}


    @staticmethod
    def addPlayer(user: User | Member, bestof: int):
        if user.id not in PlayerContext.users:
            db.DbServiceImpl.users.createOrFind(user)
            PlayerContext.users[user.id] = user
            PlayerContext._userIdToBestOf[user.id] = bestof
            if bestof == 1:
                PlayerContext._bestOf1.append(user.id)
                return len(PlayerContext._bestOf1)
            elif bestof == 3:
                PlayerContext._bestOf3.append(user.id)
                return len(PlayerContext._bestOf3)
            elif bestof == 5:
                PlayerContext._bestOf5.append(user.id)
                return len(PlayerContext._bestOf5)


    @staticmethod
    def removePlayer(id: int):
        bestOf = PlayerContext._userIdToBestOf[id]
        match bestOf:
            case 1:
                PlayerContext._removePlayerBo1(id)
            case 3:
                PlayerContext._removePlayerBo3(id)
            case 5:
                PlayerContext._removePlayerBo5(id)
            case _:
                raise ValueError("INVALID_BESTOF")


    @staticmethod
    async def trigger_queue(bestOf: int):
        match bestOf:
            case 1:
                await PlayerContext._triggerQueueBo1()
            case 3:
                await PlayerContext._triggerQueueBo3()
            case 5:
                await PlayerContext._triggerQueueBo5()
            case _:
                await PlayerContext._triggerQueueBo1()


    @staticmethod
    async def _triggerQueueBo1():
        players = PlayerContext._bestOf1[-PLAYER_REQUIRED:]
        if len(players) < PLAYER_REQUIRED:
            raise Exception("NOT_ENOUGH_PLAYERS")
        _ = await PlayerContext.send_ready_check(players)
        PlayerContext._bestOf1 = PlayerContext._bestOf1[:-PLAYER_REQUIRED]


    @staticmethod
    async def _triggerQueueBo3():
        pass


    @staticmethod
    async def _triggerQueueBo5():
        pass


    @staticmethod
    def _removePlayerBo1(id: int):
        if id in PlayerContext._bestOf1:
            PlayerContext._bestOf1.remove(id)
        if id in PlayerContext._userIdToBestOf:
            del PlayerContext._userIdToBestOf[id]


    @staticmethod
    def _removePlayerBo3(id: int):
        if id in PlayerContext._bestOf3:
            PlayerContext._bestOf3.remove(id)
        if id in PlayerContext._userIdToBestOf:
            del PlayerContext._userIdToBestOf[id]


    @staticmethod
    def _removePlayerBo5(id: int):
        if id in PlayerContext._bestOf5:
            PlayerContext._bestOf5.remove(id)
        if id in PlayerContext._userIdToBestOf:
            del PlayerContext._userIdToBestOf[id]


    @staticmethod
    async def send_ready_check(playerIds: list[int]):
        for id in playerIds:
            user = PlayerContext.users[id]
            if user is None:
                PlayerContext.removePlayer(id)
                return

            _ = await user.send("Ready check!")

    @staticmethod
    def status(user: User | Member):
        _ = user
        pass


    @staticmethod
    def list(bestOf: int):
        _ = bestOf
        pass
