from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="CampaignRolesChange")


@_attrs_define
class CampaignRolesChange:
    """
    Attributes:
        added_roles (list[str]):
        remove_current_funtional_roles (bool):
        removed_roles (list[str]):
        username (str):
    """

    added_roles: list[str]
    remove_current_funtional_roles: bool
    removed_roles: list[str]
    username: str

    def to_dict(self) -> dict[str, Any]:
        added_roles = self.added_roles

        remove_current_funtional_roles = self.remove_current_funtional_roles

        removed_roles = self.removed_roles

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "addedRoles": added_roles,
                "removeCurrentFuntionalRoles": remove_current_funtional_roles,
                "removedRoles": removed_roles,
                "username": username,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        added_roles = cast(list[str], d.pop("addedRoles"))

        remove_current_funtional_roles = d.pop("removeCurrentFuntionalRoles")

        removed_roles = cast(list[str], d.pop("removedRoles"))

        username = d.pop("username")

        campaign_roles_change = cls(
            added_roles=added_roles,
            remove_current_funtional_roles=remove_current_funtional_roles,
            removed_roles=removed_roles,
            username=username,
        )

        return campaign_roles_change
