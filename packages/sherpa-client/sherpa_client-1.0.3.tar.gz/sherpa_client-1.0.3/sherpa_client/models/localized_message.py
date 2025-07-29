from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.localized_message_format import LocalizedMessageFormat
from ..models.localized_message_templating import LocalizedMessageTemplating

T = TypeVar("T", bound="LocalizedMessage")


@_attrs_define
class LocalizedMessage:
    """
    Attributes:
        body (str):
        format_ (LocalizedMessageFormat):
        templating (LocalizedMessageTemplating):
        title (str):
    """

    body: str
    format_: LocalizedMessageFormat
    templating: LocalizedMessageTemplating
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

        format_ = LocalizedMessageFormat(d.pop("format"))

        templating = LocalizedMessageTemplating(d.pop("templating"))

        title = d.pop("title")

        localized_message = cls(
            body=body,
            format_=format_,
            templating=templating,
            title=title,
        )

        return localized_message
