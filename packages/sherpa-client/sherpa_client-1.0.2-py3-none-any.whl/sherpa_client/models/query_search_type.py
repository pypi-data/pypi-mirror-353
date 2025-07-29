from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.search_type import SearchType


T = TypeVar("T", bound="QuerySearchType")


@_attrs_define
class QuerySearchType:
    """
    Attributes:
        enumname (SearchType):
    """

    enumname: "SearchType"

    def to_dict(self) -> dict[str, Any]:
        enumname = self.enumname.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "$enum$name": enumname,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_type import SearchType

        d = dict(src_dict)
        enumname = SearchType.from_dict(d.pop("$enum$name"))

        query_search_type = cls(
            enumname=enumname,
        )

        return query_search_type
