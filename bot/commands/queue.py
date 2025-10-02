import discord
from discord import app_commands
from discord.ext import commands

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="queue", description="Queue related commands")

    @group.command(name="join", description="Join queue")
    async def join(self, interaction: discord.Interaction):
        await interaction.response.send_message("You joined the queue!")

    @group.command(name="leave", description="Leave queue")
    async def leave(self, interaction: discord.Interaction):
        await interaction.response.send_message("You left the queue!")

async def setup(bot):
    await bot.add_cog(Queue(bot))
