from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CategoryId")


@_attrs_define
class CategoryId:
    """
    Attributes:
        identifier (str):
    """

    identifier: str

    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "identifier": identifier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identifier = d.pop("identifier")

        category_id = cls(
            identifier=identifier,
        )

        return category_id
