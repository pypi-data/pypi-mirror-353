from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.campaign import Campaign
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    campaign_id: str,
    *,
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["inlineMessages"] = inline_messages

    params["inlineUserSessionEvents"] = inline_user_session_events

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/campaigns/{campaign_id}".format(
            project_name=project_name,
            campaign_id=campaign_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Campaign]]:
    if response.status_code == 200:
        response_200 = Campaign.from_dict(response.json())

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
) -> Response[Union[Any, Campaign]]:
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
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
) -> Response[Union[Any, Campaign]]:
    """Get campaign

    Args:
        project_name (str):
        campaign_id (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Campaign]]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        inline_messages=inline_messages,
        inline_user_session_events=inline_user_session_events,
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
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
) -> Optional[Union[Any, Campaign]]:
    """Get campaign

    Args:
        project_name (str):
        campaign_id (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Campaign]
    """

    return sync_detailed(
        project_name=project_name,
        campaign_id=campaign_id,
        client=client,
        inline_messages=inline_messages,
        inline_user_session_events=inline_user_session_events,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
) -> Response[Union[Any, Campaign]]:
    """Get campaign

    Args:
        project_name (str):
        campaign_id (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Campaign]]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        inline_messages=inline_messages,
        inline_user_session_events=inline_user_session_events,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
) -> Optional[Union[Any, Campaign]]:
    """Get campaign

    Args:
        project_name (str):
        campaign_id (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Campaign]
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            campaign_id=campaign_id,
            client=client,
            inline_messages=inline_messages,
            inline_user_session_events=inline_user_session_events,
        )
    ).parsed
