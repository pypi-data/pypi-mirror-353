from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cloud_integration_request import CloudIntegrationRequest
from ...models.cloud_integration_response import CloudIntegrationResponse
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    *,
    body: CloudIntegrationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/integrations/cloud",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CloudIntegrationResponse, ErrorResponse]]:
    if response.status_code == 201:
        response_201 = CloudIntegrationResponse.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CloudIntegrationResponse, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationRequest,
) -> Response[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Create a cloud integration

     Initiates a new cloud integration for the authenticated user. Returns an integration_id and
    external_id for customer onboarding. The role ARN is not required at creation time.

    Args:
        body (CloudIntegrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CloudIntegrationResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationRequest,
) -> Optional[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Create a cloud integration

     Initiates a new cloud integration for the authenticated user. Returns an integration_id and
    external_id for customer onboarding. The role ARN is not required at creation time.

    Args:
        body (CloudIntegrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CloudIntegrationResponse, ErrorResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationRequest,
) -> Response[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Create a cloud integration

     Initiates a new cloud integration for the authenticated user. Returns an integration_id and
    external_id for customer onboarding. The role ARN is not required at creation time.

    Args:
        body (CloudIntegrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CloudIntegrationResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationRequest,
) -> Optional[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Create a cloud integration

     Initiates a new cloud integration for the authenticated user. Returns an integration_id and
    external_id for customer onboarding. The role ARN is not required at creation time.

    Args:
        body (CloudIntegrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CloudIntegrationResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
