from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_project_releases_response_200 import GetProjectReleasesResponse200
from ...types import Response


def _get_kwargs(
    project_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/releases".format(
            project_id=project_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetProjectReleasesResponse200]:
    if response.status_code == 200:
        response_200 = GetProjectReleasesResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetProjectReleasesResponse200]:
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
) -> Response[GetProjectReleasesResponse200]:
    """Get project releases

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectReleasesResponse200]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[GetProjectReleasesResponse200]:
    """Get project releases

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectReleasesResponse200
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetProjectReleasesResponse200]:
    """Get project releases

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectReleasesResponse200]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[GetProjectReleasesResponse200]:
    """Get project releases

    Args:
        project_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectReleasesResponse200
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
        )
    ).parsed
