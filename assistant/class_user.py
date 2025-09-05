from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Simple representation of a bot user."""

    id: int
    user_id: int
    googlesheet_key: Optional[str]
    is_owner: int
    registered_at: str