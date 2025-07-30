from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_knowledges_id_documents_body import PostKnowledgesIdDocumentsBody
from ...models.post_knowledges_id_documents_response_201 import PostKnowledgesIdDocumentsResponse201
from ...models.post_knowledges_id_documents_response_400 import PostKnowledgesIdDocumentsResponse400
from ...models.post_knowledges_id_documents_response_401 import PostKnowledgesIdDocumentsResponse401
from ...models.post_knowledges_id_documents_response_404 import PostKnowledgesIdDocumentsResponse404
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: PostKnowledgesIdDocumentsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/knowledges/{id}/documents",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        PostKnowledgesIdDocumentsResponse201,
        PostKnowledgesIdDocumentsResponse400,
        PostKnowledgesIdDocumentsResponse401,
        PostKnowledgesIdDocumentsResponse404,
    ]
]:
    if response.status_code == 201:
        response_201 = PostKnowledgesIdDocumentsResponse201.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = PostKnowledgesIdDocumentsResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = PostKnowledgesIdDocumentsResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = PostKnowledgesIdDocumentsResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        PostKnowledgesIdDocumentsResponse201,
        PostKnowledgesIdDocumentsResponse400,
        PostKnowledgesIdDocumentsResponse401,
        PostKnowledgesIdDocumentsResponse404,
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
    body: PostKnowledgesIdDocumentsBody,
) -> Response[
    Union[
        PostKnowledgesIdDocumentsResponse201,
        PostKnowledgesIdDocumentsResponse400,
        PostKnowledgesIdDocumentsResponse401,
        PostKnowledgesIdDocumentsResponse404,
    ]
]:
    """Create Document

     Create a new document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        body (PostKnowledgesIdDocumentsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostKnowledgesIdDocumentsResponse201, PostKnowledgesIdDocumentsResponse400, PostKnowledgesIdDocumentsResponse401, PostKnowledgesIdDocumentsResponse404]]
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
    body: PostKnowledgesIdDocumentsBody,
) -> Optional[
    Union[
        PostKnowledgesIdDocumentsResponse201,
        PostKnowledgesIdDocumentsResponse400,
        PostKnowledgesIdDocumentsResponse401,
        PostKnowledgesIdDocumentsResponse404,
    ]
]:
    """Create Document

     Create a new document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        body (PostKnowledgesIdDocumentsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostKnowledgesIdDocumentsResponse201, PostKnowledgesIdDocumentsResponse400, PostKnowledgesIdDocumentsResponse401, PostKnowledgesIdDocumentsResponse404]
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
    body: PostKnowledgesIdDocumentsBody,
) -> Response[
    Union[
        PostKnowledgesIdDocumentsResponse201,
        PostKnowledgesIdDocumentsResponse400,
        PostKnowledgesIdDocumentsResponse401,
        PostKnowledgesIdDocumentsResponse404,
    ]
]:
    """Create Document

     Create a new document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        body (PostKnowledgesIdDocumentsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostKnowledgesIdDocumentsResponse201, PostKnowledgesIdDocumentsResponse400, PostKnowledgesIdDocumentsResponse401, PostKnowledgesIdDocumentsResponse404]]
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
    body: PostKnowledgesIdDocumentsBody,
) -> Optional[
    Union[
        PostKnowledgesIdDocumentsResponse201,
        PostKnowledgesIdDocumentsResponse400,
        PostKnowledgesIdDocumentsResponse401,
        PostKnowledgesIdDocumentsResponse404,
    ]
]:
    """Create Document

     Create a new document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        body (PostKnowledgesIdDocumentsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostKnowledgesIdDocumentsResponse201, PostKnowledgesIdDocumentsResponse400, PostKnowledgesIdDocumentsResponse401, PostKnowledgesIdDocumentsResponse404]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
