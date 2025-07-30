from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_users_body import PostApiUsersBody
from ...models.post_api_users_response_201 import PostApiUsersResponse201
from ...models.post_api_users_response_400 import PostApiUsersResponse400
from ...models.post_api_users_response_401 import PostApiUsersResponse401
from ...models.post_api_users_response_403 import PostApiUsersResponse403
from ...models.post_api_users_response_409 import PostApiUsersResponse409
from ...models.post_api_users_response_500 import PostApiUsersResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: PostApiUsersBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api-users",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        PostApiUsersResponse201,
        PostApiUsersResponse400,
        PostApiUsersResponse401,
        PostApiUsersResponse403,
        PostApiUsersResponse409,
        PostApiUsersResponse500,
    ]
]:
    if response.status_code == 201:
        response_201 = PostApiUsersResponse201.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = PostApiUsersResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = PostApiUsersResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = PostApiUsersResponse403.from_dict(response.json())

        return response_403
    if response.status_code == 409:
        response_409 = PostApiUsersResponse409.from_dict(response.json())

        return response_409
    if response.status_code == 500:
        response_500 = PostApiUsersResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        PostApiUsersResponse201,
        PostApiUsersResponse400,
        PostApiUsersResponse401,
        PostApiUsersResponse403,
        PostApiUsersResponse409,
        PostApiUsersResponse500,
    ]
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
    body: PostApiUsersBody,
) -> Response[
    Union[
        PostApiUsersResponse201,
        PostApiUsersResponse400,
        PostApiUsersResponse401,
        PostApiUsersResponse403,
        PostApiUsersResponse409,
        PostApiUsersResponse500,
    ]
]:
    """Create API User

     Create a new API user (Admin only)

    Args:
        body (PostApiUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostApiUsersResponse201, PostApiUsersResponse400, PostApiUsersResponse401, PostApiUsersResponse403, PostApiUsersResponse409, PostApiUsersResponse500]]
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
    body: PostApiUsersBody,
) -> Optional[
    Union[
        PostApiUsersResponse201,
        PostApiUsersResponse400,
        PostApiUsersResponse401,
        PostApiUsersResponse403,
        PostApiUsersResponse409,
        PostApiUsersResponse500,
    ]
]:
    """Create API User

     Create a new API user (Admin only)

    Args:
        body (PostApiUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostApiUsersResponse201, PostApiUsersResponse400, PostApiUsersResponse401, PostApiUsersResponse403, PostApiUsersResponse409, PostApiUsersResponse500]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiUsersBody,
) -> Response[
    Union[
        PostApiUsersResponse201,
        PostApiUsersResponse400,
        PostApiUsersResponse401,
        PostApiUsersResponse403,
        PostApiUsersResponse409,
        PostApiUsersResponse500,
    ]
]:
    """Create API User

     Create a new API user (Admin only)

    Args:
        body (PostApiUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostApiUsersResponse201, PostApiUsersResponse400, PostApiUsersResponse401, PostApiUsersResponse403, PostApiUsersResponse409, PostApiUsersResponse500]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PostApiUsersBody,
) -> Optional[
    Union[
        PostApiUsersResponse201,
        PostApiUsersResponse400,
        PostApiUsersResponse401,
        PostApiUsersResponse403,
        PostApiUsersResponse409,
        PostApiUsersResponse500,
    ]
]:
    """Create API User

     Create a new API user (Admin only)

    Args:
        body (PostApiUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostApiUsersResponse201, PostApiUsersResponse400, PostApiUsersResponse401, PostApiUsersResponse403, PostApiUsersResponse409, PostApiUsersResponse500]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
