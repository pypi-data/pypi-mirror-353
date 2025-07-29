from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataRestorationRequest")


@_attrs_define
class DataRestorationRequest:
    """
    Attributes:
        session_ids (Union[Unset, list[str]]):
        user_session_ids (Union[Unset, list[str]]):
    """

    session_ids: Union[Unset, list[str]] = UNSET
    user_session_ids: Union[Unset, list[str]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        session_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.session_ids, Unset):
            session_ids = self.session_ids

        user_session_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.user_session_ids, Unset):
            user_session_ids = self.user_session_ids

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if session_ids is not UNSET:
            field_dict["sessionIds"] = session_ids
        if user_session_ids is not UNSET:
            field_dict["userSessionIds"] = user_session_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        session_ids = cast(list[str], d.pop("sessionIds", UNSET))

        user_session_ids = cast(list[str], d.pop("userSessionIds", UNSET))

        data_restoration_request = cls(
            session_ids=session_ids,
            user_session_ids=user_session_ids,
        )

        return data_restoration_request
