import asyncio
import re
from typing import TypedDict
import discord
from discord import app_commands
from discord.ext import commands
from bot.lib.db.matches import MatchesServiceImpl
from bot.lib.db.teams import TeamsServiceImpl
from bot.lib.db.users import UsersServiceImpl
from bot.lib.log import log

class PendingScore(TypedDict):
    by: str
    score: str
    task: asyncio.Task[None]

pending_scores: dict[str, PendingScore] = {}

score_re = re.compile(r"^\s*(\d{1,2})\s*[-:]\s*(\d{1,2})\s*$")

def parse_score(s: str) -> tuple[int, int] | None:
    m = score_re.match(s)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))

async def _cleanup_after(match_id: str, delay: int = 30) -> None:
    await asyncio.sleep(delay)
    if match_id in pending_scores:
        log(f"Score pending expired for match {match_id}")
        pending_scores.pop(match_id, None)

class Game(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="game", description="Game related commands")

    @group.command(name="score", description="Submit game score as <t1>-<t2> in a match thread (captains only)")
    @app_commands.describe(score="Format like 13-9")
    async def score(self, interaction: discord.Interaction, score: str) -> None:
        try:
            thread_id = str(interaction.channel.id) if interaction.channel else None
            if not thread_id:
                await interaction.response.send_message("❌ This command can only be used in a match thread", ephemeral=True)
                return

            match = MatchesServiceImpl.find_by_thread_id(thread_id)
            if not match:
                await interaction.response.send_message("❌ No match found for this thread", ephemeral=True)
                return

            match_id = match["_id"]
            team1 = TeamsServiceImpl.find_by_id(match["team1"]) 
            team2 = TeamsServiceImpl.find_by_id(match["team2"]) 

            uid = str(interaction.user.id)
            t1_cap = UsersServiceImpl.find_by_id(team1["captainId"]).get("discordId")
            t2_cap = UsersServiceImpl.find_by_id(team2["captainId"]).get("discordId")
            if uid != t1_cap and uid != t2_cap:
                await interaction.response.send_message("❌ Only captains can submit score", ephemeral=True)
                return

            parsed = parse_score(score)
            if not parsed:
                await interaction.response.send_message("❌ Invalid score format. Use e.g. 13-9", ephemeral=True)
                return

            norm = f"{parsed[0]}-{parsed[1]}"

            existing = pending_scores.get(match_id)
            if not existing:
                pending_scores[match_id] = {"by": uid, "score": norm, "task": asyncio.create_task(_cleanup_after(match_id))}
                await interaction.response.send_message(f"📝 Score pending: {norm}. Waiting for the other captain (30s)...", ephemeral=True)
                return

            # Second submission
            if existing["by"] == uid:
                # overwrite and reset timer
                existing["score"] = norm
                if task := existing.get("task"):
                    task.cancel()
                existing["task"] = asyncio.create_task(_cleanup_after(match_id))
                await interaction.response.send_message(f"✏️ Updated pending score to {norm}. Waiting for the other captain (30s)...", ephemeral=True)
                return

            if existing["score"] == norm:
                # consensus reached
                if task := existing.get("task"):
                    task.cancel()
                pending_scores.pop(match_id, None)
                MatchesServiceImpl.set_score(match_id, parsed[0], parsed[1])
                await interaction.response.send_message(f"✅ Score confirmed: {norm}. Match finished.")
            else:
                # mismatch; reset to latest and wait again
                if task := existing.get("task"):
                    task.cancel()
                pending_scores[match_id] = {"by": uid, "score": norm, "task": asyncio.create_task(_cleanup_after(match_id))}
                await interaction.response.send_message("⚠️ Scores don't match. Latest submission recorded; waiting for other captain (30s)...", ephemeral=True)
        except Exception as e:
            log(f"Error handling /game score: {e}")
            await interaction.response.send_message("❌ Failed to submit score", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Game(bot))
