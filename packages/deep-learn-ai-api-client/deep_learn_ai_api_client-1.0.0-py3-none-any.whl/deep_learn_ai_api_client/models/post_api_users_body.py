from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_api_users_body_role import PostApiUsersBodyRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiUsersBody")


@_attrs_define
class PostApiUsersBody:
    """
    Attributes:
        name (str):  Example: John Doe.
        email (str):  Example: john@example.com.
        role (Union[Unset, PostApiUsersBodyRole]):  Default: PostApiUsersBodyRole.USER. Example: USER.
    """

    name: str
    email: str
    role: Union[Unset, PostApiUsersBodyRole] = PostApiUsersBodyRole.USER
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        email = self.email

        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "email": email,
            }
        )
        if role is not UNSET:
            field_dict["role"] = role

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        email = d.pop("email")

        _role = d.pop("role", UNSET)
        role: Union[Unset, PostApiUsersBodyRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = PostApiUsersBodyRole(_role)

        post_api_users_body = cls(
            name=name,
            email=email,
            role=role,
        )

        post_api_users_body.additional_properties = d
        return post_api_users_body

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
