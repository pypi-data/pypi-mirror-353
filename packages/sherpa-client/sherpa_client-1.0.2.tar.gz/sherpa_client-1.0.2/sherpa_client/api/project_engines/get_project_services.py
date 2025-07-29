from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_service_record import HttpServiceRecord
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    name: Union[Unset, str] = "",
    api: Union[Unset, str] = "",
    engine: Union[Unset, str] = "",
    function: Union[Unset, str] = "",
    type_: Union[Unset, str] = "",
    version: Union[Unset, str] = "",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["name"] = name

    params["api"] = api

    params["engine"] = engine

    params["function"] = function

    params["type"] = type_

    params["version"] = version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/services".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["HttpServiceRecord"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_http_service_record_array_item_data in _response_200:
            componentsschemas_http_service_record_array_item = (
                HttpServiceRecord.from_dict(
                    componentsschemas_http_service_record_array_item_data
                )
            )

            response_200.append(componentsschemas_http_service_record_array_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["HttpServiceRecord"]]:
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
    name: Union[Unset, str] = "",
    api: Union[Unset, str] = "",
    engine: Union[Unset, str] = "",
    function: Union[Unset, str] = "",
    type_: Union[Unset, str] = "",
    version: Union[Unset, str] = "",
) -> Response[list["HttpServiceRecord"]]:
    """Filter the list of services available for this project

    Args:
        project_name (str):
        name (Union[Unset, str]):  Default: ''.
        api (Union[Unset, str]):  Default: ''.
        engine (Union[Unset, str]):  Default: ''.
        function (Union[Unset, str]):  Default: ''.
        type_ (Union[Unset, str]):  Default: ''.
        version (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['HttpServiceRecord']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        name=name,
        api=api,
        engine=engine,
        function=function,
        type_=type_,
        version=version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    name: Union[Unset, str] = "",
    api: Union[Unset, str] = "",
    engine: Union[Unset, str] = "",
    function: Union[Unset, str] = "",
    type_: Union[Unset, str] = "",
    version: Union[Unset, str] = "",
) -> Optional[list["HttpServiceRecord"]]:
    """Filter the list of services available for this project

    Args:
        project_name (str):
        name (Union[Unset, str]):  Default: ''.
        api (Union[Unset, str]):  Default: ''.
        engine (Union[Unset, str]):  Default: ''.
        function (Union[Unset, str]):  Default: ''.
        type_ (Union[Unset, str]):  Default: ''.
        version (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['HttpServiceRecord']
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        name=name,
        api=api,
        engine=engine,
        function=function,
        type_=type_,
        version=version,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    name: Union[Unset, str] = "",
    api: Union[Unset, str] = "",
    engine: Union[Unset, str] = "",
    function: Union[Unset, str] = "",
    type_: Union[Unset, str] = "",
    version: Union[Unset, str] = "",
) -> Response[list["HttpServiceRecord"]]:
    """Filter the list of services available for this project

    Args:
        project_name (str):
        name (Union[Unset, str]):  Default: ''.
        api (Union[Unset, str]):  Default: ''.
        engine (Union[Unset, str]):  Default: ''.
        function (Union[Unset, str]):  Default: ''.
        type_ (Union[Unset, str]):  Default: ''.
        version (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['HttpServiceRecord']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        name=name,
        api=api,
        engine=engine,
        function=function,
        type_=type_,
        version=version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    name: Union[Unset, str] = "",
    api: Union[Unset, str] = "",
    engine: Union[Unset, str] = "",
    function: Union[Unset, str] = "",
    type_: Union[Unset, str] = "",
    version: Union[Unset, str] = "",
) -> Optional[list["HttpServiceRecord"]]:
    """Filter the list of services available for this project

    Args:
        project_name (str):
        name (Union[Unset, str]):  Default: ''.
        api (Union[Unset, str]):  Default: ''.
        engine (Union[Unset, str]):  Default: ''.
        function (Union[Unset, str]):  Default: ''.
        type_ (Union[Unset, str]):  Default: ''.
        version (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['HttpServiceRecord']
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            name=name,
            api=api,
            engine=engine,
            function=function,
            type_=type_,
            version=version,
        )
    ).parsed
