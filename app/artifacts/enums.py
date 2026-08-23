from enum import Enum

class ArtifactOperation(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class ArtifactType(str, Enum):
    LLM_RESPONSE = "llm_response"
    FILE = "file"
    DIRECTORY = "directory"
    NOTION_PAGE = "notion_page"
    GIT_COMMIT = "git_commit"
    DATABASE_ENTRY = "database_entry"
    HOME_ASSISTANT_AUTOMATION = "home_assistant_automation"
    CALENDAR_ENTRY = "calendar_entry"