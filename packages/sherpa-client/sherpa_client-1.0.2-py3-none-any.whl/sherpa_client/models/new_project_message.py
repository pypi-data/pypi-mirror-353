from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.new_project_message_scope import NewProjectMessageScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_audience import MessageAudience
    from ..models.new_project_message_localized import NewProjectMessageLocalized


T = TypeVar("T", bound="NewProjectMessage")


@_attrs_define
class NewProjectMessage:
    """
    Attributes:
        localized (NewProjectMessageLocalized):
        scope (NewProjectMessageScope):
        audience (Union[Unset, MessageAudience]):
        group (Union[Unset, str]):
        index (Union[Unset, int]):
    """

    localized: "NewProjectMessageLocalized"
    scope: NewProjectMessageScope
    audience: Union[Unset, "MessageAudience"] = UNSET
    group: Union[Unset, str] = UNSET
    index: Union[Unset, int] = UNSET

    def to_dict(self) -> dict[str, Any]:
        localized = self.localized.to_dict()

        scope = self.scope.value

        audience: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.audience, Unset):
            audience = self.audience.to_dict()

        group = self.group

        index = self.index

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "localized": localized,
                "scope": scope,
            }
        )
        if audience is not UNSET:
            field_dict["audience"] = audience
        if group is not UNSET:
            field_dict["group"] = group
        if index is not UNSET:
            field_dict["index"] = index

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_audience import MessageAudience
        from ..models.new_project_message_localized import NewProjectMessageLocalized

        d = dict(src_dict)
        localized = NewProjectMessageLocalized.from_dict(d.pop("localized"))

        scope = NewProjectMessageScope(d.pop("scope"))

        _audience = d.pop("audience", UNSET)
        audience: Union[Unset, MessageAudience]
        if isinstance(_audience, Unset):
            audience = UNSET
        else:
            audience = MessageAudience.from_dict(_audience)

        group = d.pop("group", UNSET)

        index = d.pop("index", UNSET)

        new_project_message = cls(
            localized=localized,
            scope=scope,
            audience=audience,
            group=group,
            index=index,
        )

        return new_project_message
