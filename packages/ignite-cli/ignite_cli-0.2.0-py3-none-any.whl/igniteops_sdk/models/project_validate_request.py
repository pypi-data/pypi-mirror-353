from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_validate_request_language import ProjectValidateRequestLanguage
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectValidateRequest")


@_attrs_define
class ProjectValidateRequest:
    """
    Attributes:
        description (str): Brief summary of the project and its purpose.
        framework (str): Framework to be used for the project.
        integration_id (str): Identifier for the repository integration (e.g., GitHub, GitLab).
        language (ProjectValidateRequestLanguage): Programming language for the project.
        project_name (str): Name of the project to be created.
        repository_name (Union[Unset, str]): Name of the repository associated with the project.
    """

    description: str
    framework: str
    integration_id: str
    language: ProjectValidateRequestLanguage
    project_name: str
    repository_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        framework = self.framework

        integration_id = self.integration_id

        language = self.language.value

        project_name = self.project_name

        repository_name = self.repository_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "framework": framework,
                "integration_id": integration_id,
                "language": language,
                "project_name": project_name,
            }
        )
        if repository_name is not UNSET:
            field_dict["repository_name"] = repository_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description")

        framework = d.pop("framework")

        integration_id = d.pop("integration_id")

        language = ProjectValidateRequestLanguage(d.pop("language"))

        project_name = d.pop("project_name")

        repository_name = d.pop("repository_name", UNSET)

        project_validate_request = cls(
            description=description,
            framework=framework,
            integration_id=integration_id,
            language=language,
            project_name=project_name,
            repository_name=repository_name,
        )

        project_validate_request.additional_properties = d
        return project_validate_request

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
