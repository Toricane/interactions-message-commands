from inspect import _empty, iscoroutinefunction
from interactions import Client, Extension
from shlex import split
from typing import List, Optional, Set, Tuple, Union, Sequence, Coroutine

from .errors import (
    MissingRequiredArgument,
    NoPrefixProvided,
)
from .context import MessageContext


class MessageCommands(Extension):
    def __init__(self, bot: Client):
        self.bot = bot
        self.bot.message_commands = {}

        prefix: Optional[Union[Sequence[str], str, Coroutine]] = None
        self.bot.prefix = prefix

        self.bot.event(self.process, "on_message_create")

    async def process(self, msg) -> None:
        """Processes a message and runs the corresponding command if it matches the prefix"""
        print("process")
        # if no prefix, error
        if not self.bot.prefix:
            raise NoPrefixProvided

        if iscoroutinefunction(self.bot.prefix):
            print("coroutine?")
            message = msg._json
            member = msg.member._json
            user = msg.author._json
            channel = await self.bot.http.get_channel(msg.channel_id)
            guild = await self.bot.http.get_guild(msg.guild_id)

            for i in [message, member, user, channel, guild]:
                i.pop("_client", None)

            ctx = MessageContext(
                self.bot.http,
                message=message,
                member=member,
                user=user,
                channel=channel,
                guild=guild,
            )

            prefix = await self.bot.prefix(ctx)

            if msg.content.startswith(prefix):
                await self.logic(msg, prefix, context=ctx)

            return

        # if message is from a bot, ignore it
        if msg.author.bot:
            return

        # see if the message starts with the prefix, and execute self.logic()
        if isinstance(self.bot.prefix, str) and msg.content.startswith(self.bot.prefix):
            await self.logic(msg, self.bot.prefix)
        elif isinstance(self.bot.prefix, (tuple, list, set)):
            for prefix in self.bot.prefix:
                if msg.content.startswith(prefix):
                    print("prefix", prefix)
                    return await self.logic(msg, prefix)

    async def logic(
        self,
        msg,
        prefix: Union[Sequence[str], str],
        context: Optional[MessageContext] = None,
    ) -> None:
        """The logic for finding and running a command"""
        print("logic", context)
        prefix: Union[List[str], Tuple[str], Set[str]] = prefix
        print("prefix", prefix)
        content: List[str] = split(msg.content)  # splits the message into arguments
        print("before", content)

        # check if it is a mention prefix or a prefix with spaces and uncuts the first argument
        if content[0] == prefix:
            print("if")
            content.pop(0)
        else:
            print("else", len(prefix))
            content[0] = content[0][len(prefix) :]
        print(content)

        # check if the command exists
        if all(content[0] != key for key in self.bot.message_commands):
            print("self.bot.message_commands", self.bot.message_commands)
            print("does not exist")
            return

        # get required data for MessageContext
        if not context:
            print("no context")
            message = msg._json
            member = msg.member._json
            user = msg.author._json
            print(self.bot.http.cache.channels.get(str(msg.channel_id)) or [])
            print(self.bot.http.cache.guilds.get(str(msg.guild_id)) or [])
            channel = (
                self.bot.http.cache.channels.get(str(msg.channel_id))
                or await self.bot.http.get_channel(msg.channel_id)
            )._json
            guild = (
                self.bot.http.cache.guilds.get(str(msg.guild_id))
                or await self.bot.http.get_guild(msg.guild_id)
            )._json

            for i in [message, member, user, channel, guild]:
                i.pop("_client", None)

            ctx = MessageContext(
                self.bot.http,
                message=message,
                member=member,
                user=user,
                channel=channel,
                guild=guild,
            )
        else:
            print("yes context")
            ctx = context

        func: callable = self.bot.message_commands[
            content[0]
        ]  # get the corresponding function

        # get the saved parameters of the function
        params = func.__params__
        cmd_params = func.__cmd_params__

        # add user input to parameters
        needed_params = {}
        for cmd_param, c in zip(cmd_params, content[1:]):
            if cmd_param.input in {None, _empty} or cmd_param.input and c:
                if cmd_param.variable.kind in {
                    cmd_param.variable.VAR_POSITIONAL,
                    cmd_param.variable.KEYWORD_ONLY,
                }:  # if it is *args or keyword only
                    index = content.index(c)
                    _args = content[index:]
                    cmd_param.input = " ".join(_args)
                else:
                    cmd_param.input = c
            needed_params[cmd_param.name] = cmd_param.input

        # get the required number of parameters in the function
        required_params = [
            param
            for _, param in params.items()
            if param.kind in {param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD}
        ]

        # raises if there are not enough parameters
        if len(required_params) > len(needed_params):
            raise MissingRequiredArgument

        ctx.args = [  # arguments for the function
            arg.input
            for arg in cmd_params
            if arg.variable.kind
            in {arg.variable.POSITIONAL_OR_KEYWORD, arg.variable.POSITIONAL_ONLY}
        ]
        ctx.kwargs = {  # keyword arguments for the function
            kwarg.name: kwarg.input
            for kwarg in cmd_params
            if kwarg.variable.kind == kwarg.variable.KEYWORD_ONLY
        }
        ctx._args = [  # *args for the function
            arg.input
            for arg in cmd_params
            if arg.variable.kind == arg.variable.VAR_POSITIONAL
        ]
        ctx.all_kwargs = needed_params  # all arguments as keyword arguments

        # call the function
        if func.__is_method__:
            return await func(func.__self__, ctx, *(ctx.args + ctx._args), **ctx.kwargs)
        else:
            return await func(ctx, *(ctx.args + ctx._args), **ctx.kwargs)
