from enum import Enum


class NewGlobalMessageScope(str, Enum):
    CLASSIFY_QUESTION = "classify_question"
    LOGIN = "login"
    SEARCH_DOCUMENTS = "search_documents"
    SYSTEM_PROMPT = "system_prompt"

    def __str__(self) -> str:
        return str(self.value)
