from enum import Enum


class CloudIntegrationResponseStatus(str, Enum):
    ACTIVE = "active"
    ERROR = "error"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
