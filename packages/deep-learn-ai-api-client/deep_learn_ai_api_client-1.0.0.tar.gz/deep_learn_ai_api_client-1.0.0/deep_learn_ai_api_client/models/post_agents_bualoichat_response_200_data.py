from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_agents_bualoichat_response_200_data_role import PostAgentsBualoichatResponse200DataRole

if TYPE_CHECKING:
    from ..models.post_agents_bualoichat_response_200_data_retrieved_documents_item import (
        PostAgentsBualoichatResponse200DataRetrievedDocumentsItem,
    )


T = TypeVar("T", bound="PostAgentsBualoichatResponse200Data")


@_attrs_define
class PostAgentsBualoichatResponse200Data:
    """The response data containing the AI answer and retrieved documents

    Attributes:
        role (PostAgentsBualoichatResponse200DataRole): The role of the response Example: assistant.
        content (str): The AI-generated response content Example: Here is the answer based on the knowledge base.
        retrieved_documents (list['PostAgentsBualoichatResponse200DataRetrievedDocumentsItem']): Documents retrieved
            from the knowledge base to answer the question
    """

    role: PostAgentsBualoichatResponse200DataRole
    content: str
    retrieved_documents: list["PostAgentsBualoichatResponse200DataRetrievedDocumentsItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        content = self.content

        retrieved_documents = []
        for retrieved_documents_item_data in self.retrieved_documents:
            retrieved_documents_item = retrieved_documents_item_data.to_dict()
            retrieved_documents.append(retrieved_documents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "content": content,
                "retrievedDocuments": retrieved_documents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_agents_bualoichat_response_200_data_retrieved_documents_item import (
            PostAgentsBualoichatResponse200DataRetrievedDocumentsItem,
        )

        d = dict(src_dict)
        role = PostAgentsBualoichatResponse200DataRole(d.pop("role"))

        content = d.pop("content")

        retrieved_documents = []
        _retrieved_documents = d.pop("retrievedDocuments")
        for retrieved_documents_item_data in _retrieved_documents:
            retrieved_documents_item = PostAgentsBualoichatResponse200DataRetrievedDocumentsItem.from_dict(
                retrieved_documents_item_data
            )

            retrieved_documents.append(retrieved_documents_item)

        post_agents_bualoichat_response_200_data = cls(
            role=role,
            content=content,
            retrieved_documents=retrieved_documents,
        )

        post_agents_bualoichat_response_200_data.additional_properties = d
        return post_agents_bualoichat_response_200_data

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
