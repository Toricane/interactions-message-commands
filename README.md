# interactions-message-commands
Message commands extension for discord-py-interactions

# README IS NOT FINISHED YET BUT IT IS A GOOD START

## Installation
```
pip install -U interactions-message-commands
```

## Usage
Here is the example code for how to use message commands:
```py
import interactions
from interactions.ext.message_commands import MessageCommands, MessageContext

bot = interactions.Client(
    token="ODc0NzgwOTE4MDgxMDE1ODg5.YRL9Nw.Mm5m0gbQWkaaaj-e-U-T4pV4PlQ"
)
cmd = MessageCommands(bot, "!")


@cmd.message()
async def ping(ctx):
    await ctx.send("pong")


@cmd.message(name="hello")
async def hi(ctx: MessageContext, name: str):
    await ctx.send(f"Hello, {name}!")


bot.start()
```
First, you need to initialize your client.

Next, you need to initialize `MessageCommands()`.
- Multiple string prefixes in a list, tuple, or set is also allowed!

Then, you need to register your message commands.
- `@cmd.message()`: register a message command
    - Only keyword argument at the time is `name` to override function name
    - `name` is optional, if not specified, the function name will be used
    - In the function, `ctx` is required.
    - You can have as many arguments and keyword arguments as you want! `*args` is supported, but not `**kwargs`. However, `*,` is supported.

Finally, start the bot.

Use message commands in the Discord chat, and the bot will respond! 

Example: `!ping` or `!hello John`

There is also `when_mentioned()` and `when_mentioned_or()` for the prefix:
```py
from interactions.ext.message_commands import MessageCommands, when_mentioned_or

cmd = MessageCommands(bot, when_mentioned_or("!", "?"))
```
