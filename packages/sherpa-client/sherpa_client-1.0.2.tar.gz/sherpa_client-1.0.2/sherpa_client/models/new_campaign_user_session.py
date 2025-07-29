from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="NewCampaignUserSession")


@_attrs_define
class NewCampaignUserSession:
    """
    Attributes:
        session_id (str):
        session_mode_id (str):
        username (str):
    """

    session_id: str
    session_mode_id: str
    username: str

    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        session_mode_id = self.session_mode_id

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "sessionId": session_id,
                "sessionModeId": session_mode_id,
                "username": username,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        session_id = d.pop("sessionId")

        session_mode_id = d.pop("sessionModeId")

        username = d.pop("username")

        new_campaign_user_session = cls(
            session_id=session_id,
            session_mode_id=session_mode_id,
            username=username,
        )

        return new_campaign_user_session
