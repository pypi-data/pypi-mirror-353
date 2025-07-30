from enum import Enum


class ProjectTeamUpdateRequestRole(str, Enum):
    DEVELOPER = "developer"
    LEAD = "lead"
    READER = "reader"

    def __str__(self) -> str:
        return str(self.value)
