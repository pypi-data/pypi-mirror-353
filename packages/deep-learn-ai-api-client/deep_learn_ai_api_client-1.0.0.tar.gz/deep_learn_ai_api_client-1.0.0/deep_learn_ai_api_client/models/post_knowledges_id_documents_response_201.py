from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostKnowledgesIdDocumentsResponse201")


@_attrs_define
class PostKnowledgesIdDocumentsResponse201:
    """
    Attributes:
        id (str):  Example: doc123.
        content (str):  Example: Document content....
        embedding (str):  Example: embedding123.
        created_at (str):  Example: 2024-01-01T00:00:00Z.
        updated_at (str):  Example: 2024-01-01T00:00:00Z.
        data (Union[Unset, Any]):  Example: {'title': 'Document Title'}.
    """

    id: str
    content: str
    embedding: str
    created_at: str
    updated_at: str
    data: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        content = self.content

        embedding = self.embedding

        created_at = self.created_at

        updated_at = self.updated_at

        data = self.data

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "content": content,
                "embedding": embedding,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        content = d.pop("content")

        embedding = d.pop("embedding")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        data = d.pop("data", UNSET)

        post_knowledges_id_documents_response_201 = cls(
            id=id,
            content=content,
            embedding=embedding,
            created_at=created_at,
            updated_at=updated_at,
            data=data,
        )

        post_knowledges_id_documents_response_201.additional_properties = d
        return post_knowledges_id_documents_response_201

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
