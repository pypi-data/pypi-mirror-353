from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    campaign_id: str,
    *,
    user_session_id: str,
    session_label: Union[Unset, str] = "",
    username: Union[Unset, str] = "",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["userSessionId"] = user_session_id

    params["sessionLabel"] = session_label

    params["username"] = username

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_name}/campaigns/{campaign_id}/_export_user_session".format(
            project_name=project_name,
            campaign_id=campaign_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Any]:
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Any]:
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
    session_label: Union[Unset, str] = "",
    username: Union[Unset, str] = "",
) -> Response[Any]:
    """export a user session

    Args:
        project_name (str):
        campaign_id (str):
        user_session_id (str):
        session_label (Union[Unset, str]):  Default: ''.
        username (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        user_session_id=user_session_id,
        session_label=session_label,
        username=username,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_session_id: str,
    session_label: Union[Unset, str] = "",
    username: Union[Unset, str] = "",
) -> Response[Any]:
    """export a user session

    Args:
        project_name (str):
        campaign_id (str):
        user_session_id (str):
        session_label (Union[Unset, str]):  Default: ''.
        username (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        user_session_id=user_session_id,
        session_label=session_label,
        username=username,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
