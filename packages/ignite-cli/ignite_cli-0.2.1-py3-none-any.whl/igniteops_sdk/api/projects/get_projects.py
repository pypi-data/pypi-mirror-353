from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_projects_response_404 import GetProjectsResponse404
from ...models.get_projects_sort_by import GetProjectsSortBy
from ...models.get_projects_sort_order import GetProjectsSortOrder
from ...models.project_list import ProjectList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    language: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, GetProjectsSortBy] = UNSET,
    sort_order: Union[Unset, GetProjectsSortOrder] = UNSET,
    favs: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["nextToken"] = next_token

    params["language"] = language

    json_sort_by: Union[Unset, str] = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by.value

    params["sortBy"] = json_sort_by

    json_sort_order: Union[Unset, str] = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sortOrder"] = json_sort_order

    params["favs"] = favs

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[GetProjectsResponse404, ProjectList]]:
    if response.status_code == 200:
        response_200 = ProjectList.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = GetProjectsResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GetProjectsResponse404, ProjectList]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    language: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, GetProjectsSortBy] = UNSET,
    sort_order: Union[Unset, GetProjectsSortOrder] = UNSET,
    favs: Union[Unset, bool] = UNSET,
) -> Response[Union[GetProjectsResponse404, ProjectList]]:
    """Get user's projects

     Retrieves a paginated list of projects for the authenticated user.

    Args:
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):
        language (Union[Unset, str]):
        sort_by (Union[Unset, GetProjectsSortBy]):
        sort_order (Union[Unset, GetProjectsSortOrder]):
        favs (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetProjectsResponse404, ProjectList]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        next_token=next_token,
        language=language,
        sort_by=sort_by,
        sort_order=sort_order,
        favs=favs,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    language: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, GetProjectsSortBy] = UNSET,
    sort_order: Union[Unset, GetProjectsSortOrder] = UNSET,
    favs: Union[Unset, bool] = UNSET,
) -> Optional[Union[GetProjectsResponse404, ProjectList]]:
    """Get user's projects

     Retrieves a paginated list of projects for the authenticated user.

    Args:
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):
        language (Union[Unset, str]):
        sort_by (Union[Unset, GetProjectsSortBy]):
        sort_order (Union[Unset, GetProjectsSortOrder]):
        favs (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetProjectsResponse404, ProjectList]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        next_token=next_token,
        language=language,
        sort_by=sort_by,
        sort_order=sort_order,
        favs=favs,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    language: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, GetProjectsSortBy] = UNSET,
    sort_order: Union[Unset, GetProjectsSortOrder] = UNSET,
    favs: Union[Unset, bool] = UNSET,
) -> Response[Union[GetProjectsResponse404, ProjectList]]:
    """Get user's projects

     Retrieves a paginated list of projects for the authenticated user.

    Args:
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):
        language (Union[Unset, str]):
        sort_by (Union[Unset, GetProjectsSortBy]):
        sort_order (Union[Unset, GetProjectsSortOrder]):
        favs (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetProjectsResponse404, ProjectList]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        next_token=next_token,
        language=language,
        sort_by=sort_by,
        sort_order=sort_order,
        favs=favs,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    language: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, GetProjectsSortBy] = UNSET,
    sort_order: Union[Unset, GetProjectsSortOrder] = UNSET,
    favs: Union[Unset, bool] = UNSET,
) -> Optional[Union[GetProjectsResponse404, ProjectList]]:
    """Get user's projects

     Retrieves a paginated list of projects for the authenticated user.

    Args:
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):
        language (Union[Unset, str]):
        sort_by (Union[Unset, GetProjectsSortBy]):
        sort_order (Union[Unset, GetProjectsSortOrder]):
        favs (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetProjectsResponse404, ProjectList]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            next_token=next_token,
            language=language,
            sort_by=sort_by,
            sort_order=sort_order,
            favs=favs,
        )
    ).parsed
