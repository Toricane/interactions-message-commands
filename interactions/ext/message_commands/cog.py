from asyncio import iscoroutinefunction
from inspect import getmembers
import interactions
from interactions import Client, Extension
from .decor import message


class Extension(Extension):
    def __new__(cls, client: Client, *args, **kwargs):
        self = super().__new__(cls, client, *args, **kwargs)

        # get the methods
        for _name, func in getmembers(self, predicate=iscoroutinefunction):
            # if it is a message command:
            if hasattr(func, "__message_command__"):
                # register it using the decorator
                name, aliases = func.__message_command_data__
                message(client, name, aliases=aliases)(func)

        return self

    def teardown(self):
        super().teardown()
        for name, func in getmembers(self, predicate=iscoroutinefunction):
            if (
                hasattr(func, "__message_command__")
                and name in self.client.message_commands
            ):
                del self.client.message_commands[name]


interactions.Extension = Extension
