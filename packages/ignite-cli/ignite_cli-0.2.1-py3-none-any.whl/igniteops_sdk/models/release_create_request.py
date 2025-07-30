from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.release_create_request_changelog import ReleaseCreateRequestChangelog


T = TypeVar("T", bound="ReleaseCreateRequest")


@_attrs_define
class ReleaseCreateRequest:
    """
    Attributes:
        repo_link (str): Link to the repository for this release.
        tag (str): Tag or version label for the new release.
        title (str): Title of the release.
        changelog (Union[Unset, ReleaseCreateRequestChangelog]): Changelog or list of changes included in the release.
        pipeline_execution_id (Union[Unset, str]): Identifier for the CI/CD pipeline execution related to this release.
    """

    repo_link: str
    tag: str
    title: str
    changelog: Union[Unset, "ReleaseCreateRequestChangelog"] = UNSET
    pipeline_execution_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repo_link = self.repo_link

        tag = self.tag

        title = self.title

        changelog: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.changelog, Unset):
            changelog = self.changelog.to_dict()

        pipeline_execution_id = self.pipeline_execution_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repo_link": repo_link,
                "tag": tag,
                "title": title,
            }
        )
        if changelog is not UNSET:
            field_dict["changelog"] = changelog
        if pipeline_execution_id is not UNSET:
            field_dict["pipeline_execution_id"] = pipeline_execution_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.release_create_request_changelog import (
            ReleaseCreateRequestChangelog,
        )

        d = dict(src_dict)
        repo_link = d.pop("repo_link")

        tag = d.pop("tag")

        title = d.pop("title")

        _changelog = d.pop("changelog", UNSET)
        changelog: Union[Unset, ReleaseCreateRequestChangelog]
        if isinstance(_changelog, Unset):
            changelog = UNSET
        else:
            changelog = ReleaseCreateRequestChangelog.from_dict(_changelog)

        pipeline_execution_id = d.pop("pipeline_execution_id", UNSET)

        release_create_request = cls(
            repo_link=repo_link,
            tag=tag,
            title=title,
            changelog=changelog,
            pipeline_execution_id=pipeline_execution_id,
        )

        release_create_request.additional_properties = d
        return release_create_request

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
