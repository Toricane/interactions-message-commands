from interactions import Client
from typing import List, Tuple


def when_mentioned(bot: Client) -> List[str]:
    """
    Returns 2 bot mention strings in a list

    :param Client bot: Client instance

    ```py
    cmd = Commands(bot, when_mentioned(bot))
    ```
    """
    return [
        f"<@{bot.me.id}>",
        f"<@!{bot.me.id}>",
    ]


def when_mentioned_or(bot: Client, *prefixes: Tuple[str]) -> List[str]:
    """
    Returns 2 bot mention strings and provided prefixes in a list

    :param Client bot: Client instance
    :param Tuple[str] *prefixes: prefixes to be added to the list

    ```py
    cmd = Commands(bot, when_mentioned_or(bot, "!", "?"))
    ```
    """
    return when_mentioned(bot) + list(prefixes)
