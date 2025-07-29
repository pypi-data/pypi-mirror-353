from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="SessionCorpusPermissionChange")


@_attrs_define
class SessionCorpusPermissionChange:
    """
    Attributes:
        add (bool):
        project_name (str):
        session_label (str):
        usernames (list[Any]):
    """

    add: bool
    project_name: str
    session_label: str
    usernames: list[Any]

    def to_dict(self) -> dict[str, Any]:
        add = self.add

        project_name = self.project_name

        session_label = self.session_label

        usernames = self.usernames

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "add": add,
                "projectName": project_name,
                "sessionLabel": session_label,
                "usernames": usernames,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        add = d.pop("add")

        project_name = d.pop("projectName")

        session_label = d.pop("sessionLabel")

        usernames = cast(list[Any], d.pop("usernames"))

        session_corpus_permission_change = cls(
            add=add,
            project_name=project_name,
            session_label=session_label,
            usernames=usernames,
        )

        return session_corpus_permission_change
