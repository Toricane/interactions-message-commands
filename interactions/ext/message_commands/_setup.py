from interactions import Client
from .message_commands3 import MessageCommands, message
from types import MethodType


def setup(bot: Client) -> None:
    MessageCommands(bot)
    bot.message = MethodType(message, bot)

    bot.event(bot.process, "on_message_create")
