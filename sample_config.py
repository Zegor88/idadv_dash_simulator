from idadv_dash_simulator.models.enums import LocationRarityType
from idadv_dash_simulator.models.config import (
    LocationLevel,
    LocationRarityConfig,
    LocationConfig,
    UserLevelConfig,
    SimulationConfig
)

def create_sample_config() -> SimulationConfig:
    """Создает пример конфигурации для симуляции."""
    
    # Уровни локаций
    location_levels = {
        1: LocationLevel(cost=100, xp_reward=10),
        2: LocationLevel(cost=300, xp_reward=30),
        3: LocationLevel(cost=600, xp_reward=60),
        4: LocationLevel(cost=1200, xp_reward=120),
        5: LocationLevel(cost=2400, xp_reward=240),
    }
    
    # Конфигурация локаций по редкости
    location_rarity_config = {
        LocationRarityType.COMMON: LocationRarityConfig(user_level_required=1, keys_reward=1),
        LocationRarityType.RARE: LocationRarityConfig(user_level_required=2, keys_reward=2),
        LocationRarityType.EPIC: LocationRarityConfig(user_level_required=3, keys_reward=3),
        LocationRarityType.LEGENDARY: LocationRarityConfig(user_level_required=4, keys_reward=5),
    }
    
    # Локации
    locations = {
        1: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        2: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        3: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        4: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        5: LocationConfig(rarity=LocationRarityType.EPIC, levels=location_levels.copy()),
        6: LocationConfig(rarity=LocationRarityType.LEGENDARY, levels=location_levels.copy()),
    }
    
    # Кулдауны для уровней локаций (в секундах)
    location_cooldowns = {
        1: 3600,      # 1 час
        2: 7200,      # 2 часа
        3: 14400,     # 4 часа
        4: 28800,     # 8 часов
        5: 43200,     # 12 часов
    }
    
    # Уровни пользователя
    user_levels = {
        1: UserLevelConfig(xp_required=0, gold_per_sec=0.5, keys_reward=0),
        2: UserLevelConfig(xp_required=100, gold_per_sec=1.0, keys_reward=5),
        3: UserLevelConfig(xp_required=300, gold_per_sec=2.0, keys_reward=10),
        4: UserLevelConfig(xp_required=900, gold_per_sec=4.0, keys_reward=15),
        5: UserLevelConfig(xp_required=2700, gold_per_sec=8.0, keys_reward=25),
    }
    
    # Расписание проверок (5 раз в день с 8-часовым интервалом сна)
    # Проверяем в 8:00, 12:00, 16:00, 20:00, 22:00
    check_schedule = [
        8 * 3600,     # 8:00
        12 * 3600,    # 12:00
        16 * 3600,    # 16:00
        20 * 3600,    # 20:00
        22 * 3600,    # 22:00
    ]
    
    return SimulationConfig(
        locations=locations,
        location_cooldowns=location_cooldowns,
        location_rarity_config=location_rarity_config,
        user_levels=user_levels,
        check_schedule=check_schedule
    ) 