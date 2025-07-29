from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GeneratedLabelHint")


@_attrs_define
class GeneratedLabelHint:
    """
    Attributes:
        label_hint (str):
    """

    label_hint: str

    def to_dict(self) -> dict[str, Any]:
        label_hint = self.label_hint

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "labelHint": label_hint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label_hint = d.pop("labelHint")

        generated_label_hint = cls(
            label_hint=label_hint,
        )

        return generated_label_hint
