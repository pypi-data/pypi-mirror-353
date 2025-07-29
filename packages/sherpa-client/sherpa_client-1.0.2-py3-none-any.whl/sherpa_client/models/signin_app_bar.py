from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SigninAppBar")


@_attrs_define
class SigninAppBar:
    """Top bar on signin page

    Attributes:
        bar_color (Union[Unset, str]):
        icon_color (Union[Unset, str]):
        logo_is_grey (Union[Unset, bool]):  Default: True.
        logo_is_white (Union[Unset, bool]):  Default: False.
        text (Union[Unset, str]):  Default: 'Kairntech'.
        text_color (Union[Unset, str]):
    """

    bar_color: Union[Unset, str] = UNSET
    icon_color: Union[Unset, str] = UNSET
    logo_is_grey: Union[Unset, bool] = True
    logo_is_white: Union[Unset, bool] = False
    text: Union[Unset, str] = "Kairntech"
    text_color: Union[Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        bar_color = self.bar_color

        icon_color = self.icon_color

        logo_is_grey = self.logo_is_grey

        logo_is_white = self.logo_is_white

        text = self.text

        text_color = self.text_color

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if bar_color is not UNSET:
            field_dict["barColor"] = bar_color
        if icon_color is not UNSET:
            field_dict["iconColor"] = icon_color
        if logo_is_grey is not UNSET:
            field_dict["logoIsGrey"] = logo_is_grey
        if logo_is_white is not UNSET:
            field_dict["logoIsWhite"] = logo_is_white
        if text is not UNSET:
            field_dict["text"] = text
        if text_color is not UNSET:
            field_dict["textColor"] = text_color

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bar_color = d.pop("barColor", UNSET)

        icon_color = d.pop("iconColor", UNSET)

        logo_is_grey = d.pop("logoIsGrey", UNSET)

        logo_is_white = d.pop("logoIsWhite", UNSET)

        text = d.pop("text", UNSET)

        text_color = d.pop("textColor", UNSET)

        signin_app_bar = cls(
            bar_color=bar_color,
            icon_color=icon_color,
            logo_is_grey=logo_is_grey,
            logo_is_white=logo_is_white,
            text=text,
            text_color=text_color,
        )

        return signin_app_bar
