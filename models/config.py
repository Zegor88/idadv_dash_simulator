from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .enums import LocationRarityType

@dataclass
class LocationLevel:
    cost: int
    xp_reward: int

@dataclass
class LocationRarityConfig:
    user_level_required: int
    keys_reward: int

@dataclass
class LocationConfig:
    rarity: LocationRarityType
    levels: Dict[int, LocationLevel] = field(default_factory=dict)

@dataclass
class UserLevelConfig:
    xp_required: int
    gold_per_sec: float
    keys_reward: int

@dataclass
class SimulationConfig:
    locations: Dict[int, LocationConfig]
    location_cooldowns: Dict[int, int]
    location_rarity_config: Dict[LocationRarityType, LocationRarityConfig]
    user_levels: Dict[int, UserLevelConfig]
    check_schedule: List[int] 