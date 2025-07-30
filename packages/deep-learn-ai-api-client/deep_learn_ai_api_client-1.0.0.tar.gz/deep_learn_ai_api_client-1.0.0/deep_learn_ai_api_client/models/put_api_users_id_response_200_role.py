from enum import Enum


class PutApiUsersIdResponse200Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
