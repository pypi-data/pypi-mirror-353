from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ack import Ack
from ...models.user_session_action_action import UserSessionActionAction
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    campaign_id: str,
    *,
    user_session_id: str,
    action: UserSessionActionAction,
    action_value: Union[Unset, str] = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["userSessionId"] = user_session_id

    json_action = action.value
    params["action"] = json_action

    params["actionValue"] = action_value

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_name}/campaigns/{campaign_id}/_user_session_action".format(
            project_name=project_name,
            campaign_id=campaign_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Ack, Any]]:
    if response.status_code == 200:
        response_200 = Ack.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Ack, Any]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_session_id: str,
    action: UserSessionActionAction,
    action_value: Union[Unset, str] = UNSET,
) -> Response[Union[Ack, Any]]:
    """Perform an action on a user session

    Args:
        project_name (str):
        campaign_id (str):
        user_session_id (str):
        action (UserSessionActionAction):
        action_value (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Ack, Any]]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        user_session_id=user_session_id,
        action=action,
        action_value=action_value,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_session_id: str,
    action: UserSessionActionAction,
    action_value: Union[Unset, str] = UNSET,
) -> Optional[Union[Ack, Any]]:
    """Perform an action on a user session

    Args:
        project_name (str):
        campaign_id (str):
        user_session_id (str):
        action (UserSessionActionAction):
        action_value (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Ack, Any]
    """

    return sync_detailed(
        project_name=project_name,
        campaign_id=campaign_id,
        client=client,
        user_session_id=user_session_id,
        action=action,
        action_value=action_value,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_session_id: str,
    action: UserSessionActionAction,
    action_value: Union[Unset, str] = UNSET,
) -> Response[Union[Ack, Any]]:
    """Perform an action on a user session

    Args:
        project_name (str):
        campaign_id (str):
        user_session_id (str):
        action (UserSessionActionAction):
        action_value (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Ack, Any]]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        user_session_id=user_session_id,
        action=action,
        action_value=action_value,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_session_id: str,
    action: UserSessionActionAction,
    action_value: Union[Unset, str] = UNSET,
) -> Optional[Union[Ack, Any]]:
    """Perform an action on a user session

    Args:
        project_name (str):
        campaign_id (str):
        user_session_id (str):
        action (UserSessionActionAction):
        action_value (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Ack, Any]
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            campaign_id=campaign_id,
            client=client,
            user_session_id=user_session_id,
            action=action,
            action_value=action_value,
        )
    ).parsed
