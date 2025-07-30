from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_activity import ProjectActivity
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    *,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["nextToken"] = next_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/activity".format(
            project_id=project_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ProjectActivity]]:
    if response.status_code == 200:
        response_200 = ProjectActivity.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ProjectActivity]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ProjectActivity]]:
    """Get activity for a project

    Args:
        project_id (str):
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProjectActivity]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        limit=limit,
        next_token=next_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ProjectActivity]]:
    """Get activity for a project

    Args:
        project_id (str):
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProjectActivity]
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        limit=limit,
        next_token=next_token,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ProjectActivity]]:
    """Get activity for a project

    Args:
        project_id (str):
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProjectActivity]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        limit=limit,
        next_token=next_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    next_token: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ProjectActivity]]:
    """Get activity for a project

    Args:
        project_id (str):
        limit (Union[Unset, int]):
        next_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProjectActivity]
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            limit=limit,
            next_token=next_token,
        )
    ).parsed
