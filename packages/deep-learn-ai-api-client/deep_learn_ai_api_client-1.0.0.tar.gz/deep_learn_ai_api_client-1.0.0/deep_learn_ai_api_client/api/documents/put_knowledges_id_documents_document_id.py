from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.put_knowledges_id_documents_document_id_body import PutKnowledgesIdDocumentsDocumentIdBody
from ...models.put_knowledges_id_documents_document_id_response_200 import PutKnowledgesIdDocumentsDocumentIdResponse200
from ...models.put_knowledges_id_documents_document_id_response_400 import PutKnowledgesIdDocumentsDocumentIdResponse400
from ...models.put_knowledges_id_documents_document_id_response_401 import PutKnowledgesIdDocumentsDocumentIdResponse401
from ...models.put_knowledges_id_documents_document_id_response_404 import PutKnowledgesIdDocumentsDocumentIdResponse404
from ...types import Response


def _get_kwargs(
    id: str,
    document_id: str,
    *,
    body: PutKnowledgesIdDocumentsDocumentIdBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/knowledges/{id}/documents/{document_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        PutKnowledgesIdDocumentsDocumentIdResponse200,
        PutKnowledgesIdDocumentsDocumentIdResponse400,
        PutKnowledgesIdDocumentsDocumentIdResponse401,
        PutKnowledgesIdDocumentsDocumentIdResponse404,
    ]
]:
    if response.status_code == 200:
        response_200 = PutKnowledgesIdDocumentsDocumentIdResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = PutKnowledgesIdDocumentsDocumentIdResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = PutKnowledgesIdDocumentsDocumentIdResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = PutKnowledgesIdDocumentsDocumentIdResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        PutKnowledgesIdDocumentsDocumentIdResponse200,
        PutKnowledgesIdDocumentsDocumentIdResponse400,
        PutKnowledgesIdDocumentsDocumentIdResponse401,
        PutKnowledgesIdDocumentsDocumentIdResponse404,
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
    document_id: str,
    *,
    client: AuthenticatedClient,
    body: PutKnowledgesIdDocumentsDocumentIdBody,
) -> Response[
    Union[
        PutKnowledgesIdDocumentsDocumentIdResponse200,
        PutKnowledgesIdDocumentsDocumentIdResponse400,
        PutKnowledgesIdDocumentsDocumentIdResponse401,
        PutKnowledgesIdDocumentsDocumentIdResponse404,
    ]
]:
    """Update Document

     Update an existing document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        document_id (str):  Example: doc123.
        body (PutKnowledgesIdDocumentsDocumentIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PutKnowledgesIdDocumentsDocumentIdResponse200, PutKnowledgesIdDocumentsDocumentIdResponse400, PutKnowledgesIdDocumentsDocumentIdResponse401, PutKnowledgesIdDocumentsDocumentIdResponse404]]
    """

    kwargs = _get_kwargs(
        id=id,
        document_id=document_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    document_id: str,
    *,
    client: AuthenticatedClient,
    body: PutKnowledgesIdDocumentsDocumentIdBody,
) -> Optional[
    Union[
        PutKnowledgesIdDocumentsDocumentIdResponse200,
        PutKnowledgesIdDocumentsDocumentIdResponse400,
        PutKnowledgesIdDocumentsDocumentIdResponse401,
        PutKnowledgesIdDocumentsDocumentIdResponse404,
    ]
]:
    """Update Document

     Update an existing document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        document_id (str):  Example: doc123.
        body (PutKnowledgesIdDocumentsDocumentIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PutKnowledgesIdDocumentsDocumentIdResponse200, PutKnowledgesIdDocumentsDocumentIdResponse400, PutKnowledgesIdDocumentsDocumentIdResponse401, PutKnowledgesIdDocumentsDocumentIdResponse404]
    """

    return sync_detailed(
        id=id,
        document_id=document_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    document_id: str,
    *,
    client: AuthenticatedClient,
    body: PutKnowledgesIdDocumentsDocumentIdBody,
) -> Response[
    Union[
        PutKnowledgesIdDocumentsDocumentIdResponse200,
        PutKnowledgesIdDocumentsDocumentIdResponse400,
        PutKnowledgesIdDocumentsDocumentIdResponse401,
        PutKnowledgesIdDocumentsDocumentIdResponse404,
    ]
]:
    """Update Document

     Update an existing document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        document_id (str):  Example: doc123.
        body (PutKnowledgesIdDocumentsDocumentIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PutKnowledgesIdDocumentsDocumentIdResponse200, PutKnowledgesIdDocumentsDocumentIdResponse400, PutKnowledgesIdDocumentsDocumentIdResponse401, PutKnowledgesIdDocumentsDocumentIdResponse404]]
    """

    kwargs = _get_kwargs(
        id=id,
        document_id=document_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    document_id: str,
    *,
    client: AuthenticatedClient,
    body: PutKnowledgesIdDocumentsDocumentIdBody,
) -> Optional[
    Union[
        PutKnowledgesIdDocumentsDocumentIdResponse200,
        PutKnowledgesIdDocumentsDocumentIdResponse400,
        PutKnowledgesIdDocumentsDocumentIdResponse401,
        PutKnowledgesIdDocumentsDocumentIdResponse404,
    ]
]:
    """Update Document

     Update an existing document in a knowledge base

    Args:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        document_id (str):  Example: doc123.
        body (PutKnowledgesIdDocumentsDocumentIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PutKnowledgesIdDocumentsDocumentIdResponse200, PutKnowledgesIdDocumentsDocumentIdResponse400, PutKnowledgesIdDocumentsDocumentIdResponse401, PutKnowledgesIdDocumentsDocumentIdResponse404]
    """

    return (
        await asyncio_detailed(
            id=id,
            document_id=document_id,
            client=client,
            body=body,
        )
    ).parsed
