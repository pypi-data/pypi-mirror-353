from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.doc_category import DocCategory
    from ..models.doc_sentence_metadata import DocSentenceMetadata


T = TypeVar("T", bound="DocSentence")


@_attrs_define
class DocSentence:
    """
    Attributes:
        end (int):
        start (int):
        categories (Union[Unset, list['DocCategory']]):
        metadata (Union[Unset, DocSentenceMetadata]):
        text (Union[Unset, str]):
    """

    end: int
    start: int
    categories: Union[Unset, list["DocCategory"]] = UNSET
    metadata: Union[Unset, "DocSentenceMetadata"] = UNSET
    text: Union[Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        end = self.end

        start = self.start

        categories: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.categories, Unset):
            categories = []
            for categories_item_data in self.categories:
                categories_item = categories_item_data.to_dict()
                categories.append(categories_item)

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        text = self.text

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "end": end,
                "start": start,
            }
        )
        if categories is not UNSET:
            field_dict["categories"] = categories
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.doc_category import DocCategory
        from ..models.doc_sentence_metadata import DocSentenceMetadata

        d = dict(src_dict)
        end = d.pop("end")

        start = d.pop("start")

        categories = []
        _categories = d.pop("categories", UNSET)
        for categories_item_data in _categories or []:
            categories_item = DocCategory.from_dict(categories_item_data)

            categories.append(categories_item)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, DocSentenceMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DocSentenceMetadata.from_dict(_metadata)

        text = d.pop("text", UNSET)

        doc_sentence = cls(
            end=end,
            start=start,
            categories=categories,
            metadata=metadata,
            text=text,
        )

        return doc_sentence
