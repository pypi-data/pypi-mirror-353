from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="CampaignUserGroup")


@_attrs_define
class CampaignUserGroup:
    """
    Attributes:
        label (str):
        users (list[str]):
    """

    label: str
    users: list[str]

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        users = self.users

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "label": label,
                "users": users,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        users = cast(list[str], d.pop("users"))

        campaign_user_group = cls(
            label=label,
            users=users,
        )

        return campaign_user_group
