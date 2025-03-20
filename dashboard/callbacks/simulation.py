"""
Коллбеки для запуска и управления симуляцией.
"""

import numpy as np
import pandas as pd
from dash import Input, Output, State, callback, html

from idadv_dash_simulator.simulator import Simulator
from idadv_dash_simulator.config.simulation_config import create_sample_config
from idadv_dash_simulator.utils.economy import format_time
from idadv_dash_simulator.models.config import EconomyConfig, SimulationAlgorithm
from idadv_dash_simulator.dashboard import app

@app.callback(
    [Output("simulation-status", "children"),
     Output("simulation-data-store", "data"),
     Output("user-levels-store", "data")],
    [Input("run-simulation-button", "n_clicks")],
    [State("base-gold-per-sec-input", "value"),
     State("earn-coefficient-input", "value"),
     State("cooldown-multiplier-slider", "value"),
     State("checks-per-day-slider", "value"),
     State("simulation-algorithm-radio", "value")]
)
def run_simulation(n_clicks, base_gold, earn_coefficient, cooldown_multiplier, checks_per_day, simulation_algorithm):
    """
    Запускает симуляцию и возвращает результаты.
    
    Args:
        n_clicks: Количество нажатий на кнопку
        base_gold: Базовое значение золота в секунду
        earn_coefficient: Коэффициент роста
        cooldown_multiplier: Множитель кулдауна между улучшениями
        checks_per_day: Количество проверок в день
        simulation_algorithm: Алгоритм симуляции улучшения локаций
        
    Returns:
        list: [статус, данные симуляции, уровни пользователя]
    """
    if n_clicks is None:
        return "Симуляция не запущена", None, None
    
    # Создаем конфигурацию
    config = create_sample_config()
    
    # Обновляем экономические настройки
    config.economy = EconomyConfig(
        base_gold_per_sec=base_gold,
        earn_coefficient=earn_coefficient
    )
    
    # Обновляем множитель кулдауна
    for level, cooldown in config.location_cooldowns.items():
        config.location_cooldowns[level] = int(cooldown * cooldown_multiplier)
    
    # Устанавливаем алгоритм симуляции
    config.simulation_algorithm = SimulationAlgorithm(simulation_algorithm)
    
    # Обновляем расписание проверок
    day_seconds = 86400  # секунд в дне
    if checks_per_day > 0:
        step = day_seconds / checks_per_day
        # Создаем равномерное распределение проверок в течение дня (с 8:00 до 22:00)
        active_hours = 14  # с 8:00 до 22:00
        active_seconds = active_hours * 3600
        start_time = 8 * 3600  # 8:00
        
        if checks_per_day == 1:
            # Если одна проверка, ставим её в середине дня
            config.check_schedule = [start_time + active_seconds // 2]
        else:
            # Если несколько проверок, распределяем равномерно
            check_interval = active_seconds / (checks_per_day - 1) if checks_per_day > 1 else active_seconds
            config.check_schedule = [int(start_time + i * check_interval) for i in range(checks_per_day)]
    
    # Запускаем симуляцию
    simulator = Simulator(config)
    result = simulator.run_simulation()
    
    # Подготавливаем данные для сохранения
    user_levels_data = {
        level: {
            "xp_required": level_config.xp_required,
            "gold_per_sec": level_config.gold_per_sec,
            "keys_reward": level_config.keys_reward
        } for level, level_config in config.user_levels.items()
    }
    
    algorithm_name = "Последовательное улучшение" if config.simulation_algorithm == SimulationAlgorithm.SEQUENTIAL else "Первое доступное улучшение"
    
    return html.Div([
        html.P(f"Симуляция успешно завершена"),
        html.P(f"Алгоритм: {algorithm_name}")
    ]), {"history": result.history, "stop_reason": result.stop_reason}, user_levels_data


@app.callback(
    [Output("completion-time", "children"),
     Output("final-resources", "children")],
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_completion_info(data):
    """
    Обновляет информацию о завершении симуляции.
    
    Args:
        data: Данные симуляции
        
    Returns:
        list: [информация о времени, информация о ресурсах]
    """
    if data is None or "history" not in data:
        return "Нет данных", "Нет данных"
    
    history = data["history"]
    if not history:
        return "Нет данных", "Нет данных"
    
    last_state = history[-1]
    balance = last_state["balance"]
    
    timestamp = last_state["timestamp"]
    days = timestamp // 86400
    hours = (timestamp % 86400) // 3600
    
    completion_info = html.Div([
        html.H5("Общая информация:"),
        html.P(f"Время прохождения: {days} дней, {hours} часов ({timestamp} секунд)"),
        html.P(f"Причина остановки: {data.get('stop_reason', 'Не указана')}")
    ])
    
    resources_info = html.Div([
        html.H5("Финальные ресурсы:"),
        html.P(f"Золото: {balance['gold']:.2f}"),
        html.P(f"Опыт: {balance['xp']}"),
        html.P(f"Ключи: {balance['keys']}"),
        html.P(f"Уровень: {balance['user_level']}"),
        html.P(f"Заработок в секунду: {balance['earn_per_sec']:.2f}")
    ])
    
    return completion_info, resources_info


@app.callback(
    Output("key-metrics", "children"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_key_metrics(data):
    """
    Обновляет ключевые метрики симуляции.
    
    Args:
        data: Данные симуляции
        
    Returns:
        html.Div: Блок с метриками
    """
    if data is None or "history" not in data:
        return "Нет данных"
    
    history = data["history"]
    if not history:
        return "Нет данных"
    
    # Собираем данные о улучшениях локаций
    location_upgrades = 0
    total_spent = 0
    
    for state in history:
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                location_upgrades += 1
                total_spent += -action["gold_change"]  # Стоимость - это отрицательное изменение золота
    
    # Собираем данные о стагнации
    days_with_upgrades = set()
    for state in history:
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                days_with_upgrades.add(action["timestamp"] // 86400)
    
    total_days = history[-1]["timestamp"] // 86400
    days_without_upgrades = total_days - len(days_with_upgrades)
    days_without_upgrades_percent = (days_without_upgrades / total_days * 100) if total_days > 0 else 0
    
    # Стиль для блоков метрик
    style_box = {
        "textAlign": "center", 
        "backgroundColor": "#f8f9fa", 
        "padding": "15px", 
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "width": "30%",
        "margin": "10px"
    }
    
    return html.Div([
        html.Div([
            html.H3(f"{location_upgrades}"),
            html.P("Улучшений локаций")
        ], style=style_box),
        
        html.Div([
            html.H3(f"{total_spent:,.0f}"),
            html.P("Потрачено золота")
        ], style=style_box),
        
        html.Div([
            html.H3(f"{days_without_upgrades_percent:.1f}%"),
            html.P(f"Дней без улучшений ({days_without_upgrades} из {total_days})")
        ], style=style_box)
    ], style={"display": "flex", "flexDirection": "row", "justifyContent": "space-around", "flexWrap": "wrap"}) 