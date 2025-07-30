from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_api_users_id_response_200_role import GetApiUsersIdResponse200Role

T = TypeVar("T", bound="GetApiUsersIdResponse200")


@_attrs_define
class GetApiUsersIdResponse200:
    """
    Attributes:
        id (str):  Example: user123.
        name (str):  Example: John Doe.
        email (str):  Example: john@example.com.
        role (GetApiUsersIdResponse200Role):  Example: USER.
        is_active (bool):  Example: True.
        created_at (str):  Example: 2024-01-01T00:00:00Z.
        updated_at (str):  Example: 2024-01-01T00:00:00Z.
    """

    id: str
    name: str
    email: str
    role: GetApiUsersIdResponse200Role
    is_active: bool
    created_at: str
    updated_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        email = self.email

        role = self.role.value

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

        role = GetApiUsersIdResponse200Role(d.pop("role"))

        is_active = d.pop("isActive")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        get_api_users_id_response_200 = cls(
            id=id,
            name=name,
            email=email,
            role=role,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
        )

        get_api_users_id_response_200.additional_properties = d
        return get_api_users_id_response_200

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
