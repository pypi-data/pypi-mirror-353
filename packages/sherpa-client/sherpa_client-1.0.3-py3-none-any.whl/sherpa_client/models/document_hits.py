from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.aggregation import Aggregation
    from ..models.document_hit import DocumentHit
    from ..models.search_total import SearchTotal


T = TypeVar("T", bound="DocumentHits")


@_attrs_define
class DocumentHits:
    """
    Attributes:
        hits (list['DocumentHit']):
        total (SearchTotal):
        aggregations (Union[Unset, list['Aggregation']]):
        max_score (Union[Unset, float]):
    """

    hits: list["DocumentHit"]
    total: "SearchTotal"
    aggregations: Union[Unset, list["Aggregation"]] = UNSET
    max_score: Union[Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        hits = []
        for hits_item_data in self.hits:
            hits_item = hits_item_data.to_dict()
            hits.append(hits_item)

        total = self.total.to_dict()

        aggregations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.aggregations, Unset):
            aggregations = []
            for aggregations_item_data in self.aggregations:
                aggregations_item = aggregations_item_data.to_dict()
                aggregations.append(aggregations_item)

        max_score = self.max_score

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "hits": hits,
                "total": total,
            }
        )
        if aggregations is not UNSET:
            field_dict["aggregations"] = aggregations
        if max_score is not UNSET:
            field_dict["max_score"] = max_score

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aggregation import Aggregation
        from ..models.document_hit import DocumentHit
        from ..models.search_total import SearchTotal

        d = dict(src_dict)
        hits = []
        _hits = d.pop("hits")
        for hits_item_data in _hits:
            hits_item = DocumentHit.from_dict(hits_item_data)

            hits.append(hits_item)

        total = SearchTotal.from_dict(d.pop("total"))

        aggregations = []
        _aggregations = d.pop("aggregations", UNSET)
        for aggregations_item_data in _aggregations or []:
            aggregations_item = Aggregation.from_dict(aggregations_item_data)

            aggregations.append(aggregations_item)

        max_score = d.pop("max_score", UNSET)

        document_hits = cls(
            hits=hits,
            total=total,
            aggregations=aggregations,
            max_score=max_score,
        )

        return document_hits
