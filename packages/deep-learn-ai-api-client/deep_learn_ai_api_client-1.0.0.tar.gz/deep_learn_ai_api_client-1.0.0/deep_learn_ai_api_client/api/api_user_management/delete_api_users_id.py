from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_api_users_id_response_401 import DeleteApiUsersIdResponse401
from ...models.delete_api_users_id_response_403 import DeleteApiUsersIdResponse403
from ...models.delete_api_users_id_response_404 import DeleteApiUsersIdResponse404
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api-users/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 401:
        response_401 = DeleteApiUsersIdResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = DeleteApiUsersIdResponse403.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = DeleteApiUsersIdResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]:
    """Delete API User

     Delete an API user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]:
    """Delete API User

     Delete an API user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]:
    """Delete API User

     Delete an API user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]]:
    """Delete API User

     Delete an API user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteApiUsersIdResponse401, DeleteApiUsersIdResponse403, DeleteApiUsersIdResponse404]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
