import discord
from discord import app_commands
from discord.ext import commands
import random
from bot.lib.db.matches import MatchesServiceImpl
from bot.lib.db.teams import TeamsServiceImpl
from bot.lib.db.maps import MapsServiceImpl
from bot.lib.db.vetos import VetosServiceImpl
from bot.lib.db.users import UsersServiceImpl
from bot.lib.db.map_selections import MapSelectionsServiceImpl
from bot.lib.db.side_selections import SideSelectionsServiceImpl
from bot.lib.veto_manager import VetoStateMachine
from bot.lib.exceptions import handle_exception
from bot.lib.log import log

# Store veto state machines in memory (match_id -> VetoStateMachine)
veto_states = {}


class Map(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="map", description="Map related commands")

    @group.command(name="list", description="List available maps")
    async def list(self, interaction: discord.Interaction):
        try:
            active_maps = MapsServiceImpl.get_active_maps()
            map_list = "\n".join([f"• {m['name']}" for m in active_maps])
            await interaction.response.send_message(f"**Available Maps:**\n{map_list}")
        except Exception as e:
            await handle_exception(interaction, e)

    @group.command(name="ban", description="Ban a map")
    @app_commands.describe(map_name="Map to ban")
    async def ban(self, interaction: discord.Interaction, map_name: str):
        try:
            # Get match from thread
            thread_id = str(interaction.channel.id) if interaction.channel else None
            if not thread_id:
                await interaction.response.send_message("❌ This command can only be used in a match thread")
                return

            match = MatchesServiceImpl.find_by_thread_id(thread_id)
            if not match:
                await interaction.response.send_message("❌ No match found for this thread")
                return

            match_id = match["_id"]

            # Initialize or get veto state
            if match_id not in veto_states:
                veto_states[match_id] = VetoStateMachine(match_id, match["bestOf"])

            veto = veto_states[match_id]
            current_phase = veto.get_current_phase()

            if not current_phase:
                await interaction.response.send_message("❌ Veto phase is complete")
                return

            if current_phase.action.value != "ban":
                await interaction.response.send_message(f"❌ Current phase is {current_phase.action.value}, not ban")
                return

            # Verify captain
            team_id = match["team1"] if current_phase.team_number == 1 else match["team2"]
            team = TeamsServiceImpl.find_by_id(team_id)
            expected_captain_id = UsersServiceImpl.find_by_id(team["captainId"])["discordId"]
            user_id = str(interaction.user.id)

            if expected_captain_id != user_id:
                await interaction.response.send_message("❌ Only the team captain can ban maps")
                return

            # Get map
            map_obj = MapsServiceImpl.get_map_by_name(map_name.upper())
            if not map_obj:
                await interaction.response.send_message(f"❌ Map '{map_name}' not found")
                return

            # Ban the map
            if not veto.ban_map(map_obj["_id"]):
                await interaction.response.send_message("❌ Invalid ban action")
                return

            # Record in database
            veto_id = VetosServiceImpl.create(match_id, team_id, "ban", current_phase.order)
            MapSelectionsServiceImpl.create(veto_id, map_obj["_id"])

            next_phase = veto.get_current_phase()
            await interaction.response.send_message(
                f"✅ Team {current_phase.team_number} banned **{map_name.upper()}**\n\n"
                f"Next: Team {next_phase.team_number} - {next_phase.action.value.replace('_', ' ').title()}"
            )
        except Exception as e:
            await handle_exception(interaction, e)

    @group.command(name="pick", description="Pick a map or side")
    @app_commands.describe(map_name="Map to pick or side (ATK/DEF)")
    async def pick(self, interaction: discord.Interaction, map_name: str):
        try:
            # Get match from thread
            thread_id = str(interaction.channel.id) if interaction.channel else None
            if not thread_id:
                await interaction.response.send_message("❌ This command can only be used in a match thread")
                return

            match = MatchesServiceImpl.find_by_thread_id(thread_id)
            if not match:
                await interaction.response.send_message("❌ No match found for this thread")
                return

            match_id = match["_id"]

            # Initialize or get veto state
            if match_id not in veto_states:
                veto_states[match_id] = VetoStateMachine(match_id, match["bestOf"])

            veto = veto_states[match_id]
            current_phase = veto.get_current_phase()

            if not current_phase:
                await interaction.response.send_message("❌ Veto phase is complete")
                return

            # Verify captain
            team_id = match["team1"] if current_phase.team_number == 1 else match["team2"]
            team = TeamsServiceImpl.find_by_id(team_id)

            expected_captain_id = UsersServiceImpl.find_by_id(team["captainId"])["discordId"]
            user_id = str(interaction.user.id)

            if expected_captain_id != user_id:
                await interaction.response.send_message("❌ Only the team captain can ban maps")
                return

            # Handle side pick
            if current_phase.action.value == "side_pick":
                side = map_name.upper()
                if side not in ["ATK", "DEF"]:
                    await interaction.response.send_message("❌ Side must be ATK or DEF")
                    return

                if not veto.pick_side(side):
                    await interaction.response.send_message("❌ Invalid side pick action")
                    return

                veto_id = VetosServiceImpl.create(match_id, team_id, "side_pick", current_phase.order)
                SideSelectionsServiceImpl.create(veto_id, side)

                next_phase = veto.get_current_phase()
                if next_phase:
                    await interaction.response.send_message(
                        f"✅ Team {current_phase.team_number} chose **{side}**\n\n"
                        f"Next: Team {next_phase.team_number} - {next_phase.action.value.replace('_', ' ').title()}"
                    )
                else:
                    await interaction.response.send_message(f"✅ Team {current_phase.team_number} chose **{side}**\n\n🎮 Veto phase complete!")
                return

            # Handle map pick
            if current_phase.action.value != "pick":
                await interaction.response.send_message(f"❌ Current phase is {current_phase.action.value}, not pick")
                return

            map_obj = MapsServiceImpl.get_map_by_name(map_name.upper())
            if not map_obj:
                await interaction.response.send_message(f"❌ Map '{map_name}' not found")
                return

            if not veto.pick_map(map_obj["_id"]):
                await interaction.response.send_message("❌ Invalid map pick action")
                return

            veto_id = VetosServiceImpl.create(match_id, team_id, "pick", current_phase.order)
            MapSelectionsServiceImpl.create(veto_id, map_obj["_id"])

            next_phase = veto.get_current_phase()
            await interaction.response.send_message(
                f"✅ Team {current_phase.team_number} picked **{map_name.upper()}**\n\n"
                f"Next: Team {next_phase.team_number} - {next_phase.action.value.replace('_', ' ').title()}"
            )
        except Exception as e:
            await handle_exception(interaction, e)


async def setup(bot):
    await bot.add_cog(Map(bot))

