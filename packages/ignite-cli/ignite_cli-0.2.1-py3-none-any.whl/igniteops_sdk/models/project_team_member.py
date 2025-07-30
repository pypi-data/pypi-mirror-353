from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_team_member_role import ProjectTeamMemberRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectTeamMember")


@_attrs_define
class ProjectTeamMember:
    """
    Example:
        {'email': 'jane.doe@example.com', 'name': 'Jane Doe', 'role': 'developer', 'user_id':
            '7e7a4f2c-5c3d-4d8a-b9d3-2f9e7f7e7a4f'}

    Attributes:
        role (ProjectTeamMemberRole): Role of the user in the project (owner, lead, developer, reader).
        user_id (UUID): Unique identifier of the user.
        email (Union[Unset, str]): Email address of the user.
        name (Union[Unset, str]): Display name of the user.
    """

    role: ProjectTeamMemberRole
    user_id: UUID
    email: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        user_id = str(self.user_id)

        email = self.email

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "user_id": user_id,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = ProjectTeamMemberRole(d.pop("role"))

        user_id = UUID(d.pop("user_id"))

        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        project_team_member = cls(
            role=role,
            user_id=user_id,
            email=email,
            name=name,
        )

        project_team_member.additional_properties = d
        return project_team_member

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
