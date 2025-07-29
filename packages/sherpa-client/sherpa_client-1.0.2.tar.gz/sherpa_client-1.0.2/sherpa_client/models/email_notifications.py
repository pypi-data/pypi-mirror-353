from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailNotifications")


@_attrs_define
class EmailNotifications:
    """
    Attributes:
        enabled (bool):
        notified_users (Union[Unset, list[str]]):
    """

    enabled: bool
    notified_users: Union[Unset, list[str]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        notified_users: Union[Unset, list[str]] = UNSET
        if not isinstance(self.notified_users, Unset):
            notified_users = self.notified_users

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "enabled": enabled,
            }
        )
        if notified_users is not UNSET:
            field_dict["notifiedUsers"] = notified_users

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled")

        notified_users = cast(list[str], d.pop("notifiedUsers", UNSET))

        email_notifications = cls(
            enabled=enabled,
            notified_users=notified_users,
        )

        return email_notifications
