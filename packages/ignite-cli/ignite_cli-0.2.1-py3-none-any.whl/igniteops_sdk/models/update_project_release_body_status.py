from enum import Enum


class UpdateProjectReleaseBodyStatus(str, Enum):
    COMPLETED = "completed"
    ERROR = "error"
    PENDING = "pending"
    PROCESSING = "processing"

    def __str__(self) -> str:
        return str(self.value)
