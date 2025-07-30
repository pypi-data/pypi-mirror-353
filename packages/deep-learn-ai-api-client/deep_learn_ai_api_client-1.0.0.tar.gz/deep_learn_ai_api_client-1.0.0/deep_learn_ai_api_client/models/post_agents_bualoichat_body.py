from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_agents_bualoichat_body_data import PostAgentsBualoichatBodyData
    from ..models.post_agents_bualoichat_body_messages_item import PostAgentsBualoichatBodyMessagesItem


T = TypeVar("T", bound="PostAgentsBualoichatBody")


@_attrs_define
class PostAgentsBualoichatBody:
    """
    Attributes:
        messages (list['PostAgentsBualoichatBodyMessagesItem']): Array of chat messages for the conversation
        data (PostAgentsBualoichatBodyData):
        knowledge_id (str): The knowledge base ID to search in Example: kb_123456.
    """

    messages: list["PostAgentsBualoichatBodyMessagesItem"]
    data: "PostAgentsBualoichatBodyData"
    knowledge_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        data = self.data.to_dict()

        knowledge_id = self.knowledge_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
                "data": data,
                "knowledgeId": knowledge_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_agents_bualoichat_body_data import PostAgentsBualoichatBodyData
        from ..models.post_agents_bualoichat_body_messages_item import PostAgentsBualoichatBodyMessagesItem

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = PostAgentsBualoichatBodyMessagesItem.from_dict(messages_item_data)

            messages.append(messages_item)

        data = PostAgentsBualoichatBodyData.from_dict(d.pop("data"))

        knowledge_id = d.pop("knowledgeId")

        post_agents_bualoichat_body = cls(
            messages=messages,
            data=data,
            knowledge_id=knowledge_id,
        )

        post_agents_bualoichat_body.additional_properties = d
        return post_agents_bualoichat_body

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
