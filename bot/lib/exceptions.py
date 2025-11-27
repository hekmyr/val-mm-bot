from bot.lib.log import log
import discord

class BotException(Exception):
    VALID_CODES = {
        "PLAYER_ALREADY_IN_QUEUE",
        "PLAYER_NOT_IN_QUEUE",
        "PLAYER_NOT_ELIGIBLE",
        "PLAYER_ALREADY_READY",
        "NOT_ENOUGH_PLAYERS",
        "INVALID_BESTOF",
        "BAD_PROJECT_CONFIGURATION",
        "FAILED_TO_SEND_READY_CHECK",
        "USER_NOT_FOUND",
    }

    ERROR_MESSAGES = {
        "PLAYER_ALREADY_IN_QUEUE": "You are already in this queue!",
        "PLAYER_NOT_IN_QUEUE": "You are not in any queue.",
        "PLAYER_NOT_ELIGIBLE": "You are not eligible for this action.",
        "PLAYER_ALREADY_READY": "You have already marked yourself as ready!",
        "NOT_ENOUGH_PLAYERS": "Not enough players in the queue.",
        "INVALID_BESTOF": "Invalid best of value.",
        "BAD_PROJECT_CONFIGURATION": "Bot configuration error. Please contact an admin.",
        "CHANNEL_ID_NOT_FOUND": "Match channel not found or not configured. Contact an admin.",
        "FAILED_TO_SEND_READY_CHECK": "Failed to send ready check. Please enable DMs from server members.",
        "USER_NOT_FOUND": "User not found in queue.",
    }

    def __init__(self, code: str) -> None:
        if code not in self.VALID_CODES:
            raise ValueError(f"Invalid error code: {code}")
        self.code = code
        super().__init__(code)

    def get_message(self) -> str:
        return self.ERROR_MESSAGES.get(self.code, "An error occurred.")


async def handle_exception(interaction: discord.Interaction, exception: Exception) -> None:
    match exception:
        case BotException() as bot_exc:
            message = bot_exc.get_message()
            log(bot_exc.code + ": " + message)
        case _:
            message = "An unexpected error has occurred. Please try again later."
            log(message)
            log(str(exception))
    
    await interaction.response.send_message(message, ephemeral=True)

def handle_exception2( exception: Exception) -> None:
    match exception:
        case BotException() as bot_exc:
            message = bot_exc.get_message()
            log(bot_exc.code + ": " + message)
        case _:
            message = "An unexpected error has occurred"
            log(message)
            log(str(exception))
    
