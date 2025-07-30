from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetV1UsersResponse200Item")


@_attrs_define
class GetV1UsersResponse200Item:
    """
    Attributes:
        email (Union[Unset, str]): Full email (if searching by email), or masked email (if searching by name)
        name (Union[Unset, str]): Full name (if searching by email), or masked name (if searching by name)
        user_id (Union[Unset, str]): User unique identifier
    """

    email: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name
        if user_id is not UNSET:
            field_dict["user_id"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        user_id = d.pop("user_id", UNSET)

        get_v1_users_response_200_item = cls(
            email=email,
            name=name,
            user_id=user_id,
        )

        get_v1_users_response_200_item.additional_properties = d
        return get_v1_users_response_200_item

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
