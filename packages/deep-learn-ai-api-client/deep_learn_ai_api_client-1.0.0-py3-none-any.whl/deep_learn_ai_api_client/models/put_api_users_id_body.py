from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.put_api_users_id_body_role import PutApiUsersIdBodyRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="PutApiUsersIdBody")


@_attrs_define
class PutApiUsersIdBody:
    """
    Attributes:
        name (Union[Unset, str]):  Example: John Doe Updated.
        email (Union[Unset, str]):  Example: john.updated@example.com.
        role (Union[Unset, PutApiUsersIdBodyRole]):  Example: ADMIN.
        is_active (Union[Unset, bool]):  Example: True.
    """

    name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    role: Union[Unset, PutApiUsersIdBodyRole] = UNSET
    is_active: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        email = self.email

        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email
        if role is not UNSET:
            field_dict["role"] = role
        if is_active is not UNSET:
            field_dict["isActive"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        _role = d.pop("role", UNSET)
        role: Union[Unset, PutApiUsersIdBodyRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = PutApiUsersIdBodyRole(_role)

        is_active = d.pop("isActive", UNSET)

        put_api_users_id_body = cls(
            name=name,
            email=email,
            role=role,
            is_active=is_active,
        )

        put_api_users_id_body.additional_properties = d
        return put_api_users_id_body

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
