from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_team_member import ProjectTeamMember
from ...models.project_team_update_request import ProjectTeamUpdateRequest
from ...types import Response


def _get_kwargs(
    project_id: str,
    user_id: str,
    *,
    body: ProjectTeamUpdateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/projects/{project_id}/team/{user_id}".format(
            project_id=project_id,
            user_id=user_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ProjectTeamMember]]:
    if response.status_code == 200:
        response_200 = ProjectTeamMember.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
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
) -> Response[Union[Any, ProjectTeamMember]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: ProjectTeamUpdateRequest,
) -> Response[Union[Any, ProjectTeamMember]]:
    """Update a team member's role

     Changes the user's role in the project.

    Args:
        project_id (str):
        user_id (str):
        body (ProjectTeamUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProjectTeamMember]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: ProjectTeamUpdateRequest,
) -> Optional[Union[Any, ProjectTeamMember]]:
    """Update a team member's role

     Changes the user's role in the project.

    Args:
        project_id (str):
        user_id (str):
        body (ProjectTeamUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProjectTeamMember]
    """

    return sync_detailed(
        project_id=project_id,
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: ProjectTeamUpdateRequest,
) -> Response[Union[Any, ProjectTeamMember]]:
    """Update a team member's role

     Changes the user's role in the project.

    Args:
        project_id (str):
        user_id (str):
        body (ProjectTeamUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProjectTeamMember]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: ProjectTeamUpdateRequest,
) -> Optional[Union[Any, ProjectTeamMember]]:
    """Update a team member's role

     Changes the user's role in the project.

    Args:
        project_id (str):
        user_id (str):
        body (ProjectTeamUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProjectTeamMember]
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
