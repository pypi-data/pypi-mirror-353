from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="InputLabel")


@_attrs_define
class InputLabel:
    """
    Attributes:
        label (str):
    """

    label: str

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "label": label,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        input_label = cls(
            label=label,
        )

        return input_label
