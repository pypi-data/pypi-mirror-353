from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.metadata_definition_entry import MetadataDefinitionEntry


T = TypeVar("T", bound="MetadataDefinition")


@_attrs_define
class MetadataDefinition:
    """
    Attributes:
        metadata (list['MetadataDefinitionEntry']):
    """

    metadata: list["MetadataDefinitionEntry"]

    def to_dict(self) -> dict[str, Any]:
        metadata = []
        for metadata_item_data in self.metadata:
            metadata_item = metadata_item_data.to_dict()
            metadata.append(metadata_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metadata_definition_entry import MetadataDefinitionEntry

        d = dict(src_dict)
        metadata = []
        _metadata = d.pop("metadata")
        for metadata_item_data in _metadata:
            metadata_item = MetadataDefinitionEntry.from_dict(metadata_item_data)

            metadata.append(metadata_item)

        metadata_definition = cls(
            metadata=metadata,
        )

        return metadata_definition
