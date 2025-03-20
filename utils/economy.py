"""
Утилиты для экономических расчетов.
"""

# Рассчитывает значение gold_per_sec для заданного уровня
def calculate_gold_per_sec(base_gold: float, earn_coefficient: float, level: int) -> float:
    """
    Рассчитывает значение gold_per_sec для заданного уровня.
    
    Args:
        base_gold: Базовое значение золота для первого уровня
        earn_coefficient: Коэффициент роста (например, 1.091 для роста на 9.1%)
        level: Уровень персонажа
    
    Returns:
        float: Значение gold_per_sec для указанного уровня
    """
    if level == 1:
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
    
    return f"{days} дней, {hours} часов, {minutes} минут"