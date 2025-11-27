import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from bot.lib.exceptions import BotException
from bot.lib.db.maps import MapsServiceImpl
from bot.lib.log import log

_ = load_dotenv(".env.local")

CONVEX_URL = os.getenv("CONVEX_URL")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_MATCH_THREAD_CHANNEL_ID = os.getenv("DISCORD_MATCH_THREAD_CHANNEL_ID")

intents = discord.Intents.default()
bot = commands.Bot(intents=intents, command_prefix="/")



@bot.event
async def on_ready() -> None:
    _ = await bot.tree.sync()
    log(f"✅ Logged in as {bot.user}")

async def setup() -> None:
    await bot.load_extension("bot.commands.queue")
    await bot.load_extension("bot.commands.map")
    await bot.load_extension("bot.commands.leaderboard")

def validate() -> None:
    for var in [ CONVEX_URL, DISCORD_BOT_TOKEN, DISCORD_MATCH_THREAD_CHANNEL_ID ]:
        if not var:
            raise BotException("BAD_PROJECT_CONFIGURATION")

def initialize_maps() -> None:
    isValid = MapsServiceImpl.validate()
    if not isValid:
        raise BotException("MAPS_VALIDATION_FAILED")

def main() -> None:
    validate()
    initialize_maps()
    asyncio.run(setup())
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()
