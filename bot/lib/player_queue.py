from discord import Member, User
from bot.lib.db import db
from bot.lib.exceptions import BotException

PLAYER_REQUIRED = 1
class PlayerContext:
    users: dict[int, User | Member | None] = {}
    _best_of_1_ready: set[int] = {
        1419316584639369276, 1419317168817967145, 1419317384363249814,
        1419317623451025659, 1419317778325962802, 1419317955703083099,
        1419318214835437638, 1419318377251471565, 1419318576627712013
    }
    _best_of_1: list[int] = [
        1419316584639369276, 1419317168817967145, 1419317384363249814,
        1419317623451025659, 1419317778325962802, 1419317955703083099,
        1419318214835437638, 1419318377251471565, 1419318576627712013
    ]
    _best_of_3_ready: set[int] = set()
    _best_of_3: list[int] = []
    _best_of_5_ready: set[int] = set()
    _best_of_5: list[int] = []
    _user_id_to_best_of: dict[int, int] = {}


    @staticmethod
    def add_player(user: User | Member, bestof: int):
        if user.id in PlayerContext.users:
            old_bestof = PlayerContext._user_id_to_best_of.get(user.id)
            if old_bestof == bestof:
                raise BotException("PLAYER_ALREADY_IN_QUEUE")
            PlayerContext.removePlayer(user.id)
        
        db.DbServiceImpl.users.createOrFind(user)
        PlayerContext.users[user.id] = user
        PlayerContext._user_id_to_best_of[user.id] = bestof
        match bestof:
            case 1:
                PlayerContext._best_of_1.append(user.id)
                return len(PlayerContext._best_of_1)
            case 3:
                PlayerContext._best_of_3.append(user.id)
                return len(PlayerContext._best_of_3)
            case 5:
                PlayerContext._best_of_5.append(user.id)
                return len(PlayerContext._best_of_5)
            case _:
                raise BotException("INVALID_BESTOF")



    @staticmethod
    def _peek_current_batch_ids(bestOf: int):
        match bestOf:
            case 1:
                return PlayerContext._best_of_1[-PLAYER_REQUIRED:]
            case 3:
                return PlayerContext._best_of_3[-PLAYER_REQUIRED:]
            case 5:
                return PlayerContext._best_of_5[-PLAYER_REQUIRED:]
            case _:
                raise BotException("INVALID_BESTOF")



    @staticmethod
    def removePlayer(id: int):
        bestOf = PlayerContext._user_id_to_best_of.get(id)
        match bestOf:
            case 1:
                PlayerContext._removePlayerBo1(id)
            case 3:
                PlayerContext._removePlayerBo3(id)
            case 5:
                PlayerContext._removePlayerBo5(id)
            case _:
                raise BotException("INVALID_BESTOF")



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
        players = PlayerContext._best_of_1[-PLAYER_REQUIRED:]
        if len(players) < PLAYER_REQUIRED:
            raise BotException("NOT_ENOUGH_PLAYERS")
        _ = await PlayerContext.send_ready_check(players)
        PlayerContext._best_of_1 = PlayerContext._best_of_1[:-PLAYER_REQUIRED]


    @staticmethod
    async def _triggerQueueBo3():
        pass


    @staticmethod
    async def _triggerQueueBo5():
        pass


    @staticmethod
    def _removePlayerBo1(id: int):
        if id in PlayerContext._best_of_1:
            PlayerContext._best_of_1.remove(id)
        if id in PlayerContext._user_id_to_best_of:
            del PlayerContext._user_id_to_best_of[id]


    @staticmethod
    def _removePlayerBo3(id: int):
        if id in PlayerContext._best_of_3:
            PlayerContext._best_of_3.remove(id)
        if id in PlayerContext._user_id_to_best_of:
            del PlayerContext._user_id_to_best_of[id]


    @staticmethod
    def _removePlayerBo5(id: int):
        if id in PlayerContext._best_of_5:
            PlayerContext._best_of_5.remove(id)
        if id in PlayerContext._user_id_to_best_of:
            del PlayerContext._user_id_to_best_of[id]


    @staticmethod
    async def send_ready_check(playerIds: list[int]):
        for id in playerIds:
            user = PlayerContext.users[id]
            if user is None:
                PlayerContext.removePlayer(id)
                return

            _ = await user.send("Ready check!")


    @staticmethod
    async def set_player_as_ready(id: int):
        best_of = PlayerContext._user_id_to_best_of[id]
        match best_of:
            case 1:
                return await PlayerContext._set_player_as_ready_bo1(id)
            case 3:
                return await PlayerContext._set_player_as_ready_bo3(id)
            case 5:
                return await PlayerContext._set_player_as_ready_bo5(id)
            case _:
                raise BotException("PLAYER_NOT_ELIGIBLE")


    @staticmethod
    async def _set_player_as_ready_bo1(id: int):
        bestOf = 1
        playerIds = PlayerContext._peek_current_batch_ids(bestOf)
        if id not in playerIds:
            raise BotException("PLAYER_NOT_ELIGIBLE")
        if id in PlayerContext._best_of_1_ready:
            raise BotException("PLAYER_ALREADY_READY")

        PlayerContext._best_of_1_ready.add(id)
        return len(PlayerContext._best_of_1_ready)


    @staticmethod
    async def _set_player_as_ready_bo3(id: int):
        bestOf = 3
        playerIds = PlayerContext._peek_current_batch_ids(bestOf)
        if id not in playerIds:
            raise BotException("PLAYER_NOT_ELIGIBLE")
        if id in PlayerContext._best_of_3_ready:
            raise BotException("PLAYER_ALREADY_READY")

        PlayerContext._best_of_3_ready.add(id)
        return len(PlayerContext._best_of_3_ready)




    @staticmethod
    async def _set_player_as_ready_bo5(id: int):
        bestOf = 5
        playerIds = PlayerContext._peek_current_batch_ids(bestOf)
        if id not in playerIds:
            raise BotException("PLAYER_NOT_ELIGIBLE")
        if id in PlayerContext._best_of_5_ready:
            raise BotException("PLAYER_ALREADY_READY")

        PlayerContext._best_of_5_ready.add(id)
        return len(PlayerContext._best_of_5_ready)



    @staticmethod
    def status(user: User | Member):
        _ = user
        pass


    @staticmethod
    def list_players(bestOf: int):
        _ = bestOf
        pass


    @staticmethod
    def _find_best_of(id: int):
        return PlayerContext._user_id_to_best_of.get(id, 1)

    @staticmethod
    def find_best_of(id: int):
        return PlayerContext._find_best_of(id)

    @staticmethod
    def _find_ready_players(bestOf: int):
        batch = PlayerContext._peek_current_batch_ids(bestOf)
        match bestOf:
            case 1:
                ready = PlayerContext._best_of_1_ready
            case 3:
                ready = PlayerContext._best_of_3_ready
            case 5:
                ready = PlayerContext._best_of_5_ready
            case _:
                ready = set()
        return [pid for pid in batch if pid in ready]

    @staticmethod
    def find_ready_players(bestOf: int):
        return PlayerContext._find_ready_players(bestOf)

    @staticmethod
    async def create_match(player_ids: list[int], best_of: int):
        for pid in player_ids:
            user = PlayerContext.users.get(pid)
            if user:
                _ = await user.send(f"Match created! Best of {best_of}")
