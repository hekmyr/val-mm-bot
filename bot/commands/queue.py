import discord
from discord import Interaction, app_commands
from discord.ext import commands
from bot.lib.player_queue import PlayerContext
from bot.lib.constants import PLAYER_REQUIRED, READY_TIMEOUT
from bot.lib.log import log
from bot.lib.exceptions import handle_exception

class Queue(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        from bot.lib.player_queue import PlayerContext
        PlayerContext.bot = bot

    group: app_commands.Group = app_commands.Group(name="queue", description="Queue related commands")

    @group.command(name="join", description="Join queue")
    @app_commands.choices(best_of=[
        app_commands.Choice(name="1", value=1),
    ])
    async def join(self, interaction: discord.Interaction, best_of: int = 1) -> None:
        try:
            if best_of not in [1]:
                best_of = 1
 
            try:
                _ = await interaction.user.send("You will receive ready checks here, before the game start.")
            except discord.Forbidden:
                _ = await interaction.response.send_message("I cannot send you DMs. Please enable DMs from server members in your privacy settings.\nGo to Server Settings → Content & Social -> Social permissions -> Direct Messages",
                    ephemeral=True
                )
                return
            
            player_count = PlayerContext.add_player(interaction.user, best_of)
            log(f"{player_count} players in queue (Best of {best_of})")
            _ = await interaction.response.send_message(f"You joined the queue! ({player_count}/{PLAYER_REQUIRED} players)")
        except Exception as e:
            await handle_exception(interaction, e)

    @group.command(name="ready", description="Mark as ready")
    async def ready(self, interaction: Interaction) -> None:
        try:
            _ = await PlayerContext.set_player_as_ready(interaction.user.id)
            _ = await interaction.response.send_message(f"You have been marked as ready!\nThe game will start within {READY_TIMEOUT} seconds")
        except Exception as e:
            await handle_exception(interaction, e)

    @group.command(name="leave", description="Leave queue")
    async def leave(self, interaction: discord.Interaction) -> None:
        try:
            PlayerContext.removePlayer(interaction.user.id)
            _ = await interaction.response.send_message("You left the queue!")
        except Exception as e:
            await handle_exception(interaction, e)

    @group.command(name="status", description="Check your queue status")
    async def status(self, interaction: discord.Interaction) -> None:
        try:
            user_id = interaction.user.id
            if user_id not in PlayerContext.users:
                _ = await interaction.response.send_message("You are not in any queue.")
            else:
                best_of = PlayerContext._user_id_to_best_of.get(user_id)
                _ = await interaction.response.send_message(f"You are in the queue! (Best of {best_of})")
        except Exception as e:
            await handle_exception(interaction, e)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Queue(bot))
