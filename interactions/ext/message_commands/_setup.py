from interactions import Client
from .message_commands3 import MessageCommands
from types import MethodType
from typing import Sequence, Union


def setup(bot: Client) -> None:
    MessageCommands(bot)
    bot.event(bot.process, "on_message_create")
