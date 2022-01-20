import functools
from inspect import _empty, signature, ismethod
from typing import Sequence

from .errors import (
    DuplicateAlias,
    DuplicateName,
)


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


def message(self, name: str = None, *, aliases: Sequence[str] = None) -> callable:
    """
    Decorator for creating a message-based command

    :param str name: The name of the command
    :param Sequence[str] aliases: The aliases of the command

    ```py
    @bot.message(name="ping")
    async def ping(ctx):
        await ctx.send("pong")
    ```
    """

    def inner(func):
        # gets func if it is a method
        old_func = func
        if ismethod(func):
            func = func.__func__
            func.__self__ = old_func.__self__
            func.__is_method__ = True
        else:
            func.__is_method__ = False
        func.__message_command__ = True

        # get name
        command_name = name or func.__name__

        # ignore self, ctx parameters
        if "." in func.__qualname__:  # is part of a class
            callback = functools.partial(func, None, None)
        else:
            callback = functools.partial(func, None)

        # get the parameters of the function
        params = signature(callback).parameters

        # organize parameters
        cmd_params = []
        for _name, param in params.items():
            cmd_param = CommandParameter(
                name=_name,
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
        if command_name in self.message_commands:
            raise DuplicateName(command_name)
        self.message_commands[command_name] = func

        # add any aliases if they are specified and are not in the commands dict
        if aliases is not None:
            for alias in aliases:
                if alias in self.message_commands:
                    raise DuplicateAlias(alias)
                self.message_commands[alias] = func

        return func

    return inner


def extension_message(name: str = None, *, aliases: Sequence[str] = None) -> callable:
    def inner(func):
        func.__message_command__ = True
        func.__message_command_data__ = (name, aliases)
        func.__params__ = None
        func.__cmd_params__ = None
        func.__is_method__ = ismethod(func)
        return func

    return inner
