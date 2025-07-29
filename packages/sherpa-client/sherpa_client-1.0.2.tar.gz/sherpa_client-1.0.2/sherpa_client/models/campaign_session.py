from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CampaignSession")


@_attrs_define
class CampaignSession:
    """
    Attributes:
        duration (int):
        id (str):
        label (str):
        split_size (float):
        reconciliation_username (Union[Unset, str]):
    """

    duration: int
    id: str
    label: str
    split_size: float
    reconciliation_username: Union[Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        duration = self.duration

        id = self.id

        label = self.label

        split_size = self.split_size

        reconciliation_username = self.reconciliation_username

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "duration": duration,
                "id": id,
                "label": label,
                "splitSize": split_size,
            }
        )
        if reconciliation_username is not UNSET:
            field_dict["reconciliationUsername"] = reconciliation_username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        duration = d.pop("duration")

        id = d.pop("id")

        label = d.pop("label")

        split_size = d.pop("splitSize")

        reconciliation_username = d.pop("reconciliationUsername", UNSET)

        campaign_session = cls(
            duration=duration,
            id=id,
            label=label,
            split_size=split_size,
            reconciliation_username=reconciliation_username,
        )

        return campaign_session
