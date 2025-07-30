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


T = TypeVar("T", bound="ApiKeyItem")


@_attrs_define
class ApiKeyItem:
    """
    Attributes:
        created_at (Union[Unset, datetime.datetime]): Date and time when the key was created.
        expires_at (Union[None, Unset, datetime.datetime]): Expiration date and time of the key, if set.
        key_id (Union[Unset, UUID]): Unique identifier for the key.
        name (Union[Unset, str]): Friendly name for the key.
        permissions (Union[Unset, ApiKeyPermissions]):  Example: {'projects': ['read', 'write'], 'releases': ['read']}.
        revoked (Union[Unset, bool]): Whether the key has been revoked.
    """

    created_at: Union[Unset, datetime.datetime] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    key_id: Union[Unset, UUID] = UNSET
    name: Union[Unset, str] = UNSET
    permissions: Union[Unset, "ApiKeyPermissions"] = UNSET
    revoked: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

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

        name = self.name

        permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()

        revoked = self.revoked

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if key_id is not UNSET:
            field_dict["key_id"] = key_id
        if name is not UNSET:
            field_dict["name"] = name
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if revoked is not UNSET:
            field_dict["revoked"] = revoked

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_permissions import ApiKeyPermissions

        d = dict(src_dict)
        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

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

        name = d.pop("name", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, ApiKeyPermissions]
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = ApiKeyPermissions.from_dict(_permissions)

        revoked = d.pop("revoked", UNSET)

        api_key_item = cls(
            created_at=created_at,
            expires_at=expires_at,
            key_id=key_id,
            name=name,
            permissions=permissions,
            revoked=revoked,
        )

        api_key_item.additional_properties = d
        return api_key_item

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
