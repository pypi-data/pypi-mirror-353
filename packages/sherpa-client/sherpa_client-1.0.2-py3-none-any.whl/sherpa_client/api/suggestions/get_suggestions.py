from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.suggestions_list import SuggestionsList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    from_: Union[Unset, int] = 0,
    size: Union[Unset, int] = 25,
    sort: Union[Unset, str] = "sampling",
    filter_: Union[Unset, str] = "",
    html_version: Union[Unset, bool] = False,
    facet: Union[Unset, bool] = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["from"] = from_

    params["size"] = size

    params["sort"] = sort

    params["filter"] = filter_

    params["htmlVersion"] = html_version

    params["facet"] = facet

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_name}/suggestions".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SuggestionsList]:
    if response.status_code == 200:
        response_200 = SuggestionsList.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SuggestionsList]:
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
    from_: Union[Unset, int] = 0,
    size: Union[Unset, int] = 25,
    sort: Union[Unset, str] = "sampling",
    filter_: Union[Unset, str] = "",
    html_version: Union[Unset, bool] = False,
    facet: Union[Unset, bool] = False,
) -> Response[SuggestionsList]:
    """Get suggestions according to the project nature

    Args:
        project_name (str):
        from_ (Union[Unset, int]):  Default: 0.
        size (Union[Unset, int]):  Default: 25.
        sort (Union[Unset, str]):  Default: 'sampling'.
        filter_ (Union[Unset, str]):  Default: ''.
        html_version (Union[Unset, bool]):  Default: False.
        facet (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuggestionsList]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        from_=from_,
        size=size,
        sort=sort,
        filter_=filter_,
        html_version=html_version,
        facet=facet,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    from_: Union[Unset, int] = 0,
    size: Union[Unset, int] = 25,
    sort: Union[Unset, str] = "sampling",
    filter_: Union[Unset, str] = "",
    html_version: Union[Unset, bool] = False,
    facet: Union[Unset, bool] = False,
) -> Optional[SuggestionsList]:
    """Get suggestions according to the project nature

    Args:
        project_name (str):
        from_ (Union[Unset, int]):  Default: 0.
        size (Union[Unset, int]):  Default: 25.
        sort (Union[Unset, str]):  Default: 'sampling'.
        filter_ (Union[Unset, str]):  Default: ''.
        html_version (Union[Unset, bool]):  Default: False.
        facet (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuggestionsList
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        from_=from_,
        size=size,
        sort=sort,
        filter_=filter_,
        html_version=html_version,
        facet=facet,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    from_: Union[Unset, int] = 0,
    size: Union[Unset, int] = 25,
    sort: Union[Unset, str] = "sampling",
    filter_: Union[Unset, str] = "",
    html_version: Union[Unset, bool] = False,
    facet: Union[Unset, bool] = False,
) -> Response[SuggestionsList]:
    """Get suggestions according to the project nature

    Args:
        project_name (str):
        from_ (Union[Unset, int]):  Default: 0.
        size (Union[Unset, int]):  Default: 25.
        sort (Union[Unset, str]):  Default: 'sampling'.
        filter_ (Union[Unset, str]):  Default: ''.
        html_version (Union[Unset, bool]):  Default: False.
        facet (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuggestionsList]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        from_=from_,
        size=size,
        sort=sort,
        filter_=filter_,
        html_version=html_version,
        facet=facet,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    from_: Union[Unset, int] = 0,
    size: Union[Unset, int] = 25,
    sort: Union[Unset, str] = "sampling",
    filter_: Union[Unset, str] = "",
    html_version: Union[Unset, bool] = False,
    facet: Union[Unset, bool] = False,
) -> Optional[SuggestionsList]:
    """Get suggestions according to the project nature

    Args:
        project_name (str):
        from_ (Union[Unset, int]):  Default: 0.
        size (Union[Unset, int]):  Default: 25.
        sort (Union[Unset, str]):  Default: 'sampling'.
        filter_ (Union[Unset, str]):  Default: ''.
        html_version (Union[Unset, bool]):  Default: False.
        facet (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuggestionsList
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            from_=from_,
            size=size,
            sort=sort,
            filter_=filter_,
            html_version=html_version,
            facet=facet,
        )
    ).parsed
