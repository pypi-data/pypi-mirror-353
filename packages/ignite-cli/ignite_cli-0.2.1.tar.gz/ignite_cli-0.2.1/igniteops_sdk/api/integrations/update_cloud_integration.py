from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cloud_integration_response import CloudIntegrationResponse
from ...models.cloud_integration_update_request import CloudIntegrationUpdateRequest
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    integration_id: str,
    *,
    body: CloudIntegrationUpdateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/integrations/cloud/{integration_id}".format(
            integration_id=integration_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CloudIntegrationResponse, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = CloudIntegrationResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
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
    integration_id: str,
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationUpdateRequest,
) -> Response[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Update a cloud integration

     Updates the integration with the customer's IAM Role ARN after they have created it. This completes
    the onboarding process.

    Args:
        integration_id (str):
        body (CloudIntegrationUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CloudIntegrationResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        integration_id=integration_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    integration_id: str,
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationUpdateRequest,
) -> Optional[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Update a cloud integration

     Updates the integration with the customer's IAM Role ARN after they have created it. This completes
    the onboarding process.

    Args:
        integration_id (str):
        body (CloudIntegrationUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CloudIntegrationResponse, ErrorResponse]
    """

    return sync_detailed(
        integration_id=integration_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    integration_id: str,
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationUpdateRequest,
) -> Response[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Update a cloud integration

     Updates the integration with the customer's IAM Role ARN after they have created it. This completes
    the onboarding process.

    Args:
        integration_id (str):
        body (CloudIntegrationUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CloudIntegrationResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        integration_id=integration_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    integration_id: str,
    *,
    client: AuthenticatedClient,
    body: CloudIntegrationUpdateRequest,
) -> Optional[Union[CloudIntegrationResponse, ErrorResponse]]:
    """Update a cloud integration

     Updates the integration with the customer's IAM Role ARN after they have created it. This completes
    the onboarding process.

    Args:
        integration_id (str):
        body (CloudIntegrationUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CloudIntegrationResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            integration_id=integration_id,
            client=client,
            body=body,
        )
    ).parsed
