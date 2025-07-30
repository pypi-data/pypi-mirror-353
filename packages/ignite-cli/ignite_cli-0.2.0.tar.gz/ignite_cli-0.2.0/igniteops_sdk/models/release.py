import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.release_status import ReleaseStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.release_changelog import ReleaseChangelog


T = TypeVar("T", bound="Release")


@_attrs_define
class Release:
    """
    Attributes:
        changelog (Union[Unset, ReleaseChangelog]): Changelog or list of changes included in the release.
        id (Union[Unset, str]): Unique identifier for the release.
        pipeline_execution_id (Union[Unset, str]): Identifier for the CI/CD pipeline execution related to this release.
        release_date (Union[Unset, datetime.datetime]): Date and time when the release was published.
        repo_link (Union[Unset, str]): Link to the repository for this release.
        status (Union[Unset, ReleaseStatus]): Current status of the release.
        tag (Union[Unset, str]): Tag or version label for the release.
        title (Union[Unset, str]): Title of the release.
    """

    changelog: Union[Unset, "ReleaseChangelog"] = UNSET
    id: Union[Unset, str] = UNSET
    pipeline_execution_id: Union[Unset, str] = UNSET
    release_date: Union[Unset, datetime.datetime] = UNSET
    repo_link: Union[Unset, str] = UNSET
    status: Union[Unset, ReleaseStatus] = UNSET
    tag: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        changelog: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.changelog, Unset):
            changelog = self.changelog.to_dict()

        id = self.id

        pipeline_execution_id = self.pipeline_execution_id

        release_date: Union[Unset, str] = UNSET
        if not isinstance(self.release_date, Unset):
            release_date = self.release_date.isoformat()

        repo_link = self.repo_link

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        tag = self.tag

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if changelog is not UNSET:
            field_dict["changelog"] = changelog
        if id is not UNSET:
            field_dict["id"] = id
        if pipeline_execution_id is not UNSET:
            field_dict["pipeline_execution_id"] = pipeline_execution_id
        if release_date is not UNSET:
            field_dict["release_date"] = release_date
        if repo_link is not UNSET:
            field_dict["repo_link"] = repo_link
        if status is not UNSET:
            field_dict["status"] = status
        if tag is not UNSET:
            field_dict["tag"] = tag
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.release_changelog import ReleaseChangelog

        d = dict(src_dict)
        _changelog = d.pop("changelog", UNSET)
        changelog: Union[Unset, ReleaseChangelog]
        if isinstance(_changelog, Unset):
            changelog = UNSET
        else:
            changelog = ReleaseChangelog.from_dict(_changelog)

        id = d.pop("id", UNSET)

        pipeline_execution_id = d.pop("pipeline_execution_id", UNSET)

        _release_date = d.pop("release_date", UNSET)
        release_date: Union[Unset, datetime.datetime]
        if isinstance(_release_date, Unset):
            release_date = UNSET
        else:
            release_date = isoparse(_release_date)

        repo_link = d.pop("repo_link", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ReleaseStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ReleaseStatus(_status)

        tag = d.pop("tag", UNSET)

        title = d.pop("title", UNSET)

        release = cls(
            changelog=changelog,
            id=id,
            pipeline_execution_id=pipeline_execution_id,
            release_date=release_date,
            repo_link=repo_link,
            status=status,
            tag=tag,
            title=title,
        )

        release.additional_properties = d
        return release

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
