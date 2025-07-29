from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.project_message_scope import ProjectMessageScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_audience import MessageAudience
    from ..models.message_mark import MessageMark
    from ..models.project_message_localized import ProjectMessageLocalized


T = TypeVar("T", bound="ProjectMessage")


@_attrs_define
class ProjectMessage:
    """
    Attributes:
        id (str):
        localized (ProjectMessageLocalized):
        scope (ProjectMessageScope):
        audience (Union[Unset, MessageAudience]):
        group (Union[Unset, str]):
        index (Union[Unset, int]):
        mark (Union[Unset, MessageMark]):
    """

    id: str
    localized: "ProjectMessageLocalized"
    scope: ProjectMessageScope
    audience: Union[Unset, "MessageAudience"] = UNSET
    group: Union[Unset, str] = UNSET
    index: Union[Unset, int] = UNSET
    mark: Union[Unset, "MessageMark"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        localized = self.localized.to_dict()

        scope = self.scope.value

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
                "scope": scope,
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
        from ..models.message_audience import MessageAudience
        from ..models.message_mark import MessageMark
        from ..models.project_message_localized import ProjectMessageLocalized

        d = dict(src_dict)
        id = d.pop("id")

        localized = ProjectMessageLocalized.from_dict(d.pop("localized"))

        scope = ProjectMessageScope(d.pop("scope"))

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

        project_message = cls(
            id=id,
            localized=localized,
            scope=scope,
            audience=audience,
            group=group,
            index=index,
            mark=mark,
        )

        return project_message
