import discord
from discord import app_commands
from discord.ext import commands
from lib.player_queue import PlayerContext

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
        if best_of not in [1, 3, 5]:
            best_of = 1
        player_count = PlayerContext.addPlayer(interaction.user, best_of)
        print(f"{player_count} players joined the queue")
        if player_count == 10:
            await PlayerContext.trigger_queue(best_of)
        _ = await interaction.response.send_message("You joined the queue!")


    @group.command(name="leave", description="Leave queue")
    async def leave(self, interaction: discord.Interaction):
        _ = await interaction.response.send_message("You left the queue!")
        PlayerContext.removePlayer(interaction.user.id)

async def setup(bot: commands.Bot):
    await bot.add_cog(Queue(bot))
