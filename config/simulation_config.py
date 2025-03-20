"""
Конфигурационный файл для настроек симуляции.
"""

from idadv_dash_simulator.models.enums import LocationRarityType
from idadv_dash_simulator.models.config import (
    LocationLevel,
    LocationRarityConfig,
    LocationConfig,
    UserLevelConfig,
    SimulationConfig,
    EconomyConfig
)
from idadv_dash_simulator.utils.economy import calculate_gold_per_sec

def create_sample_config() -> SimulationConfig:
    """
    Создает пример конфигурации для симуляции.
    
    Returns:
        SimulationConfig: Конфигурация симуляции с значениями по умолчанию
    """
    
    # Параметры экономики
    economy = EconomyConfig(
        base_gold_per_sec=0.56,
        earn_coefficient=1.091,  # Коэффициент для роста на 9.1%
        game_duration=1800  # 30 минут в секундах
    )
    
    # Уровни локаций
    location_levels = {
        1: LocationLevel(cost=100, xp_reward=10),
        2: LocationLevel(cost=300, xp_reward=30),
        3: LocationLevel(cost=600, xp_reward=60),
        4: LocationLevel(cost=1200, xp_reward=120),
        5: LocationLevel(cost=2400, xp_reward=240),
        6: LocationLevel(cost=4800, xp_reward=480),
        7: LocationLevel(cost=9600, xp_reward=960),
        8: LocationLevel(cost=19200, xp_reward=1920),
        9: LocationLevel(cost=38400, xp_reward=3840),
        10: LocationLevel(cost=76800, xp_reward=7680),        
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
        3: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        4: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        5: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        6: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        7: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        8: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        9: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        10: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        11: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        12: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        13: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        14: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        15: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        16: LocationConfig(rarity=LocationRarityType.COMMON, levels=location_levels.copy()),
        17: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        18: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        19: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        20: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        21: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        22: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        23: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        24: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        25: LocationConfig(rarity=LocationRarityType.RARE, levels=location_levels.copy()),
        26: LocationConfig(rarity=LocationRarityType.LEGENDARY, levels=location_levels.copy()),
        27: LocationConfig(rarity=LocationRarityType.LEGENDARY, levels=location_levels.copy()),
        28: LocationConfig(rarity=LocationRarityType.LEGENDARY, levels=location_levels.copy()),
        29: LocationConfig(rarity=LocationRarityType.LEGENDARY, levels=location_levels.copy()),
        30: LocationConfig(rarity=LocationRarityType.LEGENDARY, levels=location_levels.copy()),
    }
    
    # Кулдауны для уровней локаций (в секундах)
    location_cooldowns = {
        1: 10,      # 10 секунд
        2: 20,      # 20 секунд
        3: 20,      # 20 секунд
        4: 30,      # 30 секунд
        5: 45,      # 45 секунд
        6: 60,      # 1 минута
        7: 90,      # 1.5 минуты
        8: 150,     # 2.5 минуты
        9: 210,     # 3.5 минуты
        10: 300,    # 5 минут
        11: 450,    # 7.5 минут
        12: 600,    # 10 минут
        13: 900,    # 15 минут
        14: 1200,   # 20 минут
        15: 1800,   # 30 минут
        16: 2700,   # 45 минут
        17: 3600,   # 1 час
        18: 5400,   # 1.5 часа
        19: 7200,   # 2 часа
        20: 14400,  # 4 часа        
    }
    
    # Уровни пользователя с автоматическим расчетом gold_per_sec
    user_levels = {
        level: UserLevelConfig(
            xp_required=xp_required,
            gold_per_sec=calculate_gold_per_sec(economy.base_gold_per_sec, economy.earn_coefficient, level),
            keys_reward=keys_reward
        )
        for level, (xp_required, keys_reward) in enumerate([
            (0, 0),        # level 1
            (100, 5),      # level 2
            (300, 10),     # level 3
            (900, 15),     # level 4
            (2700, 25),    # level 5
            (8100, 35),    # level 6
            (24300, 45),   # level 7
            (72900, 55),   # level 8
            (218700, 65),  # level 9
            (656100, 75),  # level 10
        ], 1)  # start enumeration from 1
    }
    
    # Расписание проверок
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
        check_schedule=check_schedule,
        economy=economy
    ) 