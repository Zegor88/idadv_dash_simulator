"""
Утилиты для экономических расчетов и анализа игровой экономики.
"""

from typing import Dict, List, Union, Optional, Tuple
from functools import lru_cache
import math
import pandas as pd

@lru_cache(maxsize=128)
def calculate_gold_per_sec(base_gold: float, earn_coefficient: float, level: int) -> float:
    """
    Рассчитывает значение gold_per_sec для заданного уровня.
    Использует кэширование для оптимизации вычислений.
    
    Args:
        base_gold: Базовое значение золота для первого уровня
        earn_coefficient: Коэффициент роста (например, 1.091 для роста на 9.1%)
        level: Уровень персонажа
    
    Returns:
        float: Значение gold_per_sec для указанного уровня
    """
    if level <= 1:
        return base_gold
        
    # Каждый следующий уровень умножает предыдущее значение на коэффициент в степени уровня
    prev_value = calculate_gold_per_sec(base_gold, earn_coefficient, level - 1)
    return prev_value * (earn_coefficient ** (level - 1))

# Преобразует количество секунд в удобочитаемый формат времени
def format_time(seconds: int) -> str:
    """
    Преобразует количество секунд в удобочитаемый формат времени.
    
    Args:
        seconds: Количество секунд
        
    Returns:
        str: Строка с форматированным временем (дни, часы, минуты)
    """
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    # Форматируем строку в зависимости от наличия дней/часов
    if days > 0:
        return f"{days} дней, {hours} часов, {minutes} минут"
    elif hours > 0:
        return f"{hours} часов, {minutes} минут"
    else:
        return f"{minutes} минут"

def calculate_roi(cost: float, income_increase: float) -> Tuple[float, int]:
    """
    Рассчитывает ROI (Return on Investment) и время окупаемости для улучшения.
    
    Args:
        cost: Стоимость улучшения
        income_increase: Увеличение золота в секунду
    
    Returns:
        Tuple[float, int]: (ROI в процентах, время окупаемости в секундах)
    """
    if income_increase <= 0 or cost <= 0:
        return 0.0, float('inf')
    
    # Время окупаемости в секундах
    payback_time = cost / income_increase
    
    # ROI за один час (3600 секунд)
    hourly_roi = (income_increase * 3600 / cost) * 100
    
    return hourly_roi, math.ceil(payback_time)

def calculate_optimal_upgrade_sequence(
    location_costs: Dict[int, float], 
    location_rewards: Dict[int, float],
    budget: float,
    time_horizon: Optional[int] = None
) -> List[int]:
    """
    Рассчитывает оптимальную последовательность улучшений для максимизации дохода.
    
    Args:
        location_costs: Словарь с стоимостями улучшений локаций {id: cost}
        location_rewards: Словарь с наградами от улучшений {id: reward}
        budget: Доступный бюджет
        time_horizon: Горизонт времени в секундах (если указан, рассчитывает для заданного периода)
    
    Returns:
        List[int]: ID локаций в оптимальной последовательности улучшений
    """
    # Рассчитываем ROI для каждой локации
    roi_data = []
    
    for loc_id in location_costs:
        if loc_id in location_rewards:
            hourly_roi, payback_time = calculate_roi(location_costs[loc_id], location_rewards[loc_id])
            roi_data.append((loc_id, hourly_roi, payback_time, location_costs[loc_id]))
    
    # Сортируем по ROI (от высокого к низкому)
    roi_data.sort(key=lambda x: x[1], reverse=True)
    
    # Выбираем локации для улучшения в пределах бюджета
    upgrade_sequence = []
    remaining_budget = budget
    
    for loc_id, roi, _, cost in roi_data:
        if cost <= remaining_budget:
            upgrade_sequence.append(loc_id)
            remaining_budget -= cost
            
    return upgrade_sequence

def analyze_income_dynamics(history_data: List[Dict]) -> pd.DataFrame:
    """
    Анализирует динамику дохода на основе истории симуляции.
    
    Args:
        history_data: История симуляции
        
    Returns:
        pd.DataFrame: DataFrame с данными о динамике дохода
    """
    timestamps = []
    gold_values = []
    earn_rates = []
    
    for state in history_data:
        timestamps.append(state["timestamp"])
        gold_values.append(state["balance"]["gold"])
        earn_rates.append(state["balance"]["earn_per_sec"])
    
    return pd.DataFrame({
        "timestamp": timestamps,
        "gold": gold_values,
        "earn_per_sec": earn_rates,
        "gold_per_minute": [rate * 60 for rate in earn_rates],
        "gold_per_hour": [rate * 3600 for rate in earn_rates]
    })