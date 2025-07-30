from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_create_request import ProjectCreateRequest
from ...models.project_create_response import ProjectCreateResponse
from ...models.project_validate_request import ProjectValidateRequest
from ...models.project_validate_response import ProjectValidateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: Union["ProjectCreateRequest", "ProjectValidateRequest"],
    dry_run: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["dryRun"] = dry_run

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/projects",
        "params": params,
    }

    _body: dict[str, Any]
    if isinstance(body, ProjectCreateRequest):
        _body = body.to_dict()
    else:
        _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]:
    if response.status_code == 200:
        response_200 = ProjectValidateResponse.from_dict(response.json())

        return response_200
    if response.status_code == 202:
        response_202 = ProjectCreateResponse.from_dict(response.json())

        return response_202
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 409:
        response_409 = ProjectValidateResponse.from_dict(response.json())

        return response_409
    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Union["ProjectCreateRequest", "ProjectValidateRequest"],
    dry_run: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]:
    """Create a new project

     Initiates asynchronous creation of a new project; returns an execution ARN and initial status.

    Args:
        dry_run (Union[Unset, bool]):
        body (Union['ProjectCreateRequest', 'ProjectValidateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        dry_run=dry_run,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: Union["ProjectCreateRequest", "ProjectValidateRequest"],
    dry_run: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]:
    """Create a new project

     Initiates asynchronous creation of a new project; returns an execution ARN and initial status.

    Args:
        dry_run (Union[Unset, bool]):
        body (Union['ProjectCreateRequest', 'ProjectValidateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProjectCreateResponse, ProjectValidateResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
        dry_run=dry_run,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union["ProjectCreateRequest", "ProjectValidateRequest"],
    dry_run: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]:
    """Create a new project

     Initiates asynchronous creation of a new project; returns an execution ARN and initial status.

    Args:
        dry_run (Union[Unset, bool]):
        body (Union['ProjectCreateRequest', 'ProjectValidateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        dry_run=dry_run,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Union["ProjectCreateRequest", "ProjectValidateRequest"],
    dry_run: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ProjectCreateResponse, ProjectValidateResponse]]:
    """Create a new project

     Initiates asynchronous creation of a new project; returns an execution ARN and initial status.

    Args:
        dry_run (Union[Unset, bool]):
        body (Union['ProjectCreateRequest', 'ProjectValidateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProjectCreateResponse, ProjectValidateResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            dry_run=dry_run,
        )
    ).parsed
