from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sherpa_job_bean import SherpaJobBean


T = TypeVar("T", bound="DeleteResponse")


@_attrs_define
class DeleteResponse:
    """
    Attributes:
        removed_count (int):
        remove_job (Union[Unset, SherpaJobBean]):
    """

    removed_count: int
    remove_job: Union[Unset, "SherpaJobBean"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        removed_count = self.removed_count

        remove_job: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.remove_job, Unset):
            remove_job = self.remove_job.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "removedCount": removed_count,
            }
        )
        if remove_job is not UNSET:
            field_dict["removeJob"] = remove_job

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sherpa_job_bean import SherpaJobBean

        d = dict(src_dict)
        removed_count = d.pop("removedCount")

        _remove_job = d.pop("removeJob", UNSET)
        remove_job: Union[Unset, SherpaJobBean]
        if isinstance(_remove_job, Unset):
            remove_job = UNSET
        else:
            remove_job = SherpaJobBean.from_dict(_remove_job)

        delete_response = cls(
            removed_count=removed_count,
            remove_job=remove_job,
        )

        return delete_response
