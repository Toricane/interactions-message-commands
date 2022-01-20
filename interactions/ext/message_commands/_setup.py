from __future__ import annotations
from interactions import Client
from .message_commands2 import message, logic, process
from types import MethodType
from typing import Sequence, Union


def setup(bot: Client, prefix: Union[Sequence[str], str]) -> None:
    """
    Apply hooks to a bot to add additional features
    This function is required, as importing alone won't extend the classes
    """
    bot.message = MethodType(message, bot)
    bot.logic = MethodType(logic, bot)
    bot.process = MethodType(process, bot)

    bot.prefix = prefix
    bot.__commands__ = {}

    bot.event(bot.process, "on_message_create")
