from enum import Enum

class IntentAction(str, Enum):
    CHAT = "chat"
    CREATE_TASK = "create_task"
    MODIFY_TASK = "modify_task"
    CANCEL_TASK = "cancel_task"