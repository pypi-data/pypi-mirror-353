from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_knowledges_response_201_documents_item import PostKnowledgesResponse201DocumentsItem


T = TypeVar("T", bound="PostKnowledgesResponse201")


@_attrs_define
class PostKnowledgesResponse201:
    """
    Attributes:
        id (str):  Example: 123e4567-e89b-12d3-a456-426614174000.
        owner (str):  Example: user123.
        created_at (str):  Example: 2024-01-01T00:00:00Z.
        updated_at (str):  Example: 2024-01-01T00:00:00Z.
        documents (list['PostKnowledgesResponse201DocumentsItem']):
        data (Union[Unset, Any]):  Example: {'name': 'My Knowledge Base', 'description': 'A collection of documents
            about AI'}.
    """

    id: str
    owner: str
    created_at: str
    updated_at: str
    documents: list["PostKnowledgesResponse201DocumentsItem"]
    data: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        owner = self.owner

        created_at = self.created_at

        updated_at = self.updated_at

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        data = self.data

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "owner": owner,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "documents": documents,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_knowledges_response_201_documents_item import PostKnowledgesResponse201DocumentsItem

        d = dict(src_dict)
        id = d.pop("id")

        owner = d.pop("owner")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = PostKnowledgesResponse201DocumentsItem.from_dict(documents_item_data)

            documents.append(documents_item)

        data = d.pop("data", UNSET)

        post_knowledges_response_201 = cls(
            id=id,
            owner=owner,
            created_at=created_at,
            updated_at=updated_at,
            documents=documents,
            data=data,
        )

        post_knowledges_response_201.additional_properties = d
        return post_knowledges_response_201

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
