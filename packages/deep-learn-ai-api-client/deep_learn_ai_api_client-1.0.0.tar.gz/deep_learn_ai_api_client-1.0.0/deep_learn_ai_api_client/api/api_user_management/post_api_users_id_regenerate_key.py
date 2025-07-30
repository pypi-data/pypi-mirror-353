from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_users_id_regenerate_key_response_200 import PostApiUsersIdRegenerateKeyResponse200
from ...models.post_api_users_id_regenerate_key_response_401 import PostApiUsersIdRegenerateKeyResponse401
from ...models.post_api_users_id_regenerate_key_response_403 import PostApiUsersIdRegenerateKeyResponse403
from ...models.post_api_users_id_regenerate_key_response_404 import PostApiUsersIdRegenerateKeyResponse404
from ...models.post_api_users_id_regenerate_key_response_500 import PostApiUsersIdRegenerateKeyResponse500
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api-users/{id}/regenerate-key",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        PostApiUsersIdRegenerateKeyResponse200,
        PostApiUsersIdRegenerateKeyResponse401,
        PostApiUsersIdRegenerateKeyResponse403,
        PostApiUsersIdRegenerateKeyResponse404,
        PostApiUsersIdRegenerateKeyResponse500,
    ]
]:
    if response.status_code == 200:
        response_200 = PostApiUsersIdRegenerateKeyResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = PostApiUsersIdRegenerateKeyResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = PostApiUsersIdRegenerateKeyResponse403.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = PostApiUsersIdRegenerateKeyResponse404.from_dict(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = PostApiUsersIdRegenerateKeyResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        PostApiUsersIdRegenerateKeyResponse200,
        PostApiUsersIdRegenerateKeyResponse401,
        PostApiUsersIdRegenerateKeyResponse403,
        PostApiUsersIdRegenerateKeyResponse404,
        PostApiUsersIdRegenerateKeyResponse500,
    ]
]:
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
) -> Response[
    Union[
        PostApiUsersIdRegenerateKeyResponse200,
        PostApiUsersIdRegenerateKeyResponse401,
        PostApiUsersIdRegenerateKeyResponse403,
        PostApiUsersIdRegenerateKeyResponse404,
        PostApiUsersIdRegenerateKeyResponse500,
    ]
]:
    """Regenerate API Key

     Regenerate API key for a user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostApiUsersIdRegenerateKeyResponse200, PostApiUsersIdRegenerateKeyResponse401, PostApiUsersIdRegenerateKeyResponse403, PostApiUsersIdRegenerateKeyResponse404, PostApiUsersIdRegenerateKeyResponse500]]
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
) -> Optional[
    Union[
        PostApiUsersIdRegenerateKeyResponse200,
        PostApiUsersIdRegenerateKeyResponse401,
        PostApiUsersIdRegenerateKeyResponse403,
        PostApiUsersIdRegenerateKeyResponse404,
        PostApiUsersIdRegenerateKeyResponse500,
    ]
]:
    """Regenerate API Key

     Regenerate API key for a user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostApiUsersIdRegenerateKeyResponse200, PostApiUsersIdRegenerateKeyResponse401, PostApiUsersIdRegenerateKeyResponse403, PostApiUsersIdRegenerateKeyResponse404, PostApiUsersIdRegenerateKeyResponse500]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        PostApiUsersIdRegenerateKeyResponse200,
        PostApiUsersIdRegenerateKeyResponse401,
        PostApiUsersIdRegenerateKeyResponse403,
        PostApiUsersIdRegenerateKeyResponse404,
        PostApiUsersIdRegenerateKeyResponse500,
    ]
]:
    """Regenerate API Key

     Regenerate API key for a user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostApiUsersIdRegenerateKeyResponse200, PostApiUsersIdRegenerateKeyResponse401, PostApiUsersIdRegenerateKeyResponse403, PostApiUsersIdRegenerateKeyResponse404, PostApiUsersIdRegenerateKeyResponse500]]
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
) -> Optional[
    Union[
        PostApiUsersIdRegenerateKeyResponse200,
        PostApiUsersIdRegenerateKeyResponse401,
        PostApiUsersIdRegenerateKeyResponse403,
        PostApiUsersIdRegenerateKeyResponse404,
        PostApiUsersIdRegenerateKeyResponse500,
    ]
]:
    """Regenerate API Key

     Regenerate API key for a user (Admin only)

    Args:
        id (str):  Example: user123.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostApiUsersIdRegenerateKeyResponse200, PostApiUsersIdRegenerateKeyResponse401, PostApiUsersIdRegenerateKeyResponse403, PostApiUsersIdRegenerateKeyResponse404, PostApiUsersIdRegenerateKeyResponse500]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
