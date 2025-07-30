from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_knowledges_id_response_200 import DeleteKnowledgesIdResponse200
from ...models.delete_knowledges_id_response_401 import DeleteKnowledgesIdResponse401
from ...models.delete_knowledges_id_response_404 import DeleteKnowledgesIdResponse404
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/knowledges/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]:
    if response.status_code == 200:
        response_200 = DeleteKnowledgesIdResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = DeleteKnowledgesIdResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = DeleteKnowledgesIdResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]:
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
) -> Response[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]:
    """Delete Knowledge Base

     Delete a knowledge base by ID

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]
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
) -> Optional[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]:
    """Delete Knowledge Base

     Delete a knowledge base by ID

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]:
    """Delete Knowledge Base

     Delete a knowledge base by ID

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]
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
) -> Optional[Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]]:
    """Delete Knowledge Base

     Delete a knowledge base by ID

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeleteKnowledgesIdResponse200, DeleteKnowledgesIdResponse401, DeleteKnowledgesIdResponse404]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
