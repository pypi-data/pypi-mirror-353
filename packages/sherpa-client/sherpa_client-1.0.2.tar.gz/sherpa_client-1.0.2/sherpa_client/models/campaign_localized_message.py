from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.campaign_localized_message_format import CampaignLocalizedMessageFormat
from ..models.campaign_localized_message_templating import (
    CampaignLocalizedMessageTemplating,
)

T = TypeVar("T", bound="CampaignLocalizedMessage")


@_attrs_define
class CampaignLocalizedMessage:
    """
    Attributes:
        body (str):
        format_ (CampaignLocalizedMessageFormat):
        templating (CampaignLocalizedMessageTemplating):
        title (str):
    """

    body: str
    format_: CampaignLocalizedMessageFormat
    templating: CampaignLocalizedMessageTemplating
    title: str

    def to_dict(self) -> dict[str, Any]:
        body = self.body

        format_ = self.format_.value

        templating = self.templating.value

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "body": body,
                "format": format_,
                "templating": templating,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        body = d.pop("body")

        format_ = CampaignLocalizedMessageFormat(d.pop("format"))

        templating = CampaignLocalizedMessageTemplating(d.pop("templating"))

        title = d.pop("title")

        campaign_localized_message = cls(
            body=body,
            format_=format_,
            templating=templating,
            title=title,
        )

        return campaign_localized_message
