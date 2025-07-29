from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.suggester import Suggester
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    tags: Union[Unset, str] = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["tags"] = tags

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/suggesters".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["Suggester"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_suggester_array_item_data in _response_200:
            componentsschemas_suggester_array_item = Suggester.from_dict(
                componentsschemas_suggester_array_item_data
            )

            response_200.append(componentsschemas_suggester_array_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Suggester"]]:
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
    tags: Union[Unset, str] = UNSET,
) -> Response[list["Suggester"]]:
    """List suggesters

    Args:
        project_name (str):
        tags (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Suggester']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        tags=tags,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    tags: Union[Unset, str] = UNSET,
) -> Optional[list["Suggester"]]:
    """List suggesters

    Args:
        project_name (str):
        tags (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Suggester']
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        tags=tags,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    tags: Union[Unset, str] = UNSET,
) -> Response[list["Suggester"]]:
    """List suggesters

    Args:
        project_name (str):
        tags (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Suggester']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        tags=tags,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    tags: Union[Unset, str] = UNSET,
) -> Optional[list["Suggester"]]:
    """List suggesters

    Args:
        project_name (str):
        tags (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Suggester']
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            tags=tags,
        )
    ).parsed
