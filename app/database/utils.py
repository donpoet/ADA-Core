from datetime import datetime, UTC

def ensure_utc(value: datetime) -> datetime:
    if(value.tzinfo is None):
        return value.replace(tzinfo=UTC)
    
    return value.astimezone(UTC)