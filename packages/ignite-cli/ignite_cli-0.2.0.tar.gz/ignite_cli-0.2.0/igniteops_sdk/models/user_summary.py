from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserSummary")


@_attrs_define
class UserSummary:
    """
    Example:
        {'email': 'john.doe@example.com', 'name': 'John Doe', 'user_id': '7e7a4f2c-5c3d-4d8a-b9d3-2f9e7f7e7a4f'}

    Attributes:
        email (str): Email address of the user.
        user_id (UUID): Unique identifier for the user.
        name (Union[Unset, str]): Display name of the user.
    """

    email: str
    user_id: UUID
    name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        user_id = str(self.user_id)

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "user_id": user_id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        user_id = UUID(d.pop("user_id"))

        name = d.pop("name", UNSET)

        user_summary = cls(
            email=email,
            user_id=user_id,
            name=name,
        )

        user_summary.additional_properties = d
        return user_summary

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
