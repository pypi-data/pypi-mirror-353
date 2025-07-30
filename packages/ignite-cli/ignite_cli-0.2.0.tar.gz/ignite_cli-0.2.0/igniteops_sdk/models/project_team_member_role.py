from enum import Enum


class ProjectTeamMemberRole(str, Enum):
    DEVELOPER = "developer"
    LEAD = "lead"
    OWNER = "owner"
    READER = "reader"

    def __str__(self) -> str:
        return str(self.value)
