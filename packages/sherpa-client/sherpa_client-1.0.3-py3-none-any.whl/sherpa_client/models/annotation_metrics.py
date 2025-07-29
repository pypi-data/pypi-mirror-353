from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.annotation_facets import AnnotationFacets
    from ..models.document_facets import DocumentFacets
    from ..models.suggestion_facets import SuggestionFacets


T = TypeVar("T", bound="AnnotationMetrics")


@_attrs_define
class AnnotationMetrics:
    """
    Attributes:
        annotation_count (int):
        annotation_facets (AnnotationFacets):
        document_facets (DocumentFacets):
        documents_in_dataset (int):
        segments_in_dataset (int):
        suggestion_count (int):
        suggestion_facets (SuggestionFacets):
    """

    annotation_count: int
    annotation_facets: "AnnotationFacets"
    document_facets: "DocumentFacets"
    documents_in_dataset: int
    segments_in_dataset: int
    suggestion_count: int
    suggestion_facets: "SuggestionFacets"

    def to_dict(self) -> dict[str, Any]:
        annotation_count = self.annotation_count

        annotation_facets = self.annotation_facets.to_dict()

        document_facets = self.document_facets.to_dict()

        documents_in_dataset = self.documents_in_dataset

        segments_in_dataset = self.segments_in_dataset

        suggestion_count = self.suggestion_count

        suggestion_facets = self.suggestion_facets.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "annotationCount": annotation_count,
                "annotationFacets": annotation_facets,
                "documentFacets": document_facets,
                "documentsInDataset": documents_in_dataset,
                "segmentsInDataset": segments_in_dataset,
                "suggestionCount": suggestion_count,
                "suggestionFacets": suggestion_facets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.annotation_facets import AnnotationFacets
        from ..models.document_facets import DocumentFacets
        from ..models.suggestion_facets import SuggestionFacets

        d = dict(src_dict)
        annotation_count = d.pop("annotationCount")

        annotation_facets = AnnotationFacets.from_dict(d.pop("annotationFacets"))

        document_facets = DocumentFacets.from_dict(d.pop("documentFacets"))

        documents_in_dataset = d.pop("documentsInDataset")

        segments_in_dataset = d.pop("segmentsInDataset")

        suggestion_count = d.pop("suggestionCount")

        suggestion_facets = SuggestionFacets.from_dict(d.pop("suggestionFacets"))

        annotation_metrics = cls(
            annotation_count=annotation_count,
            annotation_facets=annotation_facets,
            document_facets=document_facets,
            documents_in_dataset=documents_in_dataset,
            segments_in_dataset=segments_in_dataset,
            suggestion_count=suggestion_count,
            suggestion_facets=suggestion_facets,
        )

        return annotation_metrics
