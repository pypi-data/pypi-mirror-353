from enum import Enum


class LocalizedMessageTemplating(str, Enum):
    JINJA2 = "jinja2"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
