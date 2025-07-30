from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_v1_users_response_200_item import GetV1UsersResponse200Item
from ...types import UNSET, Response


def _get_kwargs(
    *,
    q: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/users",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["GetV1UsersResponse200Item"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetV1UsersResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, list["GetV1UsersResponse200Item"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    q: str,
) -> Response[Union[Any, list["GetV1UsersResponse200Item"]]]:
    """Search users by name or email

     Search for users by name or email. Requires at least 3 consecutive letters in the search string. -
    If searching by email (must provide full email address), the response will include the user's full
    name and email if found. - If searching by name, the response will include masked name and masked
    email for each user for privacy.

    Args:
        q (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['GetV1UsersResponse200Item']]]
    """

    kwargs = _get_kwargs(
        q=q,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    q: str,
) -> Optional[Union[Any, list["GetV1UsersResponse200Item"]]]:
    """Search users by name or email

     Search for users by name or email. Requires at least 3 consecutive letters in the search string. -
    If searching by email (must provide full email address), the response will include the user's full
    name and email if found. - If searching by name, the response will include masked name and masked
    email for each user for privacy.

    Args:
        q (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['GetV1UsersResponse200Item']]
    """

    return sync_detailed(
        client=client,
        q=q,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    q: str,
) -> Response[Union[Any, list["GetV1UsersResponse200Item"]]]:
    """Search users by name or email

     Search for users by name or email. Requires at least 3 consecutive letters in the search string. -
    If searching by email (must provide full email address), the response will include the user's full
    name and email if found. - If searching by name, the response will include masked name and masked
    email for each user for privacy.

    Args:
        q (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['GetV1UsersResponse200Item']]]
    """

    kwargs = _get_kwargs(
        q=q,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    q: str,
) -> Optional[Union[Any, list["GetV1UsersResponse200Item"]]]:
    """Search users by name or email

     Search for users by name or email. Requires at least 3 consecutive letters in the search string. -
    If searching by email (must provide full email address), the response will include the user's full
    name and email if found. - If searching by name, the response will include masked name and masked
    email for each user for privacy.

    Args:
        q (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['GetV1UsersResponse200Item']]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
        )
    ).parsed
