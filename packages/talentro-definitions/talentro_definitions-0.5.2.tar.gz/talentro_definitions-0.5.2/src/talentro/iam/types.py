from dataclasses import dataclass
from typing import List


@dataclass
class Domain:
    name: str
    verified: bool = False


@dataclass
class Organization:
    id: str
    name: str
    alias: str
    enabled: bool
    description: str
    attributes: dict
    domains: List[Domain]
