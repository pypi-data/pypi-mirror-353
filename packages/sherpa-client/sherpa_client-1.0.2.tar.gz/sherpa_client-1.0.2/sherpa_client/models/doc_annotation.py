from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.doc_annotation_creation_mode import DocAnnotationCreationMode
from ..models.doc_annotation_status import DocAnnotationStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.annotation_term import AnnotationTerm
    from ..models.doc_annotation_properties import DocAnnotationProperties


T = TypeVar("T", bound="DocAnnotation")


@_attrs_define
class DocAnnotation:
    """A document annotation

    Attributes:
        end (int): End offset in document
        label_name (str): The label name
        start (int): Start offset in document
        text (str): Covered text
        created_by (Union[Unset, str]): User having created the annotation
        created_date (Union[Unset, str]): Creation date
        creation_mode (Union[Unset, DocAnnotationCreationMode]): Creation mode
        identifier (Union[Unset, str]): Annotation identifier (only in 'html version')
        modified_date (Union[Unset, str]): Last modification date
        properties (Union[Unset, DocAnnotationProperties]): Additional properties
        status (Union[Unset, DocAnnotationStatus]): Status of the annotation
        terms (Union[Unset, list['AnnotationTerm']]):
    """

    end: int
    label_name: str
    start: int
    text: str
    created_by: Union[Unset, str] = UNSET
    created_date: Union[Unset, str] = UNSET
    creation_mode: Union[Unset, DocAnnotationCreationMode] = UNSET
    identifier: Union[Unset, str] = UNSET
    modified_date: Union[Unset, str] = UNSET
    properties: Union[Unset, "DocAnnotationProperties"] = UNSET
    status: Union[Unset, DocAnnotationStatus] = UNSET
    terms: Union[Unset, list["AnnotationTerm"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        end = self.end

        label_name = self.label_name

        start = self.start

        text = self.text

        created_by = self.created_by

        created_date = self.created_date

        creation_mode: Union[Unset, str] = UNSET
        if not isinstance(self.creation_mode, Unset):
            creation_mode = self.creation_mode.value

        identifier = self.identifier

        modified_date = self.modified_date

        properties: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

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
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created_date is not UNSET:
            field_dict["createdDate"] = created_date
        if creation_mode is not UNSET:
            field_dict["creationMode"] = creation_mode
        if identifier is not UNSET:
            field_dict["identifier"] = identifier
        if modified_date is not UNSET:
            field_dict["modifiedDate"] = modified_date
        if properties is not UNSET:
            field_dict["properties"] = properties
        if status is not UNSET:
            field_dict["status"] = status
        if terms is not UNSET:
            field_dict["terms"] = terms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.annotation_term import AnnotationTerm
        from ..models.doc_annotation_properties import DocAnnotationProperties

        d = dict(src_dict)
        end = d.pop("end")

        label_name = d.pop("labelName")

        start = d.pop("start")

        text = d.pop("text")

        created_by = d.pop("createdBy", UNSET)

        created_date = d.pop("createdDate", UNSET)

        _creation_mode = d.pop("creationMode", UNSET)
        creation_mode: Union[Unset, DocAnnotationCreationMode]
        if isinstance(_creation_mode, Unset):
            creation_mode = UNSET
        else:
            creation_mode = DocAnnotationCreationMode(_creation_mode)

        identifier = d.pop("identifier", UNSET)

        modified_date = d.pop("modifiedDate", UNSET)

        _properties = d.pop("properties", UNSET)
        properties: Union[Unset, DocAnnotationProperties]
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = DocAnnotationProperties.from_dict(_properties)

        _status = d.pop("status", UNSET)
        status: Union[Unset, DocAnnotationStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = DocAnnotationStatus(_status)

        terms = []
        _terms = d.pop("terms", UNSET)
        for terms_item_data in _terms or []:
            terms_item = AnnotationTerm.from_dict(terms_item_data)

            terms.append(terms_item)

        doc_annotation = cls(
            end=end,
            label_name=label_name,
            start=start,
            text=text,
            created_by=created_by,
            created_date=created_date,
            creation_mode=creation_mode,
            identifier=identifier,
            modified_date=modified_date,
            properties=properties,
            status=status,
            terms=terms,
        )

        return doc_annotation
