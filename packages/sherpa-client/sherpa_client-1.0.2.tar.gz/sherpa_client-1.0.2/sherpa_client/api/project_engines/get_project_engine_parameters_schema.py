from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_project_engine_parameters_schema_response_200 import (
    GetProjectEngineParametersSchemaResponse200,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    type_: str,
    engine: str,
    ui_schema: Union[Unset, bool] = False,
    preset_metadata_values: Union[Unset, bool] = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["type"] = type_

    params["engine"] = engine

    params["uiSchema"] = ui_schema

    params["presetMetadataValues"] = preset_metadata_values

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/engine_parameters".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetProjectEngineParametersSchemaResponse200]:
    if response.status_code == 200:
        response_200 = GetProjectEngineParametersSchemaResponse200.from_dict(
            response.json()
        )

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetProjectEngineParametersSchemaResponse200]:
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
    type_: str,
    engine: str,
    ui_schema: Union[Unset, bool] = False,
    preset_metadata_values: Union[Unset, bool] = True,
) -> Response[GetProjectEngineParametersSchemaResponse200]:
    """Get the list of parameters of the given engine or engine function

    Args:
        project_name (str):
        type_ (str):
        engine (str):
        ui_schema (Union[Unset, bool]):  Default: False.
        preset_metadata_values (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectEngineParametersSchemaResponse200]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        type_=type_,
        engine=engine,
        ui_schema=ui_schema,
        preset_metadata_values=preset_metadata_values,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    type_: str,
    engine: str,
    ui_schema: Union[Unset, bool] = False,
    preset_metadata_values: Union[Unset, bool] = True,
) -> Optional[GetProjectEngineParametersSchemaResponse200]:
    """Get the list of parameters of the given engine or engine function

    Args:
        project_name (str):
        type_ (str):
        engine (str):
        ui_schema (Union[Unset, bool]):  Default: False.
        preset_metadata_values (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectEngineParametersSchemaResponse200
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        type_=type_,
        engine=engine,
        ui_schema=ui_schema,
        preset_metadata_values=preset_metadata_values,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    type_: str,
    engine: str,
    ui_schema: Union[Unset, bool] = False,
    preset_metadata_values: Union[Unset, bool] = True,
) -> Response[GetProjectEngineParametersSchemaResponse200]:
    """Get the list of parameters of the given engine or engine function

    Args:
        project_name (str):
        type_ (str):
        engine (str):
        ui_schema (Union[Unset, bool]):  Default: False.
        preset_metadata_values (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectEngineParametersSchemaResponse200]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        type_=type_,
        engine=engine,
        ui_schema=ui_schema,
        preset_metadata_values=preset_metadata_values,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    type_: str,
    engine: str,
    ui_schema: Union[Unset, bool] = False,
    preset_metadata_values: Union[Unset, bool] = True,
) -> Optional[GetProjectEngineParametersSchemaResponse200]:
    """Get the list of parameters of the given engine or engine function

    Args:
        project_name (str):
        type_ (str):
        engine (str):
        ui_schema (Union[Unset, bool]):  Default: False.
        preset_metadata_values (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectEngineParametersSchemaResponse200
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            type_=type_,
            engine=engine,
            ui_schema=ui_schema,
            preset_metadata_values=preset_metadata_values,
        )
    ).parsed
