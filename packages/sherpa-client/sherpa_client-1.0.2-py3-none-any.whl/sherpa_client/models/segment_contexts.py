from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.segment_context import SegmentContext


T = TypeVar("T", bound="SegmentContexts")


@_attrs_define
class SegmentContexts:
    """
    Attributes:
        after (SegmentContext):
        before (SegmentContext):
    """

    after: "SegmentContext"
    before: "SegmentContext"

    def to_dict(self) -> dict[str, Any]:
        after = self.after.to_dict()

        before = self.before.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "after": after,
                "before": before,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.segment_context import SegmentContext

        d = dict(src_dict)
        after = SegmentContext.from_dict(d.pop("after"))

        before = SegmentContext.from_dict(d.pop("before"))

        segment_contexts = cls(
            after=after,
            before=before,
        )

        return segment_contexts
