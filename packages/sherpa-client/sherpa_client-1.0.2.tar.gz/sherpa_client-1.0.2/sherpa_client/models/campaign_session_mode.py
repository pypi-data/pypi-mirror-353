from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CampaignSessionMode")


@_attrs_define
class CampaignSessionMode:
    """
    Attributes:
        id (str):
        label (str):
        open_functional_roles (Union[Unset, list[str]]):
        started_functional_roles (Union[Unset, list[str]]):
    """

    id: str
    label: str
    open_functional_roles: Union[Unset, list[str]] = UNSET
    started_functional_roles: Union[Unset, list[str]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        label = self.label

        open_functional_roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.open_functional_roles, Unset):
            open_functional_roles = self.open_functional_roles

        started_functional_roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.started_functional_roles, Unset):
            started_functional_roles = self.started_functional_roles

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "label": label,
            }
        )
        if open_functional_roles is not UNSET:
            field_dict["openFunctionalRoles"] = open_functional_roles
        if started_functional_roles is not UNSET:
            field_dict["startedFunctionalRoles"] = started_functional_roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        label = d.pop("label")

        open_functional_roles = cast(list[str], d.pop("openFunctionalRoles", UNSET))

        started_functional_roles = cast(
            list[str], d.pop("startedFunctionalRoles", UNSET)
        )

        campaign_session_mode = cls(
            id=id,
            label=label,
            open_functional_roles=open_functional_roles,
            started_functional_roles=started_functional_roles,
        )

        return campaign_session_mode
