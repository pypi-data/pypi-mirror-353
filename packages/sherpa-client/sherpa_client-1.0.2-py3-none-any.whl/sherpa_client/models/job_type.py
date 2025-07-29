from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="JobType")


@_attrs_define
class JobType:
    """
    Attributes:
        enumname (bool):
    """

    enumname: bool

    def to_dict(self) -> dict[str, Any]:
        enumname = self.enumname

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "$enum$name": enumname,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enumname = d.pop("$enum$name")

        job_type = cls(
            enumname=enumname,
        )

        return job_type
