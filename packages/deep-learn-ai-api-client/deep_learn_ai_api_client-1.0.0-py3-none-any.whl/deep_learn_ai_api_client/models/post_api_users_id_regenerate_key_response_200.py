from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_api_users_id_regenerate_key_response_200_role import PostApiUsersIdRegenerateKeyResponse200Role

T = TypeVar("T", bound="PostApiUsersIdRegenerateKeyResponse200")


@_attrs_define
class PostApiUsersIdRegenerateKeyResponse200:
    """
    Attributes:
        id (str):  Example: user123.
        name (str):  Example: John Doe.
        email (str):  Example: john@example.com.
        role (PostApiUsersIdRegenerateKeyResponse200Role):  Example: USER.
        api_key (str):  Example: ak_1234567890abcdef.
        is_active (bool):  Example: True.
        created_at (str):  Example: 2024-01-01T00:00:00Z.
        updated_at (str):  Example: 2024-01-01T00:00:00Z.
    """

    id: str
    name: str
    email: str
    role: PostApiUsersIdRegenerateKeyResponse200Role
    api_key: str
    is_active: bool
    created_at: str
    updated_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        email = self.email

        role = self.role.value

        api_key = self.api_key

        is_active = self.is_active

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "email": email,
                "role": role,
                "apiKey": api_key,
                "isActive": is_active,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        email = d.pop("email")

        role = PostApiUsersIdRegenerateKeyResponse200Role(d.pop("role"))

        api_key = d.pop("apiKey")

        is_active = d.pop("isActive")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        post_api_users_id_regenerate_key_response_200 = cls(
            id=id,
            name=name,
            email=email,
            role=role,
            api_key=api_key,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
        )

        post_api_users_id_regenerate_key_response_200.additional_properties = d
        return post_api_users_id_regenerate_key_response_200

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
