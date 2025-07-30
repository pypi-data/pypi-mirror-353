from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.put_knowledges_id_documents_document_id_body_data import PutKnowledgesIdDocumentsDocumentIdBodyData


T = TypeVar("T", bound="PutKnowledgesIdDocumentsDocumentIdBody")


@_attrs_define
class PutKnowledgesIdDocumentsDocumentIdBody:
    """
    Attributes:
        content (Union[Unset, str]):  Example: Updated document content....
        data (Union[Unset, PutKnowledgesIdDocumentsDocumentIdBodyData]):  Example: {'title': 'Updated Document Title',
            'category': 'guide'}.
    """

    content: Union[Unset, str] = UNSET
    data: Union[Unset, "PutKnowledgesIdDocumentsDocumentIdBodyData"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content is not UNSET:
            field_dict["content"] = content
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.put_knowledges_id_documents_document_id_body_data import (
            PutKnowledgesIdDocumentsDocumentIdBodyData,
        )

        d = dict(src_dict)
        content = d.pop("content", UNSET)

        _data = d.pop("data", UNSET)
        data: Union[Unset, PutKnowledgesIdDocumentsDocumentIdBodyData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = PutKnowledgesIdDocumentsDocumentIdBodyData.from_dict(_data)

        put_knowledges_id_documents_document_id_body = cls(
            content=content,
            data=data,
        )

        put_knowledges_id_documents_document_id_body.additional_properties = d
        return put_knowledges_id_documents_document_id_body

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
