from typing import Any
from bot.lib.constants import PLAYER_REQUIRED, READY_TIMEOUT
import asyncio
import random
import os
import discord
from discord import Member, User
from bot.lib.db.db import db
from bot.lib.db.maps import MapsServiceImpl
from bot.lib.db.map_selections import MapSelectionsServiceImpl
from bot.lib.exceptions import BotException, handle_exception2
from bot.lib.log import log
from bot.lib.team_balancer import TeamBalancer
from bot.lib.mock import MockUser, MockTeamBalancer, MockReady
from bot.lib.test_constants import TEST_USER_IDS

PLAYER_REQUIRED = 10
READY_TIMEOUT = 30

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
    def add_player(user: User | Member, bestof: int):
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
    def _peek_current_batch_ids(bestOf: int):
        match bestOf:
            case 1:
                return PlayerContext._best_of_1[-PLAYER_REQUIRED:]
            case _:
                raise BotException("INVALID_BESTOF")

    @staticmethod
    def removePlayer(id: int):
        bestOf = PlayerContext._user_id_to_best_of.get(id)
        match bestOf:
            case 1:
                PlayerContext._removePlayerBo1(id)
            case _:
                raise BotException("INVALID_BESTOF")

    @staticmethod
    async def trigger_queue(bestOf: int):
        match bestOf:
            case 1:
                await PlayerContext._triggerQueueBo1()
            case _:
                await PlayerContext._triggerQueueBo1()

    @staticmethod
    async def _triggerQueueBo1():
        players = PlayerContext._best_of_1[-PLAYER_REQUIRED:]
        if len(players) < PLAYER_REQUIRED:
            raise BotException("NOT_ENOUGH_PLAYERS")

        log(f"Queue pop! Sending ready checks to {len(players)} players (Best of 1)")
        await PlayerContext.send_ready_check(players)

        task = asyncio.create_task(PlayerContext._ready_timeout(1, players))
        PlayerContext._active_ready_checks[1] = task

    @staticmethod
    async def _ready_timeout(bestof: int, player_ids: list[int]):
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
    def _get_ready_set(bestof: int):
        match bestof:
            case 1:
                return PlayerContext._best_of_1_ready
            case _:
                return set[int]()

    @staticmethod
    def _removePlayerBo1(id: int):
        if id in PlayerContext._best_of_1:
            PlayerContext._best_of_1.remove(id)
        if id in PlayerContext._user_id_to_best_of:
            del PlayerContext._user_id_to_best_of[id]
        if id in PlayerContext.users:
            del PlayerContext.users[id]

    @staticmethod
    async def send_ready_check(playerIds: list[int]):
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
    async def set_player_as_ready(id: int):
        best_of = PlayerContext._user_id_to_best_of.get(id)
        if best_of is None:
            raise BotException("PLAYER_NOT_IN_QUEUE")

        match best_of:
            case 1:
                return await PlayerContext._set_player_as_ready_bo1(id)
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
            case _:
                ready = set()
        return [pid for pid in batch if pid in ready]

    @staticmethod
    def find_ready_players(bestOf: int):
        return PlayerContext._find_ready_players(bestOf)

    @staticmethod
    async def create_match(discord_ids: list[int], best_of: int):

        log(f"Creating match with {len(discord_ids)} players (Best of {best_of})")

        # Generate team names
        team1_name = TeamBalancer.generate_team_name()
        team2_name = TeamBalancer.generate_team_name()

        # MOCK: Balance teams - MOCK VERSION
        team1_player_ids, team2_player_ids = MockTeamBalancer.balance_teams_mock(discord_ids)

        # Original: team1_player_ids, team2_player_ids = TeamBalancer.balance_teams(player_ids)

        # MOCK: Pick captains - MOCK VERSION
        team1_captain_did = MockTeamBalancer.pick_captain_mock(team1_player_ids)
        team2_captain_did = MockTeamBalancer.pick_captain_mock(team2_player_ids)

        # team1_captain_id = TeamBalancer.pick_captain(team1_player_ids)
        # team2_captain_id = TeamBalancer.pick_captain(team2_player_ids)

        # MOCK: Random first pick - MOCK VERSION
        team_a_first_pick = MockTeamBalancer.get_first_pick_mock()
        # Original: team_a_first_pick = random.choice([True, False])

        log(f"Teams: {team1_name} vs {team2_name}")
        log(f"Captains: {team1_captain_did} vs {team2_captain_did}")
        log(f"First pick: {'Team A' if team_a_first_pick else 'Team B'}")

        discord_id_to_user_dto: dict[int, Any] = {}
        for did in discord_ids:
            user = PlayerContext.users.get(did)
            if user:
                try:
                    user_dto = db.users.find_by_discord_id(user.id)
                    discord_id_to_user_dto[did] = user_dto
                except Exception as e:
                    raise BotException(f"USER_NOT_FOUND")

        try:
            team1_captain_user_dto = discord_id_to_user_dto.get(team1_captain_did)
            if not team1_captain_user_dto:
                # Use first available player from team1
                for did in team1_player_ids:
                    if did in discord_id_to_user_dto.discordId:
                        team1_captain_user_dto = discord_id_to_user_dto[did]
                        break
            
            team2_captain_user_dto = discord_id_to_user_dto.get(team2_captain_did)
            if not team2_captain_user_dto:
                # Use first available player from team2
                for did in team2_player_ids:
                    if did in discord_id_to_user_dto:
                        team2_captain_user_dto = discord_id_to_user_dto[did]
                        break
            
            team1_db_id = db.teams.create(
                name=team1_name,
                captain_id=team1_captain_user_dto.id,
                has_first_pick=team_a_first_pick
            )
            team2_db_id = db.teams.create(
                name=team2_name,
                captain_id=team2_captain_user_dto.id,
                has_first_pick=not team_a_first_pick
            )
            log(f"Teams saved to DB: {team1_db_id} vs {team2_db_id}")
        except Exception as e:
            raise BotException("FAILED_TO_CREATE_TEAMS") from e

        try:
            match_db_id = db.matches.create(
                team1_id=team1_db_id,
                team2_id=team2_db_id,
                best_of=best_of
            )
            log(f"Match saved to DB: {match_db_id}")

            selected_map = None
            if best_of == 1 and match_db_id and team1_db_id:
                try:
                    active_maps = MapsServiceImpl.get_active_maps()
                    selected_map = random.choice(active_maps)
                    log(f"BO1 decider selected: {selected_map['name']} (mapId={selected_map['_id']})")
                except Exception as e:
                    raise BotException("FAILED_TO_SELECT_MAP") from e
        except Exception as e:
            raise BotException("FAILED_TO_CREATE_MATCH") from e

        # TODO: Can't we create our teams with players directly?
        try:
            for did in team1_player_ids:
                if did in discord_id_to_user_dto:
                    db.players.create(
                        team_id=team1_db_id,
                        user_id=discord_id_to_user_dto[did]
                    )
            for did in team2_player_ids:
                if did in discord_id_to_user_dto:
                    db.players.create(
                        team_id=team2_db_id,
                        user_id=discord_id_to_user_dto[did]
                    )
        except Exception as e:
            raise BotException("FAILED_TO_ADD_PLAYERS_TO_TEAMS") from e

        thread_url = None
        try:
            channel_id = int(os.getenv("DISCORD_MATCH_THREAD_CHANNEL_ID", "0"))
            if channel_id == 0:
                log("DISCORD_MATCH_THREAD_CHANNEL_ID is not set; skipping thread creation")
            else:
                bot_client = PlayerContext.bot
                if isinstance(bot_client, discord.Client):
                    channel = bot_client.get_channel(channel_id)
                    if channel is None:
                        try:
                            channel = await bot_client.fetch_channel(channel_id)
                        except Exception:
                            channel = None
                    if channel and isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
                        match_id_short = match_db_id[:6] if match_db_id else "XXXXXX"
                        thread_name = f"{team1_name} vs {team2_name} (BO{best_of}) | MATCH ID: {match_id_short}"
                        if isinstance(channel, discord.TextChannel):
                            # Create a private thread from the channel
                            thread = await channel.create_thread(
                                name=thread_name,
                                type=discord.ChannelType.private_thread,
                                invitable=False
                            )
                        else:
                            # Forum: create a post directly as thread
                            thread = await channel.create_thread(name=thread_name, content="Match thread")
                        
                        # Store thread URL for notifications
                        thread_url = f"https://discord.com/channels/{channel.guild.id}/{thread.id}"
                        
                        # Add bot to thread (for private threads)
                        try:
                            if isinstance(thread, discord.Thread) and bot_client.user:
                                await thread.add_user(bot_client.user)
                        except Exception as e:
                            log(f"Could not add bot to thread: {e}")
                        
                        # Add members
                        for did in discord_ids:
                            member = PlayerContext.users.get(did)
                            if isinstance(member, (discord.User, discord.Member)):
                                try:
                                    await thread.add_user(member)
                                except Exception:
                                    pass
                        
                        # Post match details in the thread
                        try:
                            # Build team rosters with mentions
                            team1_roster = []
                            for did in team1_player_ids:
                                member = PlayerContext.users.get(did)
                                if member:
                                    captain_marker = " 👑" if did == team1_captain_did else ""
                                    # Handle both real Discord users and MockUsers
                                    if hasattr(member, 'mention'):
                                        team1_roster.append(f"{member.mention}{captain_marker}")
                                    else:
                                        team1_roster.append(f"<@{did}>{captain_marker}")
                            
                            team2_roster = []
                            for did in team2_player_ids:
                                member = PlayerContext.users.get(did)
                                if member:
                                    captain_marker = " 👑" if did == team2_captain_did else ""
                                    # Handle both real Discord users and MockUsers
                                    if hasattr(member, 'mention'):
                                        team2_roster.append(f"{member.mention}{captain_marker}")
                                    else:
                                        team2_roster.append(f"<@{did}>{captain_marker}")
                            
                            first_pick_team = team1_name if team_a_first_pick else team2_name
                            map_line = f"**Map:** {selected_map['name']}" if selected_map else ""
                            
                            match_message = f"""# 🎮 Match Started!
## Best of {best_of}

### **{team1_name}**
{chr(10).join(team1_roster)}

### **{team2_name}**
{chr(10).join(team2_roster)}

**First Pick:** {first_pick_team}
{map_line}
**Match ID:** `{match_id_short}`"""
                            
                            await thread.send(match_message)
                        except Exception as e:
                            log(f"Error posting match details to thread: {e}")
                        
                        # Persist thread ID
                        try:
                            await db.matches.update_thread_id(match_db_id, str(thread.id))
                        except Exception as e:
                            log(f"Failed to save thread id: {e}")
                        
                        # Create voice channels for the match
                        try:
                            category_id = int(os.getenv("DISCORD_MATCH_CATEGORY_ID", "0"))
                            if category_id > 0 and channel.guild:
                                category = bot_client.get_channel(category_id)
                                if category is None:
                                    try:
                                        category = await bot_client.fetch_channel(category_id)
                                    except Exception:
                                        category = None
                                
                                if category and isinstance(category, discord.CategoryChannel):
                                    # Create team voice channels
                                    team1_voice = await channel.guild.create_voice_channel(
                                        name=f"{team1_name}",
                                        category=category
                                    )
                                    team2_voice = await channel.guild.create_voice_channel(
                                        name=f"{team2_name}",
                                        category=category
                                    )
                                    common_voice = await channel.guild.create_voice_channel(
                                        name=f"Common Chat | {team1_name} | {team2_name}",
                                        category=category
                                    )
                                    
                                    log(f"Created voice channels: {team1_voice.id}, {team2_voice.id}, {common_voice.id}")
                                    
                                    # Schedule automatic deletion after 2 hours
                                    async def delete_voice_channels():
                                        await asyncio.sleep(2 * 60 * 60)  # 2 hours
                                        try:
                                            await team1_voice.delete(reason="Match ended - 2 hour limit")
                                            await team2_voice.delete(reason="Match ended - 2 hour limit")
                                            await common_voice.delete(reason="Match ended - 2 hour limit")
                                            log(f"Deleted voice channels for match {match_id_short}")
                                        except Exception as e:
                                            log(f"Error deleting voice channels: {e}")
                                    
                                    _ = asyncio.create_task(delete_voice_channels())
                                    
                                    # Post voice channel links in thread
                                    voice_message = f"\n\n**Voice Channels:**\n{team1_voice.mention}\n{team2_voice.mention}\n{common_voice.mention}"
                                    await thread.send(voice_message)
                                else:
                                    log("Category channel not found or invalid")
                            else:
                                log("DISCORD_MATCH_CATEGORY_ID not set; skipping voice channel creation")
                        except Exception as e:
                            log(f"Error creating voice channels: {e}")
                    else:
                        log("Configured DISCORD_MATCH_THREAD_CHANNEL_ID not found or invalid type")
                else:
                    log("Discord client not available to create thread")
        except Exception as e:
            log(f"Error creating private thread: {e}")

        # Notify players
        for did in discord_ids:
            user = PlayerContext.users.get(did)
            if user:
                try:
                    message = f"Match created! Best of {best_of}\nTeam A: {team1_name}\nTeam B: {team2_name}"
                    if thread_url:
                        message += f"\n\nJoin the match thread: {thread_url}"
                    _ = await user.send(message)
                except:
                    pass
