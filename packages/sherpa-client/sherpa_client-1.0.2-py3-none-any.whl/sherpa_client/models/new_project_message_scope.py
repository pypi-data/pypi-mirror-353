from enum import Enum


class NewProjectMessageScope(str, Enum):
    CLASSIFY_QUESTION = "classify_question"
    OPEN_CAMPAIGN = "open_campaign"
    OPEN_SESSION = "open_session"
    SEARCH_DOCUMENTS = "search_documents"
    STOP_CAMPAIGN = "stop_campaign"
    SYSTEM_PROMPT = "system_prompt"

    def __str__(self) -> str:
        return str(self.value)
