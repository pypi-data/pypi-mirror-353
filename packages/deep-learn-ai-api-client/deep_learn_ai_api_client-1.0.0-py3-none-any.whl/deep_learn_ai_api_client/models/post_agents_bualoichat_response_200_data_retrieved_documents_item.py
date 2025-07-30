from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_agents_bualoichat_response_200_data_retrieved_documents_item_metadata import (
        PostAgentsBualoichatResponse200DataRetrievedDocumentsItemMetadata,
    )


T = TypeVar("T", bound="PostAgentsBualoichatResponse200DataRetrievedDocumentsItem")


@_attrs_define
class PostAgentsBualoichatResponse200DataRetrievedDocumentsItem:
    """
    Attributes:
        content (str): The content of the retrieved document Example: Document content retrieved from knowledge base.
        metadata (Union[Unset, PostAgentsBualoichatResponse200DataRetrievedDocumentsItemMetadata]): Additional metadata
            about the retrieved document
    """

    content: str
    metadata: Union[Unset, "PostAgentsBualoichatResponse200DataRetrievedDocumentsItemMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_agents_bualoichat_response_200_data_retrieved_documents_item_metadata import (
            PostAgentsBualoichatResponse200DataRetrievedDocumentsItemMetadata,
        )

        d = dict(src_dict)
        content = d.pop("content")

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, PostAgentsBualoichatResponse200DataRetrievedDocumentsItemMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PostAgentsBualoichatResponse200DataRetrievedDocumentsItemMetadata.from_dict(_metadata)

        post_agents_bualoichat_response_200_data_retrieved_documents_item = cls(
            content=content,
            metadata=metadata,
        )

        post_agents_bualoichat_response_200_data_retrieved_documents_item.additional_properties = d
        return post_agents_bualoichat_response_200_data_retrieved_documents_item

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
