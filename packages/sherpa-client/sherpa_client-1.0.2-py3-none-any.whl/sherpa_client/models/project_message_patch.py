from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.project_message_patch_scope import ProjectMessagePatchScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_audience import MessageAudience
    from ..models.project_message_patch_localized import ProjectMessagePatchLocalized


T = TypeVar("T", bound="ProjectMessagePatch")


@_attrs_define
class ProjectMessagePatch:
    """
    Attributes:
        audience (Union[Unset, MessageAudience]):
        group (Union[Unset, str]):
        index (Union[Unset, int]):
        localized (Union[Unset, ProjectMessagePatchLocalized]):
        scope (Union[Unset, ProjectMessagePatchScope]):
    """

    audience: Union[Unset, "MessageAudience"] = UNSET
    group: Union[Unset, str] = UNSET
    index: Union[Unset, int] = UNSET
    localized: Union[Unset, "ProjectMessagePatchLocalized"] = UNSET
    scope: Union[Unset, ProjectMessagePatchScope] = UNSET

    def to_dict(self) -> dict[str, Any]:
        audience: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.audience, Unset):
            audience = self.audience.to_dict()

        group = self.group

        index = self.index

        localized: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.localized, Unset):
            localized = self.localized.to_dict()

        scope: Union[Unset, str] = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope.value

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if audience is not UNSET:
            field_dict["audience"] = audience
        if group is not UNSET:
            field_dict["group"] = group
        if index is not UNSET:
            field_dict["index"] = index
        if localized is not UNSET:
            field_dict["localized"] = localized
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_audience import MessageAudience
        from ..models.project_message_patch_localized import (
            ProjectMessagePatchLocalized,
        )

        d = dict(src_dict)
        _audience = d.pop("audience", UNSET)
        audience: Union[Unset, MessageAudience]
        if isinstance(_audience, Unset):
            audience = UNSET
        else:
            audience = MessageAudience.from_dict(_audience)

        group = d.pop("group", UNSET)

        index = d.pop("index", UNSET)

        _localized = d.pop("localized", UNSET)
        localized: Union[Unset, ProjectMessagePatchLocalized]
        if isinstance(_localized, Unset):
            localized = UNSET
        else:
            localized = ProjectMessagePatchLocalized.from_dict(_localized)

        _scope = d.pop("scope", UNSET)
        scope: Union[Unset, ProjectMessagePatchScope]
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = ProjectMessagePatchScope(_scope)

        project_message_patch = cls(
            audience=audience,
            group=group,
            index=index,
            localized=localized,
            scope=scope,
        )

        return project_message_patch
