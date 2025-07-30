from enum import Enum


class PutApiUsersIdBodyRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
