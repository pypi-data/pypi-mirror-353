from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_key_create_request_permissions import (
        ApiKeyCreateRequestPermissions,
    )


T = TypeVar("T", bound="ApiKeyCreateRequest")


@_attrs_define
class ApiKeyCreateRequest:
    """
    Example:
        {'name': 'CI/CD Bot Token', 'permissions': {'projects': ['read', 'write'], 'releases': ['read']}, 'ttlDays': 30}

    Attributes:
        name (str): Friendly name for the key
        permissions (Union[Unset, ApiKeyCreateRequestPermissions]): Allowed actions per service
        ttl_days (Union[Unset, int]): Days until expiration (omit for no expiry)
    """

    name: str
    permissions: Union[Unset, "ApiKeyCreateRequestPermissions"] = UNSET
    ttl_days: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()

        ttl_days = self.ttl_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if ttl_days is not UNSET:
            field_dict["ttlDays"] = ttl_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_create_request_permissions import (
            ApiKeyCreateRequestPermissions,
        )

        d = dict(src_dict)
        name = d.pop("name")

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, ApiKeyCreateRequestPermissions]
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = ApiKeyCreateRequestPermissions.from_dict(_permissions)

        ttl_days = d.pop("ttlDays", UNSET)

        api_key_create_request = cls(
            name=name,
            permissions=permissions,
            ttl_days=ttl_days,
        )

        api_key_create_request.additional_properties = d
        return api_key_create_request

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
