from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_segment_context_context_output import GetSegmentContextContextOutput
from ...models.segment_contexts import SegmentContexts
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    document_identifier: str,
    segment_start: int,
    from_before: Union[Unset, int] = 0,
    size_before: Union[Unset, int] = 1,
    from_after: Union[Unset, int] = 0,
    size_after: Union[Unset, int] = 1,
    context_output: Union[
        Unset, GetSegmentContextContextOutput
    ] = GetSegmentContextContextOutput.SEGMENTS,
    include_annotations: Union[Unset, bool] = False,
    html_version: Union[Unset, bool] = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["documentIdentifier"] = document_identifier

    params["segmentStart"] = segment_start

    params["fromBefore"] = from_before

    params["sizeBefore"] = size_before

    params["fromAfter"] = from_after

    params["sizeAfter"] = size_after

    json_context_output: Union[Unset, str] = UNSET
    if not isinstance(context_output, Unset):
        json_context_output = context_output.value

    params["contextOutput"] = json_context_output

    params["includeAnnotations"] = include_annotations

    params["htmlVersion"] = html_version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_name}/segments/_context".format(
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SegmentContexts]:
    if response.status_code == 200:
        response_200 = SegmentContexts.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SegmentContexts]:
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
    document_identifier: str,
    segment_start: int,
    from_before: Union[Unset, int] = 0,
    size_before: Union[Unset, int] = 1,
    from_after: Union[Unset, int] = 0,
    size_after: Union[Unset, int] = 1,
    context_output: Union[
        Unset, GetSegmentContextContextOutput
    ] = GetSegmentContextContextOutput.SEGMENTS,
    include_annotations: Union[Unset, bool] = False,
    html_version: Union[Unset, bool] = False,
) -> Response[SegmentContexts]:
    """Get segments surrounding a segment

    Args:
        project_name (str):
        document_identifier (str):
        segment_start (int):
        from_before (Union[Unset, int]):  Default: 0.
        size_before (Union[Unset, int]):  Default: 1.
        from_after (Union[Unset, int]):  Default: 0.
        size_after (Union[Unset, int]):  Default: 1.
        context_output (Union[Unset, GetSegmentContextContextOutput]):  Default:
            GetSegmentContextContextOutput.SEGMENTS.
        include_annotations (Union[Unset, bool]):  Default: False.
        html_version (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SegmentContexts]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        document_identifier=document_identifier,
        segment_start=segment_start,
        from_before=from_before,
        size_before=size_before,
        from_after=from_after,
        size_after=size_after,
        context_output=context_output,
        include_annotations=include_annotations,
        html_version=html_version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    document_identifier: str,
    segment_start: int,
    from_before: Union[Unset, int] = 0,
    size_before: Union[Unset, int] = 1,
    from_after: Union[Unset, int] = 0,
    size_after: Union[Unset, int] = 1,
    context_output: Union[
        Unset, GetSegmentContextContextOutput
    ] = GetSegmentContextContextOutput.SEGMENTS,
    include_annotations: Union[Unset, bool] = False,
    html_version: Union[Unset, bool] = False,
) -> Optional[SegmentContexts]:
    """Get segments surrounding a segment

    Args:
        project_name (str):
        document_identifier (str):
        segment_start (int):
        from_before (Union[Unset, int]):  Default: 0.
        size_before (Union[Unset, int]):  Default: 1.
        from_after (Union[Unset, int]):  Default: 0.
        size_after (Union[Unset, int]):  Default: 1.
        context_output (Union[Unset, GetSegmentContextContextOutput]):  Default:
            GetSegmentContextContextOutput.SEGMENTS.
        include_annotations (Union[Unset, bool]):  Default: False.
        html_version (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SegmentContexts
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
        document_identifier=document_identifier,
        segment_start=segment_start,
        from_before=from_before,
        size_before=size_before,
        from_after=from_after,
        size_after=size_after,
        context_output=context_output,
        include_annotations=include_annotations,
        html_version=html_version,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    document_identifier: str,
    segment_start: int,
    from_before: Union[Unset, int] = 0,
    size_before: Union[Unset, int] = 1,
    from_after: Union[Unset, int] = 0,
    size_after: Union[Unset, int] = 1,
    context_output: Union[
        Unset, GetSegmentContextContextOutput
    ] = GetSegmentContextContextOutput.SEGMENTS,
    include_annotations: Union[Unset, bool] = False,
    html_version: Union[Unset, bool] = False,
) -> Response[SegmentContexts]:
    """Get segments surrounding a segment

    Args:
        project_name (str):
        document_identifier (str):
        segment_start (int):
        from_before (Union[Unset, int]):  Default: 0.
        size_before (Union[Unset, int]):  Default: 1.
        from_after (Union[Unset, int]):  Default: 0.
        size_after (Union[Unset, int]):  Default: 1.
        context_output (Union[Unset, GetSegmentContextContextOutput]):  Default:
            GetSegmentContextContextOutput.SEGMENTS.
        include_annotations (Union[Unset, bool]):  Default: False.
        html_version (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SegmentContexts]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        document_identifier=document_identifier,
        segment_start=segment_start,
        from_before=from_before,
        size_before=size_before,
        from_after=from_after,
        size_after=size_after,
        context_output=context_output,
        include_annotations=include_annotations,
        html_version=html_version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    document_identifier: str,
    segment_start: int,
    from_before: Union[Unset, int] = 0,
    size_before: Union[Unset, int] = 1,
    from_after: Union[Unset, int] = 0,
    size_after: Union[Unset, int] = 1,
    context_output: Union[
        Unset, GetSegmentContextContextOutput
    ] = GetSegmentContextContextOutput.SEGMENTS,
    include_annotations: Union[Unset, bool] = False,
    html_version: Union[Unset, bool] = False,
) -> Optional[SegmentContexts]:
    """Get segments surrounding a segment

    Args:
        project_name (str):
        document_identifier (str):
        segment_start (int):
        from_before (Union[Unset, int]):  Default: 0.
        size_before (Union[Unset, int]):  Default: 1.
        from_after (Union[Unset, int]):  Default: 0.
        size_after (Union[Unset, int]):  Default: 1.
        context_output (Union[Unset, GetSegmentContextContextOutput]):  Default:
            GetSegmentContextContextOutput.SEGMENTS.
        include_annotations (Union[Unset, bool]):  Default: False.
        html_version (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SegmentContexts
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            document_identifier=document_identifier,
            segment_start=segment_start,
            from_before=from_before,
            size_before=size_before,
            from_after=from_after,
            size_after=size_after,
            context_output=context_output,
            include_annotations=include_annotations,
            html_version=html_version,
        )
    ).parsed
