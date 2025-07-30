from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ErrorResponse")


@_attrs_define
class ErrorResponse:
    """
    Example:
        {'error': 'invalid_request', 'error_description': 'The provided project name is invalid.', 'field':
            'project_name', 'status': 400}

    Attributes:
        error (Union[Unset, str]): Error code or identifier.
        error_description (Union[Unset, str]): Human-readable description of the error.
        field (Union[Unset, UUID]): Field related to the error, if applicable.
        status (Union[Unset, int]): HTTP status code associated with the error.
    """

    error: Union[Unset, str] = UNSET
    error_description: Union[Unset, str] = UNSET
    field: Union[Unset, UUID] = UNSET
    status: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        error_description = self.error_description

        field: Union[Unset, str] = UNSET
        if not isinstance(self.field, Unset):
            field = str(self.field)

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error is not UNSET:
            field_dict["error"] = error
        if error_description is not UNSET:
            field_dict["error_description"] = error_description
        if field is not UNSET:
            field_dict["field"] = field
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = d.pop("error", UNSET)

        error_description = d.pop("error_description", UNSET)

        _field = d.pop("field", UNSET)
        field: Union[Unset, UUID]
        if isinstance(_field, Unset):
            field = UNSET
        else:
            field = UUID(_field)

        status = d.pop("status", UNSET)

        error_response = cls(
            error=error,
            error_description=error_description,
            field=field,
            status=status,
        )

        error_response.additional_properties = d
        return error_response

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
