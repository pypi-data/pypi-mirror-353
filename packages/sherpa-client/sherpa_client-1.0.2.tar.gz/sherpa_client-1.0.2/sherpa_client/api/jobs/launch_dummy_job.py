from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.sherpa_job_bean import SherpaJobBean
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    job_desc: Union[Unset, str] = "All work and no play makes Jack a dull boy",
    timeout: Union[Unset, int] = 60,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["job_desc"] = job_desc

    params["timeout"] = timeout

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_name}/job".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SherpaJobBean]:
    if response.status_code == 200:
        response_200 = SherpaJobBean.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SherpaJobBean]:
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
    job_desc: Union[Unset, str] = "All work and no play makes Jack a dull boy",
    timeout: Union[Unset, int] = 60,
) -> Response[SherpaJobBean]:
    """create a dummy job

    Args:
        project_name (str):
        job_desc (Union[Unset, str]):  Default: 'All work and no play makes Jack a dull boy'.
        timeout (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SherpaJobBean]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        job_desc=job_desc,
        timeout=timeout,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    job_desc: Union[Unset, str] = "All work and no play makes Jack a dull boy",
    timeout: Union[Unset, int] = 60,
) -> Optional[SherpaJobBean]:
    """create a dummy job

    Args:
        project_name (str):
        job_desc (Union[Unset, str]):  Default: 'All work and no play makes Jack a dull boy'.
        timeout (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SherpaJobBean
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        job_desc=job_desc,
        timeout=timeout,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    job_desc: Union[Unset, str] = "All work and no play makes Jack a dull boy",
    timeout: Union[Unset, int] = 60,
) -> Response[SherpaJobBean]:
    """create a dummy job

    Args:
        project_name (str):
        job_desc (Union[Unset, str]):  Default: 'All work and no play makes Jack a dull boy'.
        timeout (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SherpaJobBean]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        job_desc=job_desc,
        timeout=timeout,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    job_desc: Union[Unset, str] = "All work and no play makes Jack a dull boy",
    timeout: Union[Unset, int] = 60,
) -> Optional[SherpaJobBean]:
    """create a dummy job

    Args:
        project_name (str):
        job_desc (Union[Unset, str]):  Default: 'All work and no play makes Jack a dull boy'.
        timeout (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SherpaJobBean
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            job_desc=job_desc,
            timeout=timeout,
        )
    ).parsed
