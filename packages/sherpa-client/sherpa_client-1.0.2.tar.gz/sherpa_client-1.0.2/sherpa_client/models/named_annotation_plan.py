from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.annotation_plan import AnnotationPlan


T = TypeVar("T", bound="NamedAnnotationPlan")


@_attrs_define
class NamedAnnotationPlan:
    """
    Attributes:
        label (str):
        name (str):
        parameters (AnnotationPlan):
        created_at (Union[Unset, str]):
        created_by (Union[Unset, str]):
        favorite (Union[Unset, bool]):
        modified_at (Union[Unset, str]):
        modified_by (Union[Unset, str]):
        tags (Union[Unset, list[str]]):
    """

    label: str
    name: str
    parameters: "AnnotationPlan"
    created_at: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET
    favorite: Union[Unset, bool] = UNSET
    modified_at: Union[Unset, str] = UNSET
    modified_by: Union[Unset, str] = UNSET
    tags: Union[Unset, list[str]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        name = self.name

        parameters = self.parameters.to_dict()

        created_at = self.created_at

        created_by = self.created_by

        favorite = self.favorite

        modified_at = self.modified_at

        modified_by = self.modified_by

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "label": label,
                "name": name,
                "parameters": parameters,
            }
        )
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if favorite is not UNSET:
            field_dict["favorite"] = favorite
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if modified_by is not UNSET:
            field_dict["modifiedBy"] = modified_by
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.annotation_plan import AnnotationPlan

        d = dict(src_dict)
        label = d.pop("label")

        name = d.pop("name")

        parameters = AnnotationPlan.from_dict(d.pop("parameters"))

        created_at = d.pop("createdAt", UNSET)

        created_by = d.pop("createdBy", UNSET)

        favorite = d.pop("favorite", UNSET)

        modified_at = d.pop("modifiedAt", UNSET)

        modified_by = d.pop("modifiedBy", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))

        named_annotation_plan = cls(
            label=label,
            name=name,
            parameters=parameters,
            created_at=created_at,
            created_by=created_by,
            favorite=favorite,
            modified_at=modified_at,
            modified_by=modified_by,
            tags=tags,
        )

        return named_annotation_plan
