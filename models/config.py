from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from .enums import LocationRarityType

@dataclass
class LocationLevel:
    cost: int
    xp_reward: int

@dataclass
class LocationRarityConfig:
    user_level_required: int
    keys_reward: int
    cost_growth_ratio: float = 1.0

@dataclass
class LocationConfig:
    rarity: LocationRarityType
    levels: Dict[int, LocationLevel] = field(default_factory=dict)

@dataclass
class StartingBalanceConfig:
    """Конфигурация начального баланса игрока."""
    gold: float = 1000.0  # Начальное золото
    xp: int = 1      # Начальный опыт
    keys: int = 1    # Начальное количество ключей

@dataclass
class EconomyConfig:
    """Конфигурация экономики игры."""
    base_gold_per_sec: float
    earn_coefficient: float
    starting_balance: StartingBalanceConfig = field(default_factory=StartingBalanceConfig)
    game_duration: int = 1800  # 30 минут в секундах по умолчанию

class SimulationAlgorithm(Enum):
    """Алгоритмы симуляции улучшения локаций."""
    SEQUENTIAL = "sequential"  # Последовательное улучшение
    FIRST_AVAILABLE = "first_available"  # Первое доступное улучшение

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
    economy: EconomyConfig = field(default_factory=EconomyConfig)
    simulation_algorithm: SimulationAlgorithm = SimulationAlgorithm.SEQUENTIAL  # Алгоритм симуляции 