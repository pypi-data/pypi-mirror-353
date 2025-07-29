from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.campaign_message import CampaignMessage
    from ..models.campaign_session import CampaignSession
    from ..models.campaign_session_mode import CampaignSessionMode
    from ..models.campaign_user_group import CampaignUserGroup
    from ..models.campaign_user_session import CampaignUserSession
    from ..models.email_notifications import EmailNotifications
    from ..models.message_id import MessageId
    from ..models.new_campaign_message import NewCampaignMessage


T = TypeVar("T", bound="Campaign")


@_attrs_define
class Campaign:
    """
    Attributes:
        id (str):
        label (str):
        overview_messages (list[Union['CampaignMessage', 'MessageId', 'NewCampaignMessage']]):
        stop_messages (list[Union['CampaignMessage', 'MessageId', 'NewCampaignMessage']]):
        welcome_messages (list[Union['CampaignMessage', 'MessageId', 'NewCampaignMessage']]):
        email_notifications (Union[Unset, EmailNotifications]):
        session_modes (Union[Unset, list['CampaignSessionMode']]):
        sessions (Union[Unset, list['CampaignSession']]):
        user_groups (Union[Unset, list['CampaignUserGroup']]):
        user_sessions (Union[Unset, list['CampaignUserSession']]):
    """

    id: str
    label: str
    overview_messages: list[Union["CampaignMessage", "MessageId", "NewCampaignMessage"]]
    stop_messages: list[Union["CampaignMessage", "MessageId", "NewCampaignMessage"]]
    welcome_messages: list[Union["CampaignMessage", "MessageId", "NewCampaignMessage"]]
    email_notifications: Union[Unset, "EmailNotifications"] = UNSET
    session_modes: Union[Unset, list["CampaignSessionMode"]] = UNSET
    sessions: Union[Unset, list["CampaignSession"]] = UNSET
    user_groups: Union[Unset, list["CampaignUserGroup"]] = UNSET
    user_sessions: Union[Unset, list["CampaignUserSession"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.campaign_message import CampaignMessage
        from ..models.message_id import MessageId

        id = self.id

        label = self.label

        overview_messages = []
        for overview_messages_item_data in self.overview_messages:
            overview_messages_item: dict[str, Any]
            if isinstance(overview_messages_item_data, MessageId):
                overview_messages_item = overview_messages_item_data.to_dict()
            elif isinstance(overview_messages_item_data, CampaignMessage):
                overview_messages_item = overview_messages_item_data.to_dict()
            else:
                overview_messages_item = overview_messages_item_data.to_dict()

            overview_messages.append(overview_messages_item)

        stop_messages = []
        for stop_messages_item_data in self.stop_messages:
            stop_messages_item: dict[str, Any]
            if isinstance(stop_messages_item_data, MessageId):
                stop_messages_item = stop_messages_item_data.to_dict()
            elif isinstance(stop_messages_item_data, CampaignMessage):
                stop_messages_item = stop_messages_item_data.to_dict()
            else:
                stop_messages_item = stop_messages_item_data.to_dict()

            stop_messages.append(stop_messages_item)

        welcome_messages = []
        for welcome_messages_item_data in self.welcome_messages:
            welcome_messages_item: dict[str, Any]
            if isinstance(welcome_messages_item_data, MessageId):
                welcome_messages_item = welcome_messages_item_data.to_dict()
            elif isinstance(welcome_messages_item_data, CampaignMessage):
                welcome_messages_item = welcome_messages_item_data.to_dict()
            else:
                welcome_messages_item = welcome_messages_item_data.to_dict()

            welcome_messages.append(welcome_messages_item)

        email_notifications: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.email_notifications, Unset):
            email_notifications = self.email_notifications.to_dict()

        session_modes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.session_modes, Unset):
            session_modes = []
            for session_modes_item_data in self.session_modes:
                session_modes_item = session_modes_item_data.to_dict()
                session_modes.append(session_modes_item)

        sessions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sessions, Unset):
            sessions = []
            for sessions_item_data in self.sessions:
                sessions_item = sessions_item_data.to_dict()
                sessions.append(sessions_item)

        user_groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.user_groups, Unset):
            user_groups = []
            for user_groups_item_data in self.user_groups:
                user_groups_item = user_groups_item_data.to_dict()
                user_groups.append(user_groups_item)

        user_sessions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.user_sessions, Unset):
            user_sessions = []
            for user_sessions_item_data in self.user_sessions:
                user_sessions_item = user_sessions_item_data.to_dict()
                user_sessions.append(user_sessions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "label": label,
                "overviewMessages": overview_messages,
                "stopMessages": stop_messages,
                "welcomeMessages": welcome_messages,
            }
        )
        if email_notifications is not UNSET:
            field_dict["emailNotifications"] = email_notifications
        if session_modes is not UNSET:
            field_dict["sessionModes"] = session_modes
        if sessions is not UNSET:
            field_dict["sessions"] = sessions
        if user_groups is not UNSET:
            field_dict["userGroups"] = user_groups
        if user_sessions is not UNSET:
            field_dict["userSessions"] = user_sessions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.campaign_message import CampaignMessage
        from ..models.campaign_session import CampaignSession
        from ..models.campaign_session_mode import CampaignSessionMode
        from ..models.campaign_user_group import CampaignUserGroup
        from ..models.campaign_user_session import CampaignUserSession
        from ..models.email_notifications import EmailNotifications
        from ..models.message_id import MessageId
        from ..models.new_campaign_message import NewCampaignMessage

        d = dict(src_dict)
        id = d.pop("id")

        label = d.pop("label")

        overview_messages = []
        _overview_messages = d.pop("overviewMessages")
        for overview_messages_item_data in _overview_messages:

            def _parse_overview_messages_item(
                data: object,
            ) -> Union["CampaignMessage", "MessageId", "NewCampaignMessage"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    overview_messages_item_type_0 = MessageId.from_dict(data)

                    return overview_messages_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    overview_messages_item_type_1 = CampaignMessage.from_dict(data)

                    return overview_messages_item_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                overview_messages_item_type_2 = NewCampaignMessage.from_dict(data)

                return overview_messages_item_type_2

            overview_messages_item = _parse_overview_messages_item(
                overview_messages_item_data
            )

            overview_messages.append(overview_messages_item)

        stop_messages = []
        _stop_messages = d.pop("stopMessages")
        for stop_messages_item_data in _stop_messages:

            def _parse_stop_messages_item(
                data: object,
            ) -> Union["CampaignMessage", "MessageId", "NewCampaignMessage"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stop_messages_item_type_0 = MessageId.from_dict(data)

                    return stop_messages_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stop_messages_item_type_1 = CampaignMessage.from_dict(data)

                    return stop_messages_item_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                stop_messages_item_type_2 = NewCampaignMessage.from_dict(data)

                return stop_messages_item_type_2

            stop_messages_item = _parse_stop_messages_item(stop_messages_item_data)

            stop_messages.append(stop_messages_item)

        welcome_messages = []
        _welcome_messages = d.pop("welcomeMessages")
        for welcome_messages_item_data in _welcome_messages:

            def _parse_welcome_messages_item(
                data: object,
            ) -> Union["CampaignMessage", "MessageId", "NewCampaignMessage"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    welcome_messages_item_type_0 = MessageId.from_dict(data)

                    return welcome_messages_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    welcome_messages_item_type_1 = CampaignMessage.from_dict(data)

                    return welcome_messages_item_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                welcome_messages_item_type_2 = NewCampaignMessage.from_dict(data)

                return welcome_messages_item_type_2

            welcome_messages_item = _parse_welcome_messages_item(
                welcome_messages_item_data
            )

            welcome_messages.append(welcome_messages_item)

        _email_notifications = d.pop("emailNotifications", UNSET)
        email_notifications: Union[Unset, EmailNotifications]
        if isinstance(_email_notifications, Unset):
            email_notifications = UNSET
        else:
            email_notifications = EmailNotifications.from_dict(_email_notifications)

        session_modes = []
        _session_modes = d.pop("sessionModes", UNSET)
        for session_modes_item_data in _session_modes or []:
            session_modes_item = CampaignSessionMode.from_dict(session_modes_item_data)

            session_modes.append(session_modes_item)

        sessions = []
        _sessions = d.pop("sessions", UNSET)
        for sessions_item_data in _sessions or []:
            sessions_item = CampaignSession.from_dict(sessions_item_data)

            sessions.append(sessions_item)

        user_groups = []
        _user_groups = d.pop("userGroups", UNSET)
        for user_groups_item_data in _user_groups or []:
            user_groups_item = CampaignUserGroup.from_dict(user_groups_item_data)

            user_groups.append(user_groups_item)

        user_sessions = []
        _user_sessions = d.pop("userSessions", UNSET)
        for user_sessions_item_data in _user_sessions or []:
            user_sessions_item = CampaignUserSession.from_dict(user_sessions_item_data)

            user_sessions.append(user_sessions_item)

        campaign = cls(
            id=id,
            label=label,
            overview_messages=overview_messages,
            stop_messages=stop_messages,
            welcome_messages=welcome_messages,
            email_notifications=email_notifications,
            session_modes=session_modes,
            sessions=sessions,
            user_groups=user_groups,
            user_sessions=user_sessions,
        )

        return campaign
