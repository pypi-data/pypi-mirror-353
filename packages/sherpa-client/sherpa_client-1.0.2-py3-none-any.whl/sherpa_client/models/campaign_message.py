from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.campaign_message_localized import CampaignMessageLocalized
    from ..models.message_audience import MessageAudience
    from ..models.message_mark import MessageMark


T = TypeVar("T", bound="CampaignMessage")


@_attrs_define
class CampaignMessage:
    """
    Attributes:
        id (str):
        localized (CampaignMessageLocalized):
        audience (Union[Unset, MessageAudience]):
        group (Union[Unset, str]):
        index (Union[Unset, int]):
        mark (Union[Unset, MessageMark]):
    """

    id: str
    localized: "CampaignMessageLocalized"
    audience: Union[Unset, "MessageAudience"] = UNSET
    group: Union[Unset, str] = UNSET
    index: Union[Unset, int] = UNSET
    mark: Union[Unset, "MessageMark"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        localized = self.localized.to_dict()

        audience: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.audience, Unset):
            audience = self.audience.to_dict()

        group = self.group

        index = self.index

        mark: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.mark, Unset):
            mark = self.mark.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "localized": localized,
            }
        )
        if audience is not UNSET:
            field_dict["audience"] = audience
        if group is not UNSET:
            field_dict["group"] = group
        if index is not UNSET:
            field_dict["index"] = index
        if mark is not UNSET:
            field_dict["mark"] = mark

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.campaign_message_localized import CampaignMessageLocalized
        from ..models.message_audience import MessageAudience
        from ..models.message_mark import MessageMark

        d = dict(src_dict)
        id = d.pop("id")

        localized = CampaignMessageLocalized.from_dict(d.pop("localized"))

        _audience = d.pop("audience", UNSET)
        audience: Union[Unset, MessageAudience]
        if isinstance(_audience, Unset):
            audience = UNSET
        else:
            audience = MessageAudience.from_dict(_audience)

        group = d.pop("group", UNSET)

        index = d.pop("index", UNSET)

        _mark = d.pop("mark", UNSET)
        mark: Union[Unset, MessageMark]
        if isinstance(_mark, Unset):
            mark = UNSET
        else:
            mark = MessageMark.from_dict(_mark)

        campaign_message = cls(
            id=id,
            localized=localized,
            audience=audience,
            group=group,
            index=index,
            mark=mark,
        )

        return campaign_message
