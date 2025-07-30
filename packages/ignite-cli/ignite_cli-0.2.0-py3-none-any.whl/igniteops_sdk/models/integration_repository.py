import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="IntegrationRepository")


@_attrs_define
class IntegrationRepository:
    """
    Example:
        {'accountName': 'igniteops', 'accountType': 'organization', 'active': True, 'apiEndpoint':
            'https://api.github.com/repos/igniteops/infra', 'creation_date': '2023-05-01T12:00:00Z', 'href':
            'https://github.com/igniteops/infra', 'id': 'd1e2c3b4-5678-4abc-9def-1234567890ab', 'name': 'igniteops/infra',
            'provider': 'github', 'status': 'active'}

    Attributes:
        account_name (Union[Unset, str]): Name of the user or organization account.
        account_type (Union[Unset, str]): Type of account (user or organization).
        active (Union[Unset, bool]): Whether the repository integration is active. Default: True.
        api_endpoint (Union[Unset, str]): API endpoint for the repository provider.
        creation_date (Union[Unset, datetime.datetime]): Date and time when the repository was created.
        href (Union[Unset, str]): Web link to the repository.
        id (Union[Unset, UUID]): Unique identifier for the integration repository.
        name (Union[Unset, str]): Name of the repository.
        provider (Union[Unset, str]): Provider of the repository integration (e.g., GitHub).
        status (Union[Unset, str]): Current status of the repository integration.
    """

    account_name: Union[Unset, str] = UNSET
    account_type: Union[Unset, str] = UNSET
    active: Union[Unset, bool] = True
    api_endpoint: Union[Unset, str] = UNSET
    creation_date: Union[Unset, datetime.datetime] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, UUID] = UNSET
    name: Union[Unset, str] = UNSET
    provider: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account_name = self.account_name

        account_type = self.account_type

        active = self.active

        api_endpoint = self.api_endpoint

        creation_date: Union[Unset, str] = UNSET
        if not isinstance(self.creation_date, Unset):
            creation_date = self.creation_date.isoformat()

        href = self.href

        id: Union[Unset, str] = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        name = self.name

        provider = self.provider

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if active is not UNSET:
            field_dict["active"] = active
        if api_endpoint is not UNSET:
            field_dict["apiEndpoint"] = api_endpoint
        if creation_date is not UNSET:
            field_dict["creation_date"] = creation_date
        if href is not UNSET:
            field_dict["href"] = href
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if provider is not UNSET:
            field_dict["provider"] = provider
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        account_name = d.pop("accountName", UNSET)

        account_type = d.pop("accountType", UNSET)

        active = d.pop("active", UNSET)

        api_endpoint = d.pop("apiEndpoint", UNSET)

        _creation_date = d.pop("creation_date", UNSET)
        creation_date: Union[Unset, datetime.datetime]
        if isinstance(_creation_date, Unset):
            creation_date = UNSET
        else:
            creation_date = isoparse(_creation_date)

        href = d.pop("href", UNSET)

        _id = d.pop("id", UNSET)
        id: Union[Unset, UUID]
        if isinstance(_id, Unset):
            id = UNSET
        else:
            id = UUID(_id)

        name = d.pop("name", UNSET)

        provider = d.pop("provider", UNSET)

        status = d.pop("status", UNSET)

        integration_repository = cls(
            account_name=account_name,
            account_type=account_type,
            active=active,
            api_endpoint=api_endpoint,
            creation_date=creation_date,
            href=href,
            id=id,
            name=name,
            provider=provider,
            status=status,
        )

        integration_repository.additional_properties = d
        return integration_repository

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
