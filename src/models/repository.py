from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)  # Immutable
class Repository:
    id: int
    name: str
    owner_name: str
    stars_count: int
    recorded_at: Optional[datetime] = None
    