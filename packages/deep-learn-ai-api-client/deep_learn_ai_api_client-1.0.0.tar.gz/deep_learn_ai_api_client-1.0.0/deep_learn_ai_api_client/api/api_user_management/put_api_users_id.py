from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.put_api_users_id_body import PutApiUsersIdBody
from ...models.put_api_users_id_response_200 import PutApiUsersIdResponse200
from ...models.put_api_users_id_response_400 import PutApiUsersIdResponse400
from ...models.put_api_users_id_response_401 import PutApiUsersIdResponse401
from ...models.put_api_users_id_response_403 import PutApiUsersIdResponse403
from ...models.put_api_users_id_response_404 import PutApiUsersIdResponse404
from ...models.put_api_users_id_response_409 import PutApiUsersIdResponse409
from ...models.put_api_users_id_response_500 import PutApiUsersIdResponse500
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: PutApiUsersIdBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api-users/{id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        PutApiUsersIdResponse200,
        PutApiUsersIdResponse400,
        PutApiUsersIdResponse401,
        PutApiUsersIdResponse403,
        PutApiUsersIdResponse404,
        PutApiUsersIdResponse409,
        PutApiUsersIdResponse500,
    ]
]:
    if response.status_code == 200:
        response_200 = PutApiUsersIdResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = PutApiUsersIdResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = PutApiUsersIdResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = PutApiUsersIdResponse403.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = PutApiUsersIdResponse404.from_dict(response.json())

        return response_404
    if response.status_code == 409:
        response_409 = PutApiUsersIdResponse409.from_dict(response.json())

        return response_409
    if response.status_code == 500:
        response_500 = PutApiUsersIdResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        PutApiUsersIdResponse200,
        PutApiUsersIdResponse400,
        PutApiUsersIdResponse401,
        PutApiUsersIdResponse403,
        PutApiUsersIdResponse404,
        PutApiUsersIdResponse409,
        PutApiUsersIdResponse500,
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
    body: PutApiUsersIdBody,
) -> Response[
    Union[
        PutApiUsersIdResponse200,
        PutApiUsersIdResponse400,
        PutApiUsersIdResponse401,
        PutApiUsersIdResponse403,
        PutApiUsersIdResponse404,
        PutApiUsersIdResponse409,
        PutApiUsersIdResponse500,
    ]
]:
    """Update API User

     Update an existing API user (Admin only)

    Args:
        id (str):  Example: user123.
        body (PutApiUsersIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PutApiUsersIdResponse200, PutApiUsersIdResponse400, PutApiUsersIdResponse401, PutApiUsersIdResponse403, PutApiUsersIdResponse404, PutApiUsersIdResponse409, PutApiUsersIdResponse500]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    body: PutApiUsersIdBody,
) -> Optional[
    Union[
        PutApiUsersIdResponse200,
        PutApiUsersIdResponse400,
        PutApiUsersIdResponse401,
        PutApiUsersIdResponse403,
        PutApiUsersIdResponse404,
        PutApiUsersIdResponse409,
        PutApiUsersIdResponse500,
    ]
]:
    """Update API User

     Update an existing API user (Admin only)

    Args:
        id (str):  Example: user123.
        body (PutApiUsersIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PutApiUsersIdResponse200, PutApiUsersIdResponse400, PutApiUsersIdResponse401, PutApiUsersIdResponse403, PutApiUsersIdResponse404, PutApiUsersIdResponse409, PutApiUsersIdResponse500]
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: PutApiUsersIdBody,
) -> Response[
    Union[
        PutApiUsersIdResponse200,
        PutApiUsersIdResponse400,
        PutApiUsersIdResponse401,
        PutApiUsersIdResponse403,
        PutApiUsersIdResponse404,
        PutApiUsersIdResponse409,
        PutApiUsersIdResponse500,
    ]
]:
    """Update API User

     Update an existing API user (Admin only)

    Args:
        id (str):  Example: user123.
        body (PutApiUsersIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PutApiUsersIdResponse200, PutApiUsersIdResponse400, PutApiUsersIdResponse401, PutApiUsersIdResponse403, PutApiUsersIdResponse404, PutApiUsersIdResponse409, PutApiUsersIdResponse500]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    body: PutApiUsersIdBody,
) -> Optional[
    Union[
        PutApiUsersIdResponse200,
        PutApiUsersIdResponse400,
        PutApiUsersIdResponse401,
        PutApiUsersIdResponse403,
        PutApiUsersIdResponse404,
        PutApiUsersIdResponse409,
        PutApiUsersIdResponse500,
    ]
]:
    """Update API User

     Update an existing API user (Admin only)

    Args:
        id (str):  Example: user123.
        body (PutApiUsersIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PutApiUsersIdResponse200, PutApiUsersIdResponse400, PutApiUsersIdResponse401, PutApiUsersIdResponse403, PutApiUsersIdResponse404, PutApiUsersIdResponse409, PutApiUsersIdResponse500]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
