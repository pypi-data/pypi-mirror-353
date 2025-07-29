from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.category_creation_mode import CategoryCreationMode
from ..models.category_status import CategoryStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="Category")


@_attrs_define
class Category:
    """A document category

    Attributes:
        document_identifier (str): identifier of the document
        label_name (str): The label name
        creation_mode (Union[Unset, CategoryCreationMode]): Creation mode
        score (Union[Unset, float]): Score of the category
        status (Union[Unset, CategoryStatus]): Status of the category
    """

    document_identifier: str
    label_name: str
    creation_mode: Union[Unset, CategoryCreationMode] = UNSET
    score: Union[Unset, float] = UNSET
    status: Union[Unset, CategoryStatus] = UNSET

    def to_dict(self) -> dict[str, Any]:
        document_identifier = self.document_identifier

        label_name = self.label_name

        creation_mode: Union[Unset, str] = UNSET
        if not isinstance(self.creation_mode, Unset):
            creation_mode = self.creation_mode.value

        score = self.score

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "documentIdentifier": document_identifier,
                "labelName": label_name,
            }
        )
        if creation_mode is not UNSET:
            field_dict["creationMode"] = creation_mode
        if score is not UNSET:
            field_dict["score"] = score
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_identifier = d.pop("documentIdentifier")

        label_name = d.pop("labelName")

        _creation_mode = d.pop("creationMode", UNSET)
        creation_mode: Union[Unset, CategoryCreationMode]
        if isinstance(_creation_mode, Unset):
            creation_mode = UNSET
        else:
            creation_mode = CategoryCreationMode(_creation_mode)

        score = d.pop("score", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, CategoryStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = CategoryStatus(_status)

        category = cls(
            document_identifier=document_identifier,
            label_name=label_name,
            creation_mode=creation_mode,
            score=score,
            status=status,
        )

        return category
