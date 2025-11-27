from bot.lib.constants import PLAYER_REQUIRED, READY_TIMEOUT
import asyncio
import os
import discord
from discord import Member, User
from bot.lib.exceptions import BotException
from bot.lib.log import log
from bot.lib.mock import MockUser, MockReady
from bot.lib.test_constants import TEST_USER_IDS
from bot.lib.match_creator import MatchCreator

class PlayerContext:
    bot: discord.Client | None = None
    users: dict[int, User | Member | None] = {uid: MockUser(uid) for uid in TEST_USER_IDS}
    _best_of_1_ready: set[int] = set(TEST_USER_IDS)
    _best_of_1: list[int] = TEST_USER_IDS.copy()
    _user_id_to_best_of: dict[int, int] = {}
    _active_ready_checks: dict[int, asyncio.Task[None]] = {}

    @staticmethod
    def get_user_best_of(user_id: int) -> int | None:
        return PlayerContext._user_id_to_best_of.get(user_id)

    @staticmethod
    def add_player(user: User | Member, bestof: int) -> int:
        if user.id in PlayerContext.users:
            old_bestof = PlayerContext.get_user_best_of(user.id)
            if old_bestof == bestof:
                raise BotException("PLAYER_ALREADY_IN_QUEUE")
            PlayerContext.removePlayer(user.id)

        PlayerContext.users[user.id] = user
        PlayerContext._user_id_to_best_of[user.id] = bestof
        match bestof:
            case 1:
                PlayerContext._best_of_1.append(user.id)
                player_count = len(PlayerContext._best_of_1)
            case _:
                raise BotException("INVALID_BESTOF")

        if player_count == PLAYER_REQUIRED:
            _ = asyncio.create_task(PlayerContext.trigger_queue(bestof))

        return player_count

    @staticmethod
    def _peek_current_batch_ids(bestOf: int) -> list[int]:
        match bestOf:
            case 1:
                return PlayerContext._best_of_1[-PLAYER_REQUIRED:]
            case _:
                raise BotException("INVALID_BESTOF")

    @staticmethod
    def removePlayer(id: int) -> None:
        bestOf = PlayerContext._user_id_to_best_of.get(id)
        match bestOf:
            case 1:
                PlayerContext._removePlayerBo1(id)
            case _:
                raise BotException("INVALID_BESTOF")

    @staticmethod
    async def trigger_queue(bestOf: int) -> None:
        match bestOf:
            case 1:
                await PlayerContext._triggerQueueBo1()
            case _:
                await PlayerContext._triggerQueueBo1()

    @staticmethod
    async def _triggerQueueBo1() -> None:
        players = PlayerContext._best_of_1[-PLAYER_REQUIRED:]
        if len(players) < PLAYER_REQUIRED:
            raise BotException("NOT_ENOUGH_PLAYERS")

        log(f"Queue pop! Sending ready checks to {len(players)} players (Best of 1)")
        await PlayerContext.send_ready_check(players)

        task = asyncio.create_task(PlayerContext._ready_timeout(1, players))
        PlayerContext._active_ready_checks[1] = task

    @staticmethod
    async def _ready_timeout(bestof: int, player_ids: list[int]) -> None:
        await asyncio.sleep(READY_TIMEOUT)

        # MOCK: Auto-mark test users as ready for testing
        MockReady.auto_ready_mock_users(bestof)

        ready_set = PlayerContext._get_ready_set(bestof)
        not_ready = [pid for pid in player_ids if pid not in ready_set]

        if not not_ready:
            log(f"All {len(player_ids)} players ready! Creating match (Best of {bestof})")
            ready_set.clear()
            match bestof:
                case 1:
                    PlayerContext._best_of_1 = PlayerContext._best_of_1[:-PLAYER_REQUIRED]
                case _:
                    raise BotException("INVALID_BESTOF")
            await PlayerContext.create_match(player_ids, bestof)
        else:
            log(f"Ready timeout! {len(not_ready)} players not ready (Best of {bestof})")
            for pid in not_ready:
                user = PlayerContext.users.get(pid)
                if user:
                    try:
                        _ = await user.send("You were not ready in time and have been removed from the queue.")
                    except:
                        pass
                PlayerContext.removePlayer(pid)

            ready_set.clear()

            remaining_queue = PlayerContext._peek_current_batch_ids(bestof)
            if len(remaining_queue) >= PLAYER_REQUIRED:
                log(f"Retriggering queue for Best of {bestof} with {len(remaining_queue)} remaining players")
                await PlayerContext.trigger_queue(bestof)

    @staticmethod
    def _get_ready_set(bestof: int) -> set[int]:
        match bestof:
            case 1:
                return PlayerContext._best_of_1_ready
            case _:
                return set[int]()

    @staticmethod
    def _removePlayerBo1(id: int) -> None:
        if id in PlayerContext._best_of_1:
            PlayerContext._best_of_1.remove(id)
        if id in PlayerContext._user_id_to_best_of:
            del PlayerContext._user_id_to_best_of[id]
        if id in PlayerContext.users:
            del PlayerContext.users[id]

    @staticmethod
    async def send_ready_check(playerIds: list[int]) -> None:
        for id in playerIds:
            log(f"Sending ready check to player {id}")
            user = PlayerContext.users[id]
            if user is not None:
                try:
                    _ = await user.send("Ready check! Type `/queue ready` within 30 seconds to confirm.")
                except Exception as e:
                    raise BotException("FAILED_TO_SEND_READY_CHECK") from e
            else:
                raise BotException("USER_NOT_FOUND")

    @staticmethod
    async def set_player_as_ready(id: int) -> int:
        best_of = PlayerContext._user_id_to_best_of.get(id)
        if best_of is None:
            raise BotException("PLAYER_NOT_IN_QUEUE")

        match best_of:
            case 1:
                return await PlayerContext._set_player_as_ready_bo1(id)
            case _:
                raise BotException("PLAYER_NOT_ELIGIBLE")

    @staticmethod
    async def _set_player_as_ready_bo1(id: int) -> int:
        bestOf = 1
        playerIds = PlayerContext._peek_current_batch_ids(bestOf)
        if id not in playerIds:
            raise BotException("PLAYER_NOT_ELIGIBLE")
        if id in PlayerContext._best_of_1_ready:
            raise BotException("PLAYER_ALREADY_READY")

        PlayerContext._best_of_1_ready.add(id)
        return len(PlayerContext._best_of_1_ready)

    @staticmethod
    def status(user: User | Member) -> None:
        _ = user
        pass

    @staticmethod
    def list_players(bestOf: int) -> None:
        _ = bestOf
        pass

    @staticmethod
    def _find_best_of(id: int) -> int:
        return PlayerContext._user_id_to_best_of.get(id, 1)

    @staticmethod
    def find_best_of(id: int) -> int:
        return PlayerContext._find_best_of(id)

    @staticmethod
    def _find_ready_players(bestOf: int) -> list[int]:
        batch = PlayerContext._peek_current_batch_ids(bestOf)
        ready = set[int]()
        match bestOf:
            case 1:
                ready = PlayerContext._best_of_1_ready
            case _:
                pass
        return [pid for pid in batch if pid in ready]

    @staticmethod
    def find_ready_players(bestOf: int) -> list[int]:
        return PlayerContext._find_ready_players(bestOf)

    @staticmethod
    async def create_match(discord_ids: list[int], best_of: int) -> None:

        log(f"Creating match with {len(discord_ids)} players (Best of {best_of})")

        team1_name, team2_name = MatchCreator.generate_team_names()
        team1_ids, team2_ids = MatchCreator.balance_teams(discord_ids)
        team1_captain_did, team2_captain_did = MatchCreator.pick_captains(team1_ids, team2_ids)
        team_a_first_pick = MatchCreator.decide_first_pick()

        log(f"Teams: {team1_name} vs {team2_name}")
        log(f"Captains: {team1_captain_did} vs {team2_captain_did}")
        log(f"First pick: {'Team A' if team_a_first_pick else 'Team B'}")

        try:
            discord_id_to_user_dto = MatchCreator.fetch_user_dtos(discord_ids)
            team1_captain_dto = MatchCreator.resolve_captain_dto(
                team1_captain_did,
                team1_ids,
                discord_id_to_user_dto
            )
            team2_captain_dto = MatchCreator.resolve_captain_dto(
                team2_captain_did,
                team2_ids,
                discord_id_to_user_dto
            )
            team1_id, team2_id = MatchCreator.create_teams_in_db(
                team1_name,
                team2_name,
                team1_captain_dto,
                team2_captain_dto,
                team_a_first_pick
            )
            match_db_id = MatchCreator.create_match_record_and_initial_vetos(
                team1_id,
                team2_id,
                best_of
            )
            MatchCreator.add_players_to_teams(
                team1_ids,
                team2_ids,
                discord_id_to_user_dto,
                team1_id,
                team2_id
            )

            if PlayerContext.bot:
                channel_id = int(os.getenv("DISCORD_MATCH_THREAD_CHANNEL_ID", "0"))
                thread_url = await MatchCreator.create_and_populate_thread(
                    PlayerContext.bot,
                    channel_id,
                    team1_name,
                    team2_name,
                    team1_ids,
                    team2_ids,
                    PlayerContext.users,
                    team1_captain_did,
                    team2_captain_did,
                    team_a_first_pick,
                    match_db_id
                )

                category_id = int(os.getenv("DISCORD_MATCH_CATEGORY_ID", "0"))
                await MatchCreator.create_voice_channels(
                    PlayerContext.bot,
                    category_id,
                    team1_name,
                    team2_name,
                    match_db_id
                )

                await MatchCreator.notify_players(
                    discord_ids,
                    PlayerContext.users,
                    best_of,
                    team1_name,
                    team2_name,
                    thread_url
                )
            else:
                log("PlayerContext.bot is None, skipping Discord operations")
        except Exception as e:
            log(f"Error during match creation: {e}")
            raise BotException("MATCH_CREATION_FAILED") from e
