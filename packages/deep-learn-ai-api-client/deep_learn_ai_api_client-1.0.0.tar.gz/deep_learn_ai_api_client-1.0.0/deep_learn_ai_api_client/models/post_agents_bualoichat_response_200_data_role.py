from enum import Enum


class PostAgentsBualoichatResponse200DataRole(str, Enum):
    ASSISTANT = "assistant"

    def __str__(self) -> str:
        return str(self.value)
