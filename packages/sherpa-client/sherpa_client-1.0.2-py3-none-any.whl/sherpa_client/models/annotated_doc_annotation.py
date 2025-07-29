from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.annotated_doc_annotation_creation_mode import (
    AnnotatedDocAnnotationCreationMode,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.annotated_doc_annotation_properties import (
        AnnotatedDocAnnotationProperties,
    )
    from ..models.annotation_term import AnnotationTerm


T = TypeVar("T", bound="AnnotatedDocAnnotation")


@_attrs_define
class AnnotatedDocAnnotation:
    """A document annotation

    Attributes:
        end (int): End offset in document
        label_name (str): Label name
        start (int): Start offset in document
        text (str): Covered text
        creation_mode (Union[Unset, AnnotatedDocAnnotationCreationMode]): Creation mode
        label (Union[Unset, str]): Human-friendly label
        label_id (Union[Unset, str]): External label identifier
        properties (Union[Unset, AnnotatedDocAnnotationProperties]): Additional properties
        score (Union[Unset, float]): Score of the annotation
        terms (Union[Unset, list['AnnotationTerm']]):
    """

    end: int
    label_name: str
    start: int
    text: str
    creation_mode: Union[Unset, AnnotatedDocAnnotationCreationMode] = UNSET
    label: Union[Unset, str] = UNSET
    label_id: Union[Unset, str] = UNSET
    properties: Union[Unset, "AnnotatedDocAnnotationProperties"] = UNSET
    score: Union[Unset, float] = UNSET
    terms: Union[Unset, list["AnnotationTerm"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        end = self.end

        label_name = self.label_name

        start = self.start

        text = self.text

        creation_mode: Union[Unset, str] = UNSET
        if not isinstance(self.creation_mode, Unset):
            creation_mode = self.creation_mode.value

        label = self.label

        label_id = self.label_id

        properties: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        score = self.score

        terms: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.terms, Unset):
            terms = []
            for terms_item_data in self.terms:
                terms_item = terms_item_data.to_dict()
                terms.append(terms_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "end": end,
                "labelName": label_name,
                "start": start,
                "text": text,
            }
        )
        if creation_mode is not UNSET:
            field_dict["creationMode"] = creation_mode
        if label is not UNSET:
            field_dict["label"] = label
        if label_id is not UNSET:
            field_dict["labelId"] = label_id
        if properties is not UNSET:
            field_dict["properties"] = properties
        if score is not UNSET:
            field_dict["score"] = score
        if terms is not UNSET:
            field_dict["terms"] = terms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.annotated_doc_annotation_properties import (
            AnnotatedDocAnnotationProperties,
        )
        from ..models.annotation_term import AnnotationTerm

        d = dict(src_dict)
        end = d.pop("end")

        label_name = d.pop("labelName")

        start = d.pop("start")

        text = d.pop("text")

        _creation_mode = d.pop("creationMode", UNSET)
        creation_mode: Union[Unset, AnnotatedDocAnnotationCreationMode]
        if isinstance(_creation_mode, Unset):
            creation_mode = UNSET
        else:
            creation_mode = AnnotatedDocAnnotationCreationMode(_creation_mode)

        label = d.pop("label", UNSET)

        label_id = d.pop("labelId", UNSET)

        _properties = d.pop("properties", UNSET)
        properties: Union[Unset, AnnotatedDocAnnotationProperties]
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = AnnotatedDocAnnotationProperties.from_dict(_properties)

        score = d.pop("score", UNSET)

        terms = []
        _terms = d.pop("terms", UNSET)
        for terms_item_data in _terms or []:
            terms_item = AnnotationTerm.from_dict(terms_item_data)

            terms.append(terms_item)

        annotated_doc_annotation = cls(
            end=end,
            label_name=label_name,
            start=start,
            text=text,
            creation_mode=creation_mode,
            label=label,
            label_id=label_id,
            properties=properties,
            score=score,
            terms=terms,
        )

        return annotated_doc_annotation
