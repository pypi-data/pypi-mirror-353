from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_engine_parameters_schema_response_200 import (
    GetEngineParametersSchemaResponse200,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service: str,
    *,
    nature: str,
    function: str,
    include_embedded_services: Union[Unset, bool] = False,
    ui_schema: Union[Unset, bool] = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["nature"] = nature

    params["function"] = function

    params["includeEmbeddedServices"] = include_embedded_services

    params["uiSchema"] = ui_schema

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/services/{service}/parameters".format(
            service=service,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, GetEngineParametersSchemaResponse200]]:
    if response.status_code == 200:
        response_200 = GetEngineParametersSchemaResponse200.from_dict(response.json())

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
) -> Response[Union[Any, GetEngineParametersSchemaResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    service: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nature: str,
    function: str,
    include_embedded_services: Union[Unset, bool] = False,
    ui_schema: Union[Unset, bool] = False,
) -> Response[Union[Any, GetEngineParametersSchemaResponse200]]:
    """get the options of the given service in JSON schema format

    Args:
        service (str):
        nature (str):
        function (str):
        include_embedded_services (Union[Unset, bool]):  Default: False.
        ui_schema (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetEngineParametersSchemaResponse200]]
    """

    kwargs = _get_kwargs(
        service=service,
        nature=nature,
        function=function,
        include_embedded_services=include_embedded_services,
        ui_schema=ui_schema,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    service: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nature: str,
    function: str,
    include_embedded_services: Union[Unset, bool] = False,
    ui_schema: Union[Unset, bool] = False,
) -> Optional[Union[Any, GetEngineParametersSchemaResponse200]]:
    """get the options of the given service in JSON schema format

    Args:
        service (str):
        nature (str):
        function (str):
        include_embedded_services (Union[Unset, bool]):  Default: False.
        ui_schema (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetEngineParametersSchemaResponse200]
    """

    return sync_detailed(
        service=service,
        client=client,
        nature=nature,
        function=function,
        include_embedded_services=include_embedded_services,
        ui_schema=ui_schema,
    ).parsed


async def asyncio_detailed(
    service: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nature: str,
    function: str,
    include_embedded_services: Union[Unset, bool] = False,
    ui_schema: Union[Unset, bool] = False,
) -> Response[Union[Any, GetEngineParametersSchemaResponse200]]:
    """get the options of the given service in JSON schema format

    Args:
        service (str):
        nature (str):
        function (str):
        include_embedded_services (Union[Unset, bool]):  Default: False.
        ui_schema (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetEngineParametersSchemaResponse200]]
    """

    kwargs = _get_kwargs(
        service=service,
        nature=nature,
        function=function,
        include_embedded_services=include_embedded_services,
        ui_schema=ui_schema,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nature: str,
    function: str,
    include_embedded_services: Union[Unset, bool] = False,
    ui_schema: Union[Unset, bool] = False,
) -> Optional[Union[Any, GetEngineParametersSchemaResponse200]]:
    """get the options of the given service in JSON schema format

    Args:
        service (str):
        nature (str):
        function (str):
        include_embedded_services (Union[Unset, bool]):  Default: False.
        ui_schema (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetEngineParametersSchemaResponse200]
    """

    return (
        await asyncio_detailed(
            service=service,
            client=client,
            nature=nature,
            function=function,
            include_embedded_services=include_embedded_services,
            ui_schema=ui_schema,
        )
    ).parsed
