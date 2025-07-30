from enum import Enum


class PostApiUsersIdRegenerateKeyResponse200Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
