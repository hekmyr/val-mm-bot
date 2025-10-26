import discord
from discord import app_commands
from discord.ext import commands

class Map(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="map", description="Map related commands")

    @group.command(name="list", description="List available maps")
    async def list(self, interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon...")

    @group.command(name="pick", description="Pick a map")
    async def pick(self, interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon...")

    @group.command(name="ban", description="Ban a map")
    async def ban(self, interaction: discord.Interaction):
        await interaction.response.send_message("Coming soon...")

async def setup(bot):
    await bot.add_cog(Map(bot))
