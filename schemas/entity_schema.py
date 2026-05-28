from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Entity:

    entity_id: str

    canonical_name: str

    normalized_name: str

    entity_type: str

    aliases: List[str] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )
