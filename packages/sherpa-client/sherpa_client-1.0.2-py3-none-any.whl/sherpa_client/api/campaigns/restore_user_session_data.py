from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_restoration_request import DataRestorationRequest
from ...models.sherpa_job_bean import SherpaJobBean
from ...types import Response


def _get_kwargs(
    project_name: str,
    campaign_id: str,
    *,
    body: DataRestorationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_name}/campaigns/{campaign_id}/_restore_data".format(
            project_name=project_name,
            campaign_id=campaign_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SherpaJobBean]]:
    if response.status_code == 200:
        response_200 = SherpaJobBean.from_dict(response.json())

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
) -> Response[Union[Any, SherpaJobBean]]:
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
    body: DataRestorationRequest,
) -> Response[Union[Any, SherpaJobBean]]:
    """restore user session data

    Args:
        project_name (str):
        campaign_id (str):
        body (DataRestorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SherpaJobBean]]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: DataRestorationRequest,
) -> Optional[Union[Any, SherpaJobBean]]:
    """restore user session data

    Args:
        project_name (str):
        campaign_id (str):
        body (DataRestorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SherpaJobBean]
    """

    return sync_detailed(
        project_name=project_name,
        campaign_id=campaign_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: DataRestorationRequest,
) -> Response[Union[Any, SherpaJobBean]]:
    """restore user session data

    Args:
        project_name (str):
        campaign_id (str):
        body (DataRestorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SherpaJobBean]]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        campaign_id=campaign_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    campaign_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: DataRestorationRequest,
) -> Optional[Union[Any, SherpaJobBean]]:
    """restore user session data

    Args:
        project_name (str):
        campaign_id (str):
        body (DataRestorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SherpaJobBean]
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            campaign_id=campaign_id,
            client=client,
            body=body,
        )
    ).parsed
