from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="UserSessionState")


@_attrs_define
class UserSessionState:
    """
    Attributes:
        enumname (bool):
    """

    enumname: bool

    def to_dict(self) -> dict[str, Any]:
        enumname = self.enumname

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "$enum$name": enumname,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enumname = d.pop("$enum$name")

        user_session_state = cls(
            enumname=enumname,
        )

        return user_session_state
