from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.set_project_favourite_body import SetProjectFavouriteBody
from ...models.set_project_favourite_response_200 import SetProjectFavouriteResponse200
from ...models.set_project_favourite_response_404 import SetProjectFavouriteResponse404
from ...types import Response


def _get_kwargs(
    project_id: UUID,
    *,
    body: SetProjectFavouriteBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/projects/{project_id}/fav".format(
            project_id=project_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]:
    if response.status_code == 200:
        response_200 = SetProjectFavouriteResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = SetProjectFavouriteResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    body: SetProjectFavouriteBody,
) -> Response[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]:
    """Favourite or unfavourite a project for the current user

     Sets or unsets the project as a favourite for the authenticated user. This is a user-specific action
    and is handled via the projects_users table.

    Args:
        project_id (UUID):
        body (SetProjectFavouriteBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    body: SetProjectFavouriteBody,
) -> Optional[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]:
    """Favourite or unfavourite a project for the current user

     Sets or unsets the project as a favourite for the authenticated user. This is a user-specific action
    and is handled via the projects_users table.

    Args:
        project_id (UUID):
        body (SetProjectFavouriteBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    body: SetProjectFavouriteBody,
) -> Response[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]:
    """Favourite or unfavourite a project for the current user

     Sets or unsets the project as a favourite for the authenticated user. This is a user-specific action
    and is handled via the projects_users table.

    Args:
        project_id (UUID):
        body (SetProjectFavouriteBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    body: SetProjectFavouriteBody,
) -> Optional[Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]]:
    """Favourite or unfavourite a project for the current user

     Sets or unsets the project as a favourite for the authenticated user. This is a user-specific action
    and is handled via the projects_users table.

    Args:
        project_id (UUID):
        body (SetProjectFavouriteBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SetProjectFavouriteResponse200, SetProjectFavouriteResponse404]
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            body=body,
        )
    ).parsed
