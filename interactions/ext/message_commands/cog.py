from asyncio import iscoroutinefunction
from inspect import getmembers
from interactions import Client, Extension
from .message_commands3 import message


class Extension(Extension):
    def __new__(cls, client: Client, *args, **kwargs):
        self = super().__new__(cls, client, *args, **kwargs)

        # get the methods
        for _name, func in getmembers(self, predicate=iscoroutinefunction):
            # if it is a message command:
            if hasattr(func, "__message_command__"):
                # register it using the decorator
                name, aliases = func.__message_command_data__
                message(self.bot, name, aliases=aliases)(func)

        return self

    def teardown(self):
        super().teardown()
        for name, func in getmembers(self, predicate=iscoroutinefunction):
            if name in self.client.message_commands and hasattr(
                func, "__message_command__"
            ):
                del self.client.message_commands[name]
