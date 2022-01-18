class MissingRequiredArgument(Exception):
    """Missing required arguments(s)"""

    def __init__(self):
        super().__init__("Missing required argument(s)")
