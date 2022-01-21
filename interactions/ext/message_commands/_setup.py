from interactions import Client
from .message_commands import MessageCommands
from .decor import message
from .prefixes import when_mentioned, when_mentioned_or
from types import MethodType


def setup(bot: Client) -> None:
    MessageCommands(bot)
    bot.message = MethodType(message, bot)
    bot.when_mentioned = MethodType(when_mentioned, bot)
    bot.when_mentioned_or = MethodType(when_mentioned_or, bot)
