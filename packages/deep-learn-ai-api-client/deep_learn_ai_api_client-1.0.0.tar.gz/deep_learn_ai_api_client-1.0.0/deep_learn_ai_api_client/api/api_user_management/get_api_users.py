from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_users_response_200_item import GetApiUsersResponse200Item
from ...models.get_api_users_response_401 import GetApiUsersResponse401
from ...models.get_api_users_response_403 import GetApiUsersResponse403
from ...models.get_api_users_response_500 import GetApiUsersResponse500
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api-users",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list["GetApiUsersResponse200Item"]]
]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetApiUsersResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 401:
        response_401 = GetApiUsersResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = GetApiUsersResponse403.from_dict(response.json())

        return response_403
    if response.status_code == 500:
        response_500 = GetApiUsersResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list["GetApiUsersResponse200Item"]]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list["GetApiUsersResponse200Item"]]
]:
    """List API Users

     Get all API users (Admin only)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list['GetApiUsersResponse200Item']]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list["GetApiUsersResponse200Item"]]
]:
    """List API Users

     Get all API users (Admin only)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list['GetApiUsersResponse200Item']]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list["GetApiUsersResponse200Item"]]
]:
    """List API Users

     Get all API users (Admin only)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list['GetApiUsersResponse200Item']]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list["GetApiUsersResponse200Item"]]
]:
    """List API Users

     Get all API users (Admin only)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetApiUsersResponse401, GetApiUsersResponse403, GetApiUsersResponse500, list['GetApiUsersResponse200Item']]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
