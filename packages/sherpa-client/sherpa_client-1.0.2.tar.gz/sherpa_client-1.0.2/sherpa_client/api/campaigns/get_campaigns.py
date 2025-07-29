from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.campaign import Campaign
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
    output_fields: Union[Unset, str] = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["inlineMessages"] = inline_messages

    params["inlineUserSessionEvents"] = inline_user_session_events

    params["outputFields"] = output_fields

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/campaigns".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["Campaign"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_campaign_array_item_data in _response_200:
            componentsschemas_campaign_array_item = Campaign.from_dict(
                componentsschemas_campaign_array_item_data
            )

            response_200.append(componentsschemas_campaign_array_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Campaign"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
    output_fields: Union[Unset, str] = UNSET,
) -> Response[list["Campaign"]]:
    """Get annotation campaigns of the project

    Args:
        project_name (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Campaign']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        inline_messages=inline_messages,
        inline_user_session_events=inline_user_session_events,
        output_fields=output_fields,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
    output_fields: Union[Unset, str] = UNSET,
) -> Optional[list["Campaign"]]:
    """Get annotation campaigns of the project

    Args:
        project_name (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Campaign']
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        inline_messages=inline_messages,
        inline_user_session_events=inline_user_session_events,
        output_fields=output_fields,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
    output_fields: Union[Unset, str] = UNSET,
) -> Response[list["Campaign"]]:
    """Get annotation campaigns of the project

    Args:
        project_name (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Campaign']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        inline_messages=inline_messages,
        inline_user_session_events=inline_user_session_events,
        output_fields=output_fields,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    inline_messages: Union[Unset, bool] = False,
    inline_user_session_events: Union[Unset, str] = "none",
    output_fields: Union[Unset, str] = UNSET,
) -> Optional[list["Campaign"]]:
    """Get annotation campaigns of the project

    Args:
        project_name (str):
        inline_messages (Union[Unset, bool]):  Default: False.
        inline_user_session_events (Union[Unset, str]):  Default: 'none'.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Campaign']
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            inline_messages=inline_messages,
            inline_user_session_events=inline_user_session_events,
            output_fields=output_fields,
        )
    ).parsed
