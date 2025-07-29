from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    indices: Union[Unset, str] = "*",
    timeout_millis: Union[Unset, int] = 1500,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["indices"] = indices

    params["timeoutMillis"] = timeout_millis

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_name}/_flush".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Any]:
    if response.status_code == 204:
        return None
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
    *,
    client: Union[AuthenticatedClient, Client],
    indices: Union[Unset, str] = "*",
    timeout_millis: Union[Unset, int] = 1500,
) -> Response[Any]:
    """flush search indices of the project

    Args:
        project_name (str):
        indices (Union[Unset, str]):  Default: '*'.
        timeout_millis (Union[Unset, int]):  Default: 1500.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        indices=indices,
        timeout_millis=timeout_millis,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    indices: Union[Unset, str] = "*",
    timeout_millis: Union[Unset, int] = 1500,
) -> Response[Any]:
    """flush search indices of the project

    Args:
        project_name (str):
        indices (Union[Unset, str]):  Default: '*'.
        timeout_millis (Union[Unset, int]):  Default: 1500.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        indices=indices,
        timeout_millis=timeout_millis,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
