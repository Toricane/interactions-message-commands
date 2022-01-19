import functools
from inspect import _empty, signature
from interactions import Client
from shlex import split
from typing import List, Set, Tuple, Union, Sequence

from .errors import MissingRequiredArgument, DuplicateAlias, DuplicateName
from .context import MessageContext


class CommandParameter:
    """A parameter in a function"""

    def __init__(
        self,
        name: str,
        type: str,
        variable,
        optional: bool = False,
        input=None,
        default=None,
    ):
        self.name = name
        self.type = type
        self.variable = variable
        self.optional = optional
        self.input = input
        self.default = default

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}, type={self.type}, variable={self.variable}, optional={self.optional}, input={self.input}>"


async def process(self, msg) -> None:
    """Processes a message and runs the corresponding command if it matches the prefix"""
    # if message is from a bot, ignore it
    if msg.author.bot:
        return

    # see if the message starts with the prefix, and execute self.logic()
    if isinstance(self.prefix, str) and msg.content.startswith(self.prefix):
        await self.logic(msg)
    elif isinstance(self.prefix, (tuple, list, set)):
        for prefix in self.prefix:
            if msg.content.startswith(prefix):
                return await self.logic(msg, prefix)


async def logic(self, msg, prefix=None):
    """The logic for finding and running a command"""
    prefix: Union[List[str], Tuple[str], Set[str]] = (
        self.prefix if prefix is None else prefix
    )  # sets up the prefix
    content: List[str] = split(msg.content)  # splits the message into arguments

    # check if it is a mention prefix or a prefix with spaces and uncuts the first argument
    if content[0] == prefix:
        content.pop(0)
    else:
        content[0] = content[0][len(prefix) :]

    # check if the command exists
    if all(content[0] != key for key in self.__commands__):
        return

    # get required data for MessageContext
    message = msg._json
    member = msg.member._json
    user = msg.author._json
    channel = await self.http.get_channel(msg.channel_id)
    guild = await self.http.get_guild(msg.guild_id)

    for i in [message, member, user, channel, guild]:
        i.pop("_client", None)

    ctx = MessageContext(
        self.http,
        message=message,
        member=member,
        user=user,
        channel=channel,
        guild=guild,
    )

    func = self.__commands__[content[0]]  # get the corresponding function

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
    return await func(ctx, *(ctx.args + ctx._args), **ctx.kwargs)


def message(self, _name: str = None, *, aliases: Sequence[str] = None) -> callable:
    """
    Decorator for creating a message-based command

    :param str _name: The name of the command
    :param Sequence[str] aliases: The aliases of the command

    ```py
    @bot.message(name="ping")
    async def ping(ctx):
        await ctx.send("pong")
    ```
    """

    def inner(func):
        # get name
        command_name = _name or func.__name__

        # ignore self, ctx parameters
        if "." in func.__qualname__:  # is part of a class
            callback = functools.partial(func, None, None)
        else:
            callback = functools.partial(func, None)

        # get the parameters of the function
        params = signature(callback).parameters

        # organize parameters
        cmd_params = []
        for name, param in params.items():
            cmd_param = CommandParameter(
                name=name,
                type=param.annotation,
                variable=param,
                optional=param.default is not _empty,
                input=param.default,
                default=param.default,
            )
            cmd_params.append(cmd_param)

        # save parameters to function
        func.__params__ = params
        func.__cmd_params__ = cmd_params

        # add the function to the commands dict if it doesn't exist
        if command_name in self.__commands__:
            raise DuplicateName(command_name)
        self.__commands__[command_name] = func

        # add any aliases if they are specified and are not in the commands dict
        if aliases is not None:
            for alias in aliases:
                if alias in self.__commands__:
                    raise DuplicateAlias(alias)
                self.__commands__[alias] = func

        return func

    return inner
