import random
import asyncio
import discord

from bot.lib.db.db import db
from bot.lib.db.maps import MapsServiceImpl
from bot.lib.db.users import UserDto
from bot.lib.exceptions import BotException
from bot.lib.log import log
from bot.lib.team_balancer import TeamBalancer
from bot.lib.mock import MockTeamBalancer


class MatchCreator:

    @staticmethod
    def generate_team_names() -> tuple[str, str]:
        return (TeamBalancer.generate_team_name(), TeamBalancer.generate_team_name())

    @staticmethod
    def balance_teams(discord_ids: list[int]) -> tuple[list[int], list[int]]:
        try:
            return TeamBalancer.balance_teams(discord_ids)
        except Exception:
            return MockTeamBalancer.balance_teams_mock(discord_ids)

    @staticmethod
    def pick_captains(team1_ids: list[int], team2_ids: list[int]) -> tuple[int, int]:
        try:
            c1 = TeamBalancer.pick_captain(team1_ids)
            c2 = TeamBalancer.pick_captain(team2_ids)
            return c1, c2
        except Exception:
            return MockTeamBalancer.pick_captain_mock(team1_ids), MockTeamBalancer.pick_captain_mock(team2_ids)

    @staticmethod
    def decide_first_pick() -> bool:
        try:
            return bool(random.choice([True, False]))
        except Exception:
            return True

    @staticmethod
    def fetch_user_dtos(discord_ids: list[int]) -> dict[int, UserDto]:
        result: dict[int, UserDto] = {}
        for did in discord_ids:
            try:
                user_dto = db.users.find_by_discord_id(did)
                if user_dto:
                    result[did] = user_dto
                else:
                    log(f"User DTO not found for Discord ID: {did}")
                    raise BotException("USER_NOT_FOUND")
            except Exception:
                    log(f"User DTO not found for Discord ID: {did}")
                    raise BotException("USER_NOT_FOUND")
        return result

    @staticmethod
    def resolve_captain_dto(
        captain_did: int, team_player_ids: list[int], discord_id_to_user_dto: dict[int, UserDto]
    ) -> UserDto:
        captain_dto = discord_id_to_user_dto.get(captain_did)
        if captain_dto:
            return captain_dto

        for did in team_player_ids:
            dto = discord_id_to_user_dto.get(did)
            if dto:
                return dto

        raise BotException("FAILED_TO_RESOLVE_CAPTAIN")

    @staticmethod
    def create_teams_in_db(
        team1_name: str,
        team2_name: str,
        team1_captain_user_dto: UserDto,
        team2_captain_user_dto: UserDto,
        team_a_first_pick: bool,
    ) -> tuple[str, str]:
        try:
            team1_db_id = db.teams.create(
                name=team1_name, captain_id=team1_captain_user_dto["_id"], has_first_pick=team_a_first_pick
            )
            team2_db_id = db.teams.create(
                name=team2_name, captain_id=team2_captain_user_dto["_id"], has_first_pick=not team_a_first_pick
            )
            log(f"Teams saved to DB: {team1_db_id} vs {team2_db_id}")
            return team1_db_id, team2_db_id
        except Exception as e:
            log(f"Error creating teams in DB: {e}")
            raise BotException("FAILED_TO_CREATE_TEAMS") from e

    @staticmethod
    def create_match_record_and_initial_vetos(team1_db_id: str, team2_db_id: str, best_of: int) -> str:
        try:
            match_db_id = db.matches.create(team1_db_id, team2_db_id, best_of)
            log(f"Match saved to DB: {match_db_id}")

            if best_of == 1 and match_db_id and team1_db_id:
                try:
                    active_maps = MapsServiceImpl.get_active_maps()
                    if not active_maps:
                        raise BotException("NO_ACTIVE_MAPS")
                    selected = random.choice(active_maps)
                    _ = db.vetos.create(match_db_id, team1_db_id, "decider", 1)
                    log(f"BO1 decider selected: {selected.get('name')} (mapId={selected.get('_id')})")
                except BotException:
                    raise
                except Exception as e:
                    log(f"Failed to select map or create veto: {e}")
                    raise BotException("FAILED_TO_SELECT_MAP") from e

            return match_db_id
        except Exception as e:
            log(f"Error creating match record: {e}")
            raise BotException("FAILED_TO_CREATE_MATCH") from e

    @staticmethod
    def add_players_to_teams(
        team1_player_ids: list[int],
        team2_player_ids: list[int],
        discord_id_to_user_dto: dict[int, UserDto],
        team1_db_id: str,
        team2_db_id: str,
    ) -> None:
        try:
            for did in team1_player_ids:
                dto = discord_id_to_user_dto.get(did)
                if dto:
                    _ = db.players.create(team_id=team1_db_id, user_id=dto["_id"])
            for did in team2_player_ids:
                dto = discord_id_to_user_dto.get(did)
                if dto:
                    _ = db.players.create(team_id=team2_db_id, user_id=dto["_id"])
        except Exception as e:
            log(f"Error adding players to teams: {e}")
            raise BotException("FAILED_TO_ADD_PLAYERS_TO_TEAMS") from e

    @staticmethod
    def format_roster_mentions(player_ids: list[int], users_map: dict[int, discord.User | discord.Member | None], captain_id: int) -> list[str]:
        roster: list[str] = []
        for did in player_ids:
            member = users_map.get(did)
            if not member:
                mention = f"<@{did}>"
                roster.append(mention + (" 👑" if did == captain_id else ""))
                continue
            captain_marker = " 👑" if did == captain_id else ""
            if hasattr(member, "mention"):
                roster.append(f"{member.mention}{captain_marker}")
            else:
                roster.append(f"<@{did}>{captain_marker}")
        return roster

    @staticmethod
    async def create_and_populate_thread(
        bot_client: discord.Client,
        channel_id: int,
        team1_name: str,
        team2_name: str,
        team1_player_ids: list[int],
        team2_player_ids: list[int],
        users_map: dict[int, discord.User | discord.Member | None],
        team1_captain_did: int,
        team2_captain_did: int,
        team_a_first_pick: bool,
        match_db_id: str | None,
    ) -> str | None:
        if channel_id <= 0:
            log("DISCORD_MATCH_THREAD_CHANNEL_ID not set; skipping thread creation")
            return None

        try:
            channel = bot_client.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await bot_client.fetch_channel(channel_id)
                except Exception:
                    channel = None
            if channel is None or not isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
                log("Configured DISCORD_MATCH_THREAD_CHANNEL_ID not found or invalid type")
                return None

            match_id_short = match_db_id[:6] if match_db_id else "XXXXXX"
            thread_name = f"{team1_name} vs {team2_name} (BO{1 if team1_player_ids or team2_player_ids else 1}) | MATCH ID: {match_id_short}"

            if isinstance(channel, discord.TextChannel):
                thread = await channel.create_thread(name=thread_name, type=discord.ChannelType.private_thread, invitable=False)
            else:
                thread_with_message = await channel.create_thread(name=thread_name, content="Match thread")
                thread = thread_with_message.thread

            thread_url = f"https://discord.com/channels/{channel.guild.id}/{thread.id}"

            try:
                if bot_client.user:
                    await thread.add_user(bot_client.user)
            except Exception as e:
                log(f"Could not add bot to thread: {e}")

            for did in list(users_map.keys()):
                member = users_map.get(did)
                if isinstance(member, (discord.User, discord.Member)):
                    try:
                        await thread.add_user(member)
                    except Exception:
                        pass

            try:
                team1_roster = MatchCreator.format_roster_mentions(team1_player_ids, users_map, team1_captain_did)
                team2_roster = MatchCreator.format_roster_mentions(team2_player_ids, users_map, team2_captain_did)
                first_pick_team = team1_name if team_a_first_pick else team2_name
                match_message = (
                    f"# 🎮 Match Started!\n"
                    + f"## Best of 1\n\n"
                    + f"### **{team1_name}**\n" + "\n".join(team1_roster) + "\n\n"
                    + f"### **{team2_name}**\n" + "\n".join(team2_roster) + "\n\n"
                    + f"**First Pick:** {first_pick_team}\n"
                    + f"**Match ID:** `{match_id_short}`"
                )
                _ = await thread.send(match_message)
            except Exception as e:
                log(f"Error posting match details to thread: {e}")

            if match_db_id:
                try:
                    db.matches.update_thread_id(match_db_id, str(thread.id))
                except Exception as e:
                    log(f"Failed to save thread id: {e}")

            return thread_url
        except Exception as e:
            log(f"Error creating private thread: {e}")
            return None

    @staticmethod
    async def create_voice_channels(
        bot_client: discord.Client,
        category_id: int,
        team1_name: str,
        team2_name: str,
        match_db_id: str | None,
    ) -> None:
        if category_id <= 0:
            log("DISCORD_MATCH_CATEGORY_ID not set; skipping voice channel creation")
            return

        try:
            category = bot_client.get_channel(category_id)
            if category is None:
                try:
                    category = await bot_client.fetch_channel(category_id)
                except Exception:
                    category = None

            if not category or not isinstance(category, discord.CategoryChannel):
                log("Category channel not found or invalid type")
                return

            team1_voice = await category.guild.create_voice_channel(name=f"{team1_name}", category=category)
            team2_voice = await category.guild.create_voice_channel(name=f"{team2_name}", category=category)
            common_voice = await category.guild.create_voice_channel(name=f"Common Chat | {team1_name} | {team2_name}", category=category)

            log(f"Created voice channels: {team1_voice.id}, {team2_voice.id}, {common_voice.id}")

            async def delete_voice_channels() -> None:
                await asyncio.sleep(2 * 60 * 60)
                try:
                    await team1_voice.delete(reason="Match ended - 2 hour limit")
                    await team2_voice.delete(reason="Match ended - 2 hour limit")
                    await common_voice.delete(reason="Match ended - 2 hour limit")
                    log(f"Deleted voice channels for match {match_db_id}")
                except Exception as e:
                    log(f"Error deleting voice channels: {e}")

            _ = asyncio.create_task(delete_voice_channels())
        except Exception as e:
            log(f"Error creating voice channels: {e}")

    @staticmethod
    async def notify_players(discord_ids: list[int], users_map: dict[int, discord.User | discord.Member | None], best_of: int, team1_name: str, team2_name: str, thread_url: str | None) -> None:
        for did in discord_ids:
            user = users_map.get(did)
            if user:
                try:
                    message = f"Match created! Best of {best_of}\nTeam A: {team1_name}\nTeam B: {team2_name}"
                    if thread_url:
                        message += f"\n\nJoin the match thread: {thread_url}"
                    _ = await user.send(message)
                except Exception:
                    pass
