from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Event:
    timestamp: datetime
    data: str

@dataclass 
class Job:
    status: str
    result: str
    events: List[Event]
    # created_at: datetime = datetime.now()
    # updated_at: datetime = datetime.now()