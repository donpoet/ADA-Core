from enum import Enum

class TaskType(str, Enum):
    WEAK_LLM = "weak_llm"

class TaskStatus(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OPEN = "open"

class TaskExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskResultStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"