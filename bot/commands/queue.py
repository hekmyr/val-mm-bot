import discord
from discord import Interaction, app_commands
from discord.ext import commands
from bot.lib.player_queue import PLAYER_REQUIRED, PlayerContext
from bot.lib.log import log
from bot.lib.exceptions import handle_exception

class Queue(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    group: app_commands.Group = app_commands.Group(name="queue", description="Queue related commands")

    @group.command(name="join", description="Join queue")
    @app_commands.choices(best_of=[
        app_commands.Choice(name="1", value=1),
        app_commands.Choice(name="3", value=3),
        app_commands.Choice(name="5", value=5)
    ])
    async def join(self, interaction: discord.Interaction, best_of: int = 1):
        try:
            if best_of not in [1, 3, 5]:
                best_of = 1
            player_count = PlayerContext.add_player(interaction.user, best_of)
            log(f"{player_count} players joined the queue")
            if player_count <= PLAYER_REQUIRED:
                await PlayerContext.trigger_queue(best_of)
            _ = await interaction.response.send_message(f"You joined the queue! (Best of {best_of})")
        except Exception as e:
            await handle_exception(interaction, e)

    @group.command(name="ready", description="Mark as ready")
    async def ready(self, interaction: Interaction):
        try:
            player_count = await PlayerContext.set_player_as_ready(interaction.user.id)
            _ = await interaction.response.send_message("You have been marked as ready!")
            if player_count >= PLAYER_REQUIRED:
                best_of = PlayerContext.find_best_of(interaction.user.id)
                player_ids = PlayerContext.find_ready_players(best_of)
                await PlayerContext.send_ready_check(player_ids)
                await PlayerContext.create_match(player_ids, best_of)
        except Exception as e:
            await handle_exception(interaction, e)

    @group.command(name="leave", description="Leave queue")
    async def leave(self, interaction: discord.Interaction):
        try:
            PlayerContext.removePlayer(interaction.user.id)
            _ = await interaction.response.send_message("You left the queue!")
        except Exception as e:
            await handle_exception(interaction, e)

async def setup(bot: commands.Bot):
    await bot.add_cog(Queue(bot))
