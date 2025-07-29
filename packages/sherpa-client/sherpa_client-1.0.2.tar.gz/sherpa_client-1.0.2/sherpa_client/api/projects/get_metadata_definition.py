from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.metadata_definition import MetadataDefinition
from ...types import Response


def _get_kwargs(
    project_name: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/metadata".format(
            project_name=project_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["MetadataDefinition"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_metadata_definition_array_item_data in _response_200:
            componentsschemas_metadata_definition_array_item = (
                MetadataDefinition.from_dict(
                    componentsschemas_metadata_definition_array_item_data
                )
            )

            response_200.append(componentsschemas_metadata_definition_array_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["MetadataDefinition"]]:
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
) -> Response[list["MetadataDefinition"]]:
    """get the list of known metadata in this project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MetadataDefinition']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[list["MetadataDefinition"]]:
    """get the list of known metadata in this project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MetadataDefinition']
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[list["MetadataDefinition"]]:
    """get the list of known metadata in this project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MetadataDefinition']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[list["MetadataDefinition"]]:
    """get the list of known metadata in this project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MetadataDefinition']
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
        )
    ).parsed
