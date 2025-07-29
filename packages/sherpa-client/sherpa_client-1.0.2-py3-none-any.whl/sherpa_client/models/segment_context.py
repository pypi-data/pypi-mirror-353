from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.segment import Segment


T = TypeVar("T", bound="SegmentContext")


@_attrs_define
class SegmentContext:
    """
    Attributes:
        size (int):
        merged (Union[Unset, Segment]):
        segments (Union[Unset, list['Segment']]):
    """

    size: int
    merged: Union[Unset, "Segment"] = UNSET
    segments: Union[Unset, list["Segment"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        size = self.size

        merged: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.merged, Unset):
            merged = self.merged.to_dict()

        segments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.segments, Unset):
            segments = []
            for segments_item_data in self.segments:
                segments_item = segments_item_data.to_dict()
                segments.append(segments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "size": size,
            }
        )
        if merged is not UNSET:
            field_dict["merged"] = merged
        if segments is not UNSET:
            field_dict["segments"] = segments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.segment import Segment

        d = dict(src_dict)
        size = d.pop("size")

        _merged = d.pop("merged", UNSET)
        merged: Union[Unset, Segment]
        if isinstance(_merged, Unset):
            merged = UNSET
        else:
            merged = Segment.from_dict(_merged)

        segments = []
        _segments = d.pop("segments", UNSET)
        for segments_item_data in _segments or []:
            segments_item = Segment.from_dict(segments_item_data)

            segments.append(segments_item)

        segment_context = cls(
            size=size,
            merged=merged,
            segments=segments,
        )

        return segment_context
