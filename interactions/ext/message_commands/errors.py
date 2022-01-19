class MessageCommandError(Exception):
    """Base class for all message command errors"""


class MissingRequiredArgument(MessageCommandError):
    """Missing required arguments(s)"""

    def __init__(self):
        super().__init__("Missing required argument(s)")


class DuplicateName(MessageCommandError):
    """Duplicate command name"""

    def __init__(self, name):
        super().__init__(f"Duplicate name: {name}")


class DuplicateAlias(MessageCommandError):
    """Duplicate alias"""

    def __init__(self, alias):
        super().__init__(f"Duplicate alias: {alias}")
