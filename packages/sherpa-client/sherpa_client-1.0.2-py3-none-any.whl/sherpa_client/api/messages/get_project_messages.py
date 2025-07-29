from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_project_messages_output_format import GetProjectMessagesOutputFormat
from ...models.get_project_messages_scopes_item import GetProjectMessagesScopesItem
from ...models.project_message import ProjectMessage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    language: Union[Unset, str] = UNSET,
    read: Union[Unset, bool] = UNSET,
    group: Union[Unset, list[str]] = UNSET,
    scopes: Union[Unset, list[GetProjectMessagesScopesItem]] = UNSET,
    output_format: Union[Unset, GetProjectMessagesOutputFormat] = UNSET,
    run_templates: Union[Unset, bool] = False,
    include_global: Union[Unset, bool] = False,
    output_fields: Union[Unset, str] = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["language"] = language

    params["read"] = read

    json_group: Union[Unset, list[str]] = UNSET
    if not isinstance(group, Unset):
        json_group = group

    params["group"] = json_group

    json_scopes: Union[Unset, list[str]] = UNSET
    if not isinstance(scopes, Unset):
        json_scopes = []
        for scopes_item_data in scopes:
            scopes_item = scopes_item_data.value
            json_scopes.append(scopes_item)

    params["scopes"] = json_scopes

    json_output_format: Union[Unset, str] = UNSET
    if not isinstance(output_format, Unset):
        json_output_format = output_format.value

    params["outputFormat"] = json_output_format

    params["runTemplates"] = run_templates

    params["includeGlobal"] = include_global

    params["outputFields"] = output_fields

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/messages".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["ProjectMessage"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_project_message_array_item_data in _response_200:
            componentsschemas_project_message_array_item = ProjectMessage.from_dict(
                componentsschemas_project_message_array_item_data
            )

            response_200.append(componentsschemas_project_message_array_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["ProjectMessage"]]:
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
    language: Union[Unset, str] = UNSET,
    read: Union[Unset, bool] = UNSET,
    group: Union[Unset, list[str]] = UNSET,
    scopes: Union[Unset, list[GetProjectMessagesScopesItem]] = UNSET,
    output_format: Union[Unset, GetProjectMessagesOutputFormat] = UNSET,
    run_templates: Union[Unset, bool] = False,
    include_global: Union[Unset, bool] = False,
    output_fields: Union[Unset, str] = UNSET,
) -> Response[list["ProjectMessage"]]:
    """Get messages of current user

    Args:
        project_name (str):
        language (Union[Unset, str]):
        read (Union[Unset, bool]):
        group (Union[Unset, list[str]]):
        scopes (Union[Unset, list[GetProjectMessagesScopesItem]]):
        output_format (Union[Unset, GetProjectMessagesOutputFormat]):
        run_templates (Union[Unset, bool]):  Default: False.
        include_global (Union[Unset, bool]):  Default: False.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ProjectMessage']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        language=language,
        read=read,
        group=group,
        scopes=scopes,
        output_format=output_format,
        run_templates=run_templates,
        include_global=include_global,
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
    language: Union[Unset, str] = UNSET,
    read: Union[Unset, bool] = UNSET,
    group: Union[Unset, list[str]] = UNSET,
    scopes: Union[Unset, list[GetProjectMessagesScopesItem]] = UNSET,
    output_format: Union[Unset, GetProjectMessagesOutputFormat] = UNSET,
    run_templates: Union[Unset, bool] = False,
    include_global: Union[Unset, bool] = False,
    output_fields: Union[Unset, str] = UNSET,
) -> Optional[list["ProjectMessage"]]:
    """Get messages of current user

    Args:
        project_name (str):
        language (Union[Unset, str]):
        read (Union[Unset, bool]):
        group (Union[Unset, list[str]]):
        scopes (Union[Unset, list[GetProjectMessagesScopesItem]]):
        output_format (Union[Unset, GetProjectMessagesOutputFormat]):
        run_templates (Union[Unset, bool]):  Default: False.
        include_global (Union[Unset, bool]):  Default: False.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ProjectMessage']
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        language=language,
        read=read,
        group=group,
        scopes=scopes,
        output_format=output_format,
        run_templates=run_templates,
        include_global=include_global,
        output_fields=output_fields,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    language: Union[Unset, str] = UNSET,
    read: Union[Unset, bool] = UNSET,
    group: Union[Unset, list[str]] = UNSET,
    scopes: Union[Unset, list[GetProjectMessagesScopesItem]] = UNSET,
    output_format: Union[Unset, GetProjectMessagesOutputFormat] = UNSET,
    run_templates: Union[Unset, bool] = False,
    include_global: Union[Unset, bool] = False,
    output_fields: Union[Unset, str] = UNSET,
) -> Response[list["ProjectMessage"]]:
    """Get messages of current user

    Args:
        project_name (str):
        language (Union[Unset, str]):
        read (Union[Unset, bool]):
        group (Union[Unset, list[str]]):
        scopes (Union[Unset, list[GetProjectMessagesScopesItem]]):
        output_format (Union[Unset, GetProjectMessagesOutputFormat]):
        run_templates (Union[Unset, bool]):  Default: False.
        include_global (Union[Unset, bool]):  Default: False.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ProjectMessage']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        language=language,
        read=read,
        group=group,
        scopes=scopes,
        output_format=output_format,
        run_templates=run_templates,
        include_global=include_global,
        output_fields=output_fields,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    language: Union[Unset, str] = UNSET,
    read: Union[Unset, bool] = UNSET,
    group: Union[Unset, list[str]] = UNSET,
    scopes: Union[Unset, list[GetProjectMessagesScopesItem]] = UNSET,
    output_format: Union[Unset, GetProjectMessagesOutputFormat] = UNSET,
    run_templates: Union[Unset, bool] = False,
    include_global: Union[Unset, bool] = False,
    output_fields: Union[Unset, str] = UNSET,
) -> Optional[list["ProjectMessage"]]:
    """Get messages of current user

    Args:
        project_name (str):
        language (Union[Unset, str]):
        read (Union[Unset, bool]):
        group (Union[Unset, list[str]]):
        scopes (Union[Unset, list[GetProjectMessagesScopesItem]]):
        output_format (Union[Unset, GetProjectMessagesOutputFormat]):
        run_templates (Union[Unset, bool]):  Default: False.
        include_global (Union[Unset, bool]):  Default: False.
        output_fields (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ProjectMessage']
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            language=language,
            read=read,
            group=group,
            scopes=scopes,
            output_format=output_format,
            run_templates=run_templates,
            include_global=include_global,
            output_fields=output_fields,
        )
    ).parsed
