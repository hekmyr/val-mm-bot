import os
import discord
from bot.lib.log import log

DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))
DISCORD_MATCH_THREAD_CHANNEL_ID = int(os.getenv("DISCORD_MATCH_THREAD_CHANNEL_ID", "0"))
DISCORD_MATCH_CATEGORY_ID = int(os.getenv("DISCORD_MATCH_CATEGORY_ID", "0"))


class DiscordService:
    
    @staticmethod
    async def create_match_thread(
        bot: discord.Client,
        team1_name: str,
        team2_name: str
    ) -> str | None:
        try:
            channel = await bot.fetch_channel(DISCORD_MATCH_THREAD_CHANNEL_ID)
            
            thread_name = f"{team1_name} vs {team2_name}"
            
            if isinstance(channel, discord.TextChannel):
                thread = await channel.create_thread(
                    name=thread_name,
                    auto_archive_duration=60
                )
            elif isinstance(channel, discord.ForumChannel):
                thread_with_message = await channel.create_thread(
                    name=thread_name,
                    content=f"Match thread for {team1_name} vs {team2_name}"
                )
                thread = thread_with_message.thread
            else:
                log(f"Invalid channel type for match thread: {type(channel)}")
                return None
            
            log(f"Match thread created: {thread_name} (ID: {thread.id})")
            return str(thread.id)
        except Exception as e:
            log(f"Error creating match thread: {e}")
            return None
    
    @staticmethod
    async def create_team_voice_channels(
        bot: discord.Client,
        team_name: str
    ) -> str | None:
        try:
            guild = await bot.fetch_guild(DISCORD_GUILD_ID)
            if not guild:
                log("Guild not found")
                return None

            category = await bot.fetch_channel(DISCORD_MATCH_CATEGORY_ID)
            if not isinstance(category, discord.CategoryChannel):
                log("Invalid category channel type")
                return None
            
            voice_channel = await guild.create_voice_channel(
                name=team_name,
                category=category
            )
            
            log(f"Team voice channel created: {team_name} (ID: {voice_channel.id})")
            return str(voice_channel.id)
        except Exception as e:
            log(f"Error creating team voice channel: {e}")
            return None
    
    @staticmethod
    async def post_match_info(
        bot: discord.Client,
        thread_id: str,
        team1_name: str,
        team1_captain_id: int,
        team2_name: str,
        team2_captain_id: int,
        player_list: dict[str, list[int]]
    ) -> None:
        try:
            thread = await bot.fetch_channel(int(thread_id))
            
            if not isinstance(thread, (discord.Thread, discord.TextChannel)):
                log(f"Invalid channel type for match thread: {type(thread)}")
                return

            # Format player mentions
            team1_mentions = ", ".join([f"<@{pid}>" for pid in player_list.get("team1", [])])
            team2_mentions = ", ".join([f"<@{pid}>" for pid in player_list.get("team2", [])])
            
            message = f"""
**MATCH INFORMATION**

🔵 **Team A: {team1_name}**
Captain: <@{team1_captain_id}>
Players: {team1_mentions}

🔴 **Team B: {team2_name}**
Captain: <@{team2_captain_id}>
Players: {team2_mentions}

Waiting for pick/ban phase to begin...
            """
            
            _ = await thread.send(message)
            log(f"Match info posted to thread {thread_id}")
        except Exception as e:
            log(f"Error posting match info: {e}")
    
    @staticmethod
    async def send_player_notifications(
        bot: discord.Client,
        player_ids: list[int],
        thread_id: str,
        team1_vc_id: str,
        team2_vc_id: str
    ) -> None:
        """Send DMs to all players with thread and voice channel links"""
        try:
            thread = await bot.fetch_channel(int(thread_id))
            team1_vc = await bot.fetch_channel(int(team1_vc_id))
            team2_vc = await bot.fetch_channel(int(team2_vc_id))
            
            if not isinstance(thread, (discord.Thread, discord.TextChannel)):
                log(f"Invalid thread type: {type(thread)}")
                return

            if not isinstance(team1_vc, discord.VoiceChannel) or not isinstance(team2_vc, discord.VoiceChannel):
                log("Invalid voice channel type")
                return

            for pid in player_ids:
                try:
                    user = await bot.fetch_user(pid)
                    message = f"""
Your match has been created!

📋 Match Thread: {thread.jump_url}
🎤 Team Voice Channels:
   - {team1_vc.mention}
   - {team2_vc.mention}

Join the thread and your team's voice channel!
                    """
                    _ = await user.send(message)
                except Exception as e:
                    log(f"Error sending DM to player {pid}: {e}")
        except Exception as e:
            log(f"Error sending player notifications: {e}")
