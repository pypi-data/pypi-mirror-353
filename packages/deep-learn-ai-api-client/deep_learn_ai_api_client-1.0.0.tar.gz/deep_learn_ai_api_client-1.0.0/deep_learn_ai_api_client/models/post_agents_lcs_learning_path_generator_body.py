from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_agents_lcs_learning_path_generator_body_messages_item import (
        PostAgentsLcsLearningPathGeneratorBodyMessagesItem,
    )


T = TypeVar("T", bound="PostAgentsLcsLearningPathGeneratorBody")


@_attrs_define
class PostAgentsLcsLearningPathGeneratorBody:
    """
    Attributes:
        messages (list['PostAgentsLcsLearningPathGeneratorBodyMessagesItem']): Array of chat messages for the
            conversation
    """

    messages: list["PostAgentsLcsLearningPathGeneratorBodyMessagesItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_agents_lcs_learning_path_generator_body_messages_item import (
            PostAgentsLcsLearningPathGeneratorBodyMessagesItem,
        )

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = PostAgentsLcsLearningPathGeneratorBodyMessagesItem.from_dict(messages_item_data)

            messages.append(messages_item)

        post_agents_lcs_learning_path_generator_body = cls(
            messages=messages,
        )

        post_agents_lcs_learning_path_generator_body.additional_properties = d
        return post_agents_lcs_learning_path_generator_body

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
