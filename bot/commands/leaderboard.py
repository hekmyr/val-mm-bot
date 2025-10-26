import discord
from discord import app_commands
from discord.ext import commands

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="leaderboard", description="Leaderboad related commands")

    @group.command(name="alltime", description="View all-time leaderboard")
    async def alltime(self, interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon...")

    @group.command(name="seasonal", description="View seasonal leaderboard")
    async def pick(self, interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon...")

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
