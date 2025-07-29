from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="NewCampaignSession")


@_attrs_define
class NewCampaignSession:
    """
    Attributes:
        duration (int):
        label (str):
        split_size (float):
        reconciliation_username (Union[Unset, str]):
    """

    duration: int
    label: str
    split_size: float
    reconciliation_username: Union[Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        duration = self.duration

        label = self.label

        split_size = self.split_size

        reconciliation_username = self.reconciliation_username

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "duration": duration,
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

        label = d.pop("label")

        split_size = d.pop("splitSize")

        reconciliation_username = d.pop("reconciliationUsername", UNSET)

        new_campaign_session = cls(
            duration=duration,
            label=label,
            split_size=split_size,
            reconciliation_username=reconciliation_username,
        )

        return new_campaign_session
