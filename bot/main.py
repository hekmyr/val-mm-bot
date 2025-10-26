import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from bot.lib.exceptions import BotException

_ = load_dotenv(".env.local")

CONVEX_URL = os.getenv("CONVEX_URL")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(intents=intents, command_prefix="/")



@bot.event
async def on_ready():
    _ = await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

async def setup():
    await bot.load_extension("bot.commands.queue")
    await bot.load_extension("bot.commands.map")
    await bot.load_extension("bot.commands.leaderboard")

def validate():
    for var in [ CONVEX_URL, DISCORD_BOT_TOKEN ]:
        if not var:
            raise BotException("BAD_PROJECT_CONFIGURATION")

def main():
    asyncio.run(setup())
    if not DISCORD_BOT_TOKEN:
        raise BotException("BAD_PROJECT_CONFIGURATION")
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()
