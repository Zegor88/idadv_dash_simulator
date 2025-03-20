"""
Утилиты для обработки данных симуляции.
"""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd

# Извлекает данные о локациях из истории симуляции
def extract_location_data(history: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Извлекает данные о локациях из истории симуляции.
    
    Args:
        history: История симуляции
        
    Returns:
        Dict: Словарь данных о локациях
    """
    locations_data = {}
    
    # Инициализируем локации из первого состояния
    if history:
        first_state = history[0]
        for loc_id, loc_state in first_state["locations"].items():
            locations_data[int(loc_id)] = {
                "current_level": loc_state["current_level"],
                "available": loc_state["available"],
                "upgrades_count": 0,
                "total_cost": 0,
                "total_xp": 0,
                "total_keys": 0,
                "upgrade_times": []
            }
    
    # Собираем информацию об улучшениях
    for state in history:
        # Обновляем состояние локаций
        for loc_id, loc_state in state["locations"].items():
            loc_id = int(loc_id)
            locations_data[loc_id].update({
                "current_level": loc_state["current_level"],
                "available": loc_state["available"]
            })
        
        # Обрабатываем улучшения
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                loc_id = int(action["location_id"])
                locations_data[loc_id]["upgrades_count"] += 1
                locations_data[loc_id]["total_cost"] += action["cost"]
                locations_data[loc_id]["total_xp"] += action["reward_xp"]
                locations_data[loc_id]["total_keys"] += action["reward_keys"]
                locations_data[loc_id]["upgrade_times"].append(action["timestamp"])
    
    return locations_data

# Извлекает временную шкалу улучшений из истории симуляции
def extract_upgrades_timeline(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Извлекает временную шкалу улучшений из истории симуляции.
    
    Args:
        history: История симуляции
        
    Returns:
        List: Список улучшений
    """
    upgrades_timeline = []
    
    for state in history:
        current_gold = state["balance"]["gold"]  # Текущий баланс золота
        
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                upgrades_timeline.append({
                    "timestamp": action["timestamp"],
                    "location_id": int(action["location_id"]),
                    "cost": action["cost"],
                    "new_level": action["new_level"],
                    "reward_xp": action["reward_xp"],
                    "reward_keys": action["reward_keys"],
                    "day": action["timestamp"] / 86400,
                    "gold_before": current_gold + action["cost"]  # Баланс до покупки = текущий + стоимость
                })
    
    # Сортируем по времени
    upgrades_timeline.sort(key=lambda x: x["timestamp"])
    
    return upgrades_timeline

# Извлекает данные об уровне персонажа из истории симуляции
def extract_level_data(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Извлекает данные об уровне персонажа из истории симуляции.
    
    Args:
        history: История симуляции
        
    Returns:
        List: Список данных об уровне
    """
    level_data = []
    
    for state in history:
        level_data.append({
            "timestamp": state["timestamp"],
            "level": state["balance"]["user_level"],
            "xp": state["balance"]["xp"],
            "day": state["timestamp"] / 86400
        })
        
        # Добавляем действия повышения уровня для более точного графика
        for action in state["actions"]:
            if action["type"] == "level_up":
                level_data.append({
                    "timestamp": action["timestamp"],
                    "level": action["new_level"],
                    "xp": state["balance"]["xp"],  # Используем XP из состояния
                    "day": action["timestamp"] / 86400
                })
    
    # Сортируем по времени
    level_data.sort(key=lambda x: x["timestamp"])
    
    return level_data

# Извлекает данные о ресурсах из истории симуляции
def extract_resource_data(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Извлекает данные о ресурсах из истории симуляции.
    
    Args:
        history: История симуляции
        
    Returns:
        List: Список данных о ресурсах
    """
    resources_data = []
    
    for state in history:
        resources_data.append({
            "timestamp": state["timestamp"],
            "gold": state["balance"]["gold"],
            "keys": state["balance"]["keys"],
            "earn_per_sec": state["balance"]["earn_per_sec"],
            "day": state["timestamp"] / 86400,
            "earn_per_hour": state["balance"]["earn_per_sec"] * 3600,
            "earn_per_day": state["balance"]["earn_per_sec"] * 86400
        })
    
    # Сортируем по времени
    resources_data.sort(key=lambda x: x["timestamp"])
    
    return resources_data

# Рассчитывает периоды стагнации (без улучшений)
def calculate_stagnation_periods(upgrades_timeline: List[Dict[str, Any]], min_duration: int = 86400) -> List[Dict[str, Any]]:
    """
    Рассчитывает периоды стагнации (без улучшений).
    
    Args:
        upgrades_timeline: Временная шкала улучшений
        min_duration: Минимальная длительность периода в секундах (по умолчанию 1 день)
        
    Returns:
        List: Список периодов стагнации
    """
    stagnation_periods = []
    
    for i in range(1, len(upgrades_timeline)):
        interval = upgrades_timeline[i]["timestamp"] - upgrades_timeline[i-1]["timestamp"]
        if interval > min_duration:
            stagnation_periods.append({
                "start": upgrades_timeline[i-1]["timestamp"],
                "end": upgrades_timeline[i]["timestamp"],
                "duration": interval,
                "start_day": upgrades_timeline[i-1]["timestamp"] / 86400,
                "duration_days": interval / 86400
            })
    
    return stagnation_periods

# Рассчитывает интервалы между улучшениями в часах
def calculate_intervals(upgrades_timeline: List[Dict[str, Any]]) -> List[float]:
    """
    Рассчитывает интервалы между улучшениями в часах.
    
    Args:
        upgrades_timeline: Временная шкала улучшений
        
    Returns:
        List: Список интервалов в часах
    """
    intervals = []
    
    for i in range(1, len(upgrades_timeline)):
        interval = (upgrades_timeline[i]["timestamp"] - upgrades_timeline[i-1]["timestamp"]) / 3600  # в часах
        intervals.append(interval)
    
    return intervals

# Рассчитывает количество улучшений по дням
def calculate_upgrades_per_day(upgrades_timeline: List[Dict[str, Any]]) -> Dict[int, int]:
    """
    Рассчитывает количество улучшений по дням.
    
    Args:
        upgrades_timeline: Временная шкала улучшений
        
    Returns:
        Dict: Словарь {день: количество_улучшений}
    """
    upgrades_per_day = {}
    
    for upgrade in upgrades_timeline:
        day = int(upgrade["timestamp"] // 86400)
        upgrades_per_day[day] = upgrades_per_day.get(day, 0) + 1
    
    return upgrades_per_day 