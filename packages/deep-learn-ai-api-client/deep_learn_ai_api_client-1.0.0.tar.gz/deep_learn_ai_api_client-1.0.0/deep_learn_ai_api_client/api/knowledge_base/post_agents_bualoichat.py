from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_agents_bualoichat_body import PostAgentsBualoichatBody
from ...models.post_agents_bualoichat_response_200 import PostAgentsBualoichatResponse200
from ...models.post_agents_bualoichat_response_400 import PostAgentsBualoichatResponse400
from ...models.post_agents_bualoichat_response_500 import PostAgentsBualoichatResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: PostAgentsBualoichatBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/agents/bualoichat",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]:
    if response.status_code == 200:
        response_200 = PostAgentsBualoichatResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = PostAgentsBualoichatResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 500:
        response_500 = PostAgentsBualoichatResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostAgentsBualoichatBody,
) -> Response[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]:
    """Bualoichat Knowledge Query

     Query a specific knowledge base using AI to get relevant answers with retrieved documents.

    Args:
        body (PostAgentsBualoichatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]
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
    client: Union[AuthenticatedClient, Client],
    body: PostAgentsBualoichatBody,
) -> Optional[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]:
    """Bualoichat Knowledge Query

     Query a specific knowledge base using AI to get relevant answers with retrieved documents.

    Args:
        body (PostAgentsBualoichatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostAgentsBualoichatBody,
) -> Response[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]:
    """Bualoichat Knowledge Query

     Query a specific knowledge base using AI to get relevant answers with retrieved documents.

    Args:
        body (PostAgentsBualoichatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostAgentsBualoichatBody,
) -> Optional[Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]]:
    """Bualoichat Knowledge Query

     Query a specific knowledge base using AI to get relevant answers with retrieved documents.

    Args:
        body (PostAgentsBualoichatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostAgentsBualoichatResponse200, PostAgentsBualoichatResponse400, PostAgentsBualoichatResponse500]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
