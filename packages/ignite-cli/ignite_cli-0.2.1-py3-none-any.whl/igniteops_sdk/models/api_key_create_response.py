import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_key_permissions import ApiKeyPermissions


T = TypeVar("T", bound="ApiKeyCreateResponse")


@_attrs_define
class ApiKeyCreateResponse:
    """
    Example:
        {'expires_at': '2024-03-16T14:30:00Z', 'key_id': '123e4567-e89b-12d3-a456-426614174000', 'key_secret':
            'ghp_1234567890abcdefghijklmnopqrstuvwxyz', 'permissions': {'projects': ['read', 'write'], 'releases':
            ['read']}}

    Attributes:
        expires_at (Union[None, Unset, datetime.datetime]): Expiration date and time of the key, if set.
        key_id (Union[Unset, UUID]): Unique identifier for the key.
        key_secret (Union[Unset, str]): The generated key secret.
        permissions (Union[Unset, ApiKeyPermissions]):  Example: {'projects': ['read', 'write'], 'releases': ['read']}.
    """

    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    key_id: Union[Unset, UUID] = UNSET
    key_secret: Union[Unset, str] = UNSET
    permissions: Union[Unset, "ApiKeyPermissions"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        key_id: Union[Unset, str] = UNSET
        if not isinstance(self.key_id, Unset):
            key_id = str(self.key_id)

        key_secret = self.key_secret

        permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if key_id is not UNSET:
            field_dict["key_id"] = key_id
        if key_secret is not UNSET:
            field_dict["key_secret"] = key_secret
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_permissions import ApiKeyPermissions

        d = dict(src_dict)

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        _key_id = d.pop("key_id", UNSET)
        key_id: Union[Unset, UUID]
        if isinstance(_key_id, Unset):
            key_id = UNSET
        else:
            key_id = UUID(_key_id)

        key_secret = d.pop("key_secret", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, ApiKeyPermissions]
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = ApiKeyPermissions.from_dict(_permissions)

        api_key_create_response = cls(
            expires_at=expires_at,
            key_id=key_id,
            key_secret=key_secret,
            permissions=permissions,
        )

        api_key_create_response.additional_properties = d
        return api_key_create_response

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
