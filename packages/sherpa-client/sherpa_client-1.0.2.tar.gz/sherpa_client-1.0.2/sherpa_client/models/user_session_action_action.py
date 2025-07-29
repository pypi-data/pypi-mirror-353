from enum import Enum


class UserSessionActionAction(str, Enum):
    ADD_EXTRA_TIME = "add_extra_time"
    CLOSE = "close"
    CREATE = "create"
    OPEN = "open"
    PAUSE = "pause"
    START = "start"
    STOP = "stop"

    def __str__(self) -> str:
        return str(self.value)
