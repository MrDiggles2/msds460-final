from dataclasses import dataclass
from typing import Optional

@dataclass
class VMPlacement:
    vm_id: str
    server_id: Optional[str]  # None means unassigned
