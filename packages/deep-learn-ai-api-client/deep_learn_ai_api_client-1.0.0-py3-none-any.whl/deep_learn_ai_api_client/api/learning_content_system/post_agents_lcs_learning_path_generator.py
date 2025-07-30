from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_agents_lcs_learning_path_generator_body import PostAgentsLcsLearningPathGeneratorBody
from ...models.post_agents_lcs_learning_path_generator_response_400 import PostAgentsLcsLearningPathGeneratorResponse400
from ...models.post_agents_lcs_learning_path_generator_response_500 import PostAgentsLcsLearningPathGeneratorResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: PostAgentsLcsLearningPathGeneratorBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/agents/lcs-learning-path-generator",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]:
    if response.status_code == 200:
        response_200 = response.text
        return response_200
    if response.status_code == 400:
        response_400 = PostAgentsLcsLearningPathGeneratorResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 500:
        response_500 = PostAgentsLcsLearningPathGeneratorResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostAgentsLcsLearningPathGeneratorBody,
) -> Response[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]:
    """Generate Learning Path

     Generate a personalized learning path using AI for a given topic. Returns a streaming response with
    the generated content.

    Args:
        body (PostAgentsLcsLearningPathGeneratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]
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
    body: PostAgentsLcsLearningPathGeneratorBody,
) -> Optional[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]:
    """Generate Learning Path

     Generate a personalized learning path using AI for a given topic. Returns a streaming response with
    the generated content.

    Args:
        body (PostAgentsLcsLearningPathGeneratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostAgentsLcsLearningPathGeneratorBody,
) -> Response[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]:
    """Generate Learning Path

     Generate a personalized learning path using AI for a given topic. Returns a streaming response with
    the generated content.

    Args:
        body (PostAgentsLcsLearningPathGeneratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostAgentsLcsLearningPathGeneratorBody,
) -> Optional[Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]]:
    """Generate Learning Path

     Generate a personalized learning path using AI for a given topic. Returns a streaming response with
    the generated content.

    Args:
        body (PostAgentsLcsLearningPathGeneratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostAgentsLcsLearningPathGeneratorResponse400, PostAgentsLcsLearningPathGeneratorResponse500, str]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
