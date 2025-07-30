from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_team_update_request_role import ProjectTeamUpdateRequestRole

T = TypeVar("T", bound="ProjectTeamUpdateRequest")


@_attrs_define
class ProjectTeamUpdateRequest:
    """
    Attributes:
        role (ProjectTeamUpdateRequestRole):
    """

    role: ProjectTeamUpdateRequestRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = ProjectTeamUpdateRequestRole(d.pop("role"))

        project_team_update_request = cls(
            role=role,
        )

        project_team_update_request.additional_properties = d
        return project_team_update_request

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
