from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.annotation_creation_mode import AnnotationCreationMode
from ..models.annotation_status import AnnotationStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="Annotation")


@_attrs_define
class Annotation:
    """A document annotation

    Attributes:
        document_identifier (str): The document identifier
        end (int): End offset in document
        label_name (str): The label name
        start (int): Start offset in document
        text (str): Covered text
        creation_mode (Union[Unset, AnnotationCreationMode]): Creation mode
        status (Union[Unset, AnnotationStatus]): Status of the annotation
    """

    document_identifier: str
    end: int
    label_name: str
    start: int
    text: str
    creation_mode: Union[Unset, AnnotationCreationMode] = UNSET
    status: Union[Unset, AnnotationStatus] = UNSET

    def to_dict(self) -> dict[str, Any]:
        document_identifier = self.document_identifier

        end = self.end

        label_name = self.label_name

        start = self.start

        text = self.text

        creation_mode: Union[Unset, str] = UNSET
        if not isinstance(self.creation_mode, Unset):
            creation_mode = self.creation_mode.value

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "documentIdentifier": document_identifier,
                "end": end,
                "labelName": label_name,
                "start": start,
                "text": text,
            }
        )
        if creation_mode is not UNSET:
            field_dict["creationMode"] = creation_mode
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_identifier = d.pop("documentIdentifier")

        end = d.pop("end")

        label_name = d.pop("labelName")

        start = d.pop("start")

        text = d.pop("text")

        _creation_mode = d.pop("creationMode", UNSET)
        creation_mode: Union[Unset, AnnotationCreationMode]
        if isinstance(_creation_mode, Unset):
            creation_mode = UNSET
        else:
            creation_mode = AnnotationCreationMode(_creation_mode)

        _status = d.pop("status", UNSET)
        status: Union[Unset, AnnotationStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = AnnotationStatus(_status)

        annotation = cls(
            document_identifier=document_identifier,
            end=end,
            label_name=label_name,
            start=start,
            text=text,
            creation_mode=creation_mode,
            status=status,
        )

        return annotation
