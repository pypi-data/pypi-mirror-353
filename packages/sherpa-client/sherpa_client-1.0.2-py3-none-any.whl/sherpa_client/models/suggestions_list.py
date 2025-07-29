from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.aggregation import Aggregation
    from ..models.document import Document


T = TypeVar("T", bound="SuggestionsList")


@_attrs_define
class SuggestionsList:
    """
    Attributes:
        suggestions (list['Document']):
        aggregations (Union[Unset, list['Aggregation']]):
    """

    suggestions: list["Document"]
    aggregations: Union[Unset, list["Aggregation"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        suggestions = []
        for suggestions_item_data in self.suggestions:
            suggestions_item = suggestions_item_data.to_dict()
            suggestions.append(suggestions_item)

        aggregations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.aggregations, Unset):
            aggregations = []
            for aggregations_item_data in self.aggregations:
                aggregations_item = aggregations_item_data.to_dict()
                aggregations.append(aggregations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "suggestions": suggestions,
            }
        )
        if aggregations is not UNSET:
            field_dict["aggregations"] = aggregations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aggregation import Aggregation
        from ..models.document import Document

        d = dict(src_dict)
        suggestions = []
        _suggestions = d.pop("suggestions")
        for suggestions_item_data in _suggestions:
            suggestions_item = Document.from_dict(suggestions_item_data)

            suggestions.append(suggestions_item)

        aggregations = []
        _aggregations = d.pop("aggregations", UNSET)
        for aggregations_item_data in _aggregations or []:
            aggregations_item = Aggregation.from_dict(aggregations_item_data)

            aggregations.append(aggregations_item)

        suggestions_list = cls(
            suggestions=suggestions,
            aggregations=aggregations,
        )

        return suggestions_list
