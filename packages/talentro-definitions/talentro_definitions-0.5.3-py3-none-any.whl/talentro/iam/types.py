from dataclasses import dataclass
from typing import List

@dataclass
class Organization:
    id: str
    name: str
    displayName: str
    description: str
    attributes: dict
    roles: List[str]
    url: str
