from enum import Enum

class ReturnAction(str, Enum):
    RESPOND_NOW = "respond_now"
    DEFER = "defer"
    NO_ACTION = "no_action"
    ASK_USER = "ask_user"