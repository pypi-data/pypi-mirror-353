from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="MetadataDefinitionEntry")


@_attrs_define
class MetadataDefinitionEntry:
    """
    Attributes:
        distinct_metadata_values (list[str]):
        is_editable (bool):
        is_multiple (bool):
        metadata_name (str):
    """

    distinct_metadata_values: list[str]
    is_editable: bool
    is_multiple: bool
    metadata_name: str

    def to_dict(self) -> dict[str, Any]:
        distinct_metadata_values = self.distinct_metadata_values

        is_editable = self.is_editable

        is_multiple = self.is_multiple

        metadata_name = self.metadata_name

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "distinctMetadataValues": distinct_metadata_values,
                "isEditable": is_editable,
                "isMultiple": is_multiple,
                "metadataName": metadata_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        distinct_metadata_values = cast(list[str], d.pop("distinctMetadataValues"))

        is_editable = d.pop("isEditable")

        is_multiple = d.pop("isMultiple")

        metadata_name = d.pop("metadataName")

        metadata_definition_entry = cls(
            distinct_metadata_values=distinct_metadata_values,
            is_editable=is_editable,
            is_multiple=is_multiple,
            metadata_name=metadata_name,
        )

        return metadata_definition_entry
