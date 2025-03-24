"""
Коллбеки для запуска и управления симуляцией.
"""

import numpy as np
import pandas as pd
import dash
from dash import Input, Output, State, callback, html, no_update
from typing import Dict, List, Any, Tuple, Optional
import json

from idadv_dash_simulator.simulator import Simulator
from idadv_dash_simulator.config.simulation_config import create_sample_config
from idadv_dash_simulator.utils.economy import format_time
from idadv_dash_simulator.models.config import EconomyConfig, SimulationAlgorithm, SimulationConfig, StartingBalanceConfig
from idadv_dash_simulator.dashboard import app

def create_status_message(status_type: str, message: str, details: Optional[str] = None) -> html.Div:
    """
    Создает форматированное сообщение о статусе симуляции.
    
    Args:
        status_type: Тип статуса ('success', 'info', 'warning', 'error')
        message: Основное сообщение
        details: Дополнительная информация (опционально)
        
    Returns:
        html.Div: Отформатированный блок сообщения
    """
    status_colors = {
        'success': '#28a745',
        'info': '#6c757d',
        'warning': '#ffc107',
        'error': '#dc3545'
    }
    
    components = [html.P(message, style={"color": status_colors.get(status_type, '#6c757d')})]
    
    if details:
        components.append(html.P(details, style={"fontSize": "0.9em"}))
        
    return html.Div(components)

@app.callback(
    Output("check-times-display", "children"),
    Input("check-times-store", "data")
)
def update_check_times_display(data):
    """
    Обновляет отображение времен проверок.
    
    Args:
        data: Данные о временах проверок
        
    Returns:
        list: Список компонентов для отображения времен проверок
    """
    print("update_check_times_display вызвана с данными:", data)
    
    if not data or "times" not in data:
        times = ["08:00", "12:00", "16:00", "20:00"]
    else:
        times = data["times"]
    
    time_items = []
    for i, time in enumerate(times):
        time_item = html.Div(
            [
                html.Span(time, style={"marginRight": "10px", "fontWeight": "normal", "fontSize": "14px"}),
                html.Button(
                    "-", 
                    id={"type": "remove-specific-time-button", "index": i},
                    style={
                        "border": "none",
                        "backgroundColor": "#f44336",
                        "color": "white",
                        "borderRadius": "4px",
                        "cursor": "pointer",
                        "width": "25px",
                        "height": "25px",
                        "fontSize": "14px",
                        "padding": "0"
                    }
                )
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "marginBottom": "5px",
                "padding": "5px"
            }
        )
        time_items.append(time_item)
    
    print("Создано элементов:", len(time_items))
    
    return [
        html.Div(time_items, style={"marginBottom": "10px"}),
        html.Div(
            [
                html.Button(
                    "+", 
                    id="add-check-time-button",
                    style={
                        "border": "none",
                        "backgroundColor": "#4CAF50",
                        "color": "white",
                        "borderRadius": "4px",
                        "cursor": "pointer",
                        "width": "25px",
                        "height": "25px",
                        "fontSize": "14px",
                        "padding": "0"
                    }
                )
            ]
        )
    ]

@app.callback(
    Output("check-times-store", "data"),
    [Input({"type": "remove-specific-time-button", "index": dash.ALL}, "n_clicks"),
     Input("add-check-time-button", "n_clicks")],
    [State("check-times-store", "data")],
    prevent_initial_call=True
)
def update_check_times(remove_specific_clicks, add_clicks, current_data):
    """
    Обновляет список времен проверок при нажатии на кнопки добавления или удаления.
    
    Args:
        remove_specific_clicks: Количество нажатий на кнопки удаления конкретных времен
        add_clicks: Количество нажатий на кнопку добавления
        current_data: Текущие данные о временах проверок
        
    Returns:
        dict: Обновленные данные о временах проверок
    """
    # Определяем, какая кнопка была нажата
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_data
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if not current_data or "times" not in current_data:
        current_data = {"times": ["08:00", "12:00", "16:00", "20:00"]}
    
    times = current_data["times"]
    
    # Обработка нажатия на кнопку добавления
    if trigger_id == "add-check-time-button":
        # Добавляем новое время проверки
        if times:
            last_time = times[-1]
            h, m = map(int, last_time.split(":"))
            new_h = (h + 4) % 24
            new_time = f"{new_h:02d}:00"
        else:
            new_time = "12:00"
        
        times.append(new_time)
    
    # Обработка нажатия на кнопку удаления конкретного времени
    elif "remove-specific-time-button" in trigger_id:
        try:
            # Извлекаем индекс кнопки из ID
            button_id = json.loads(trigger_id)
            index = button_id.get("index")
            
            # Удаляем время с указанным индексом
            if index is not None and 0 <= index < len(times):
                times.pop(index)
        except (json.JSONDecodeError, ValueError, KeyError):
            # Игнорируем ошибки при парсинге ID
            pass
    
    # Убеждаемся, что список времен не пустой
    if not times:
        times = ["12:00"]
    
    return {"times": times}

@app.callback(
    [Output("simulation-status", "children"),
     Output("simulation-data-store", "data"),
     Output("user-levels-store", "data"),
     Output("auto-run-store", "data")],
    [Input("run-simulation-button", "n_clicks")],
    [State("base-gold-per-sec-input", "value"),
     State("earn-coefficient-input", "value"),
     State("cooldown-multiplier-slider", "value"),
     State("check-times-store", "data"),
     State("game-duration-input", "value"),
     State("simulation-algorithm-radio", "value"),
     State("starting-gold-input", "value"),
     State("starting-xp-input", "value"),
     State("starting-keys-input", "value"),
     State("auto-run-store", "data")]
)
def run_simulation(n_clicks, base_gold, earn_coefficient, cooldown_multiplier, 
                  check_times_data, game_duration, simulation_algorithm, 
                  starting_gold, starting_xp, starting_keys, auto_run_data):
    """
    Запускает симуляцию и возвращает результаты.
    
    Args:
        n_clicks: Количество нажатий на кнопку
        base_gold: Базовое значение золота в секунду
        earn_coefficient: Коэффициент роста
        cooldown_multiplier: Множитель кулдауна между улучшениями
        check_times_data: Данные о временах проверок
        game_duration: Длительность игровой сессии в минутах
        simulation_algorithm: Алгоритм симуляции улучшения локаций
        starting_gold: Начальное количество золота
        starting_xp: Начальный опыт
        starting_keys: Начальное количество ключей
        auto_run_data: Состояние флага автозапуска
        
    Returns:
        list: [статус, данные симуляции, уровни пользователя, флаг автозапуска]
    """
    # Для первичной загрузки страницы или если кнопка не была нажата, не запускаем симуляцию
    if n_clicks is None or n_clicks == 0:
        status_message = create_status_message(
            'info', 
            "Simulation is not running. Set the parameters and click the 'Run simulation' button.", 
            "Simulation data will be displayed after running."
        )
        return status_message, no_update, no_update, {"auto_run": False}
    
    # Создаем и настраиваем конфигурацию
    config = _create_simulation_config(
        base_gold=base_gold,
        earn_coefficient=earn_coefficient,
        cooldown_multiplier=cooldown_multiplier,
        check_times_data=check_times_data,
        game_duration=game_duration,
        simulation_algorithm=simulation_algorithm,
        starting_gold=starting_gold,
        starting_xp=starting_xp,
        starting_keys=starting_keys
    )
    
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
    
    algorithm_name = "Sequential improvement" if config.simulation_algorithm == SimulationAlgorithm.SEQUENTIAL else "First available improvement"
    
    # Создаем информацию о расписании проверок
    check_times = []
    for seconds in config.check_schedule:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        check_times.append(f"{h:02d}:{m:02d}")
    
    check_times_str = ", ".join(check_times)
    
    # Создаем информационное сообщение о завершении симуляции
    formatted_time = format_time(result.timestamp)
    status_message = create_status_message(
        'success',
        f"Simulation successfully completed in {formatted_time}!",
        f"Algorithm: {algorithm_name}, Base gold: {base_gold}, Earn coefficient: {earn_coefficient}, "
        f"Cooldown multiplier: {cooldown_multiplier}, Checks: {check_times_str}, "
        f"Session duration: {game_duration} min."
    )
    
    # Переводим историю в формат JSON для хранения
    history_data = [state for state in result.history]
    
    # Преобразуем конфигурацию в формат для хранения
    config_data = {
        "locations": {
            str(loc_id): {
                "rarity": str(loc_config.rarity.value),
                "levels": {
                    str(level): {
                        "cost": level_config.cost,
                        "xp_reward": level_config.xp_reward
                    } for level, level_config in loc_config.levels.items()
                }
            } for loc_id, loc_config in config.locations.items()
        },
        "location_cooldowns": {str(level): cooldown for level, cooldown in config.location_cooldowns.items()},
        "simulation_algorithm": config.simulation_algorithm.value,
        "game_duration": config.economy.game_duration,
        "check_schedule": config.check_schedule
    }
    
    simulation_data = {
        "history": history_data, 
        "timestamp": result.timestamp, 
        "stop_reason": result.stop_reason,
        "config": config_data
    }
    
    return status_message, simulation_data, user_levels_data, {"auto_run": True}

def _create_simulation_config(base_gold: float, earn_coefficient: float, cooldown_multiplier: float, 
                             check_times_data: dict, game_duration: int, simulation_algorithm: str, 
                             starting_gold: float, starting_xp: float, starting_keys: int) -> SimulationConfig:
    """
    Создает конфигурацию симуляции на основе параметров.
    
    Args:
        base_gold: Базовое значение золота в секунду
        earn_coefficient: Коэффициент роста
        cooldown_multiplier: Множитель кулдауна между улучшениями
        check_times_data: Данные о временах проверок
        game_duration: Длительность игровой сессии в минутах
        simulation_algorithm: Алгоритм симуляции
        starting_gold: Начальное количество золота
        starting_xp: Начальный опыт
        starting_keys: Начальное количество ключей
        
    Returns:
        SimulationConfig: Конфигурация для симуляции
    """
    # Создаем конфигурацию
    config = create_sample_config()
    
    # Проверка и приведение параметров к допустимым значениям
    if base_gold is None or base_gold <= 0:
        base_gold = config.economy.base_gold_per_sec
        
    if earn_coefficient is None or earn_coefficient <= 0:
        earn_coefficient = config.economy.earn_coefficient
        
    if cooldown_multiplier is None or cooldown_multiplier <= 0:
        cooldown_multiplier = 1.0
        
    if simulation_algorithm is None:
        simulation_algorithm = SimulationAlgorithm.SEQUENTIAL.value
        
    if starting_gold is None or starting_gold < 0:
        starting_gold = 1000.0
        
    if starting_xp is None or starting_xp < 0:
        starting_xp = 1
        
    if starting_keys is None or starting_keys < 0:
        starting_keys = 1
        
    if game_duration is None or game_duration <= 0:
        game_duration = 15  # 15 минут по умолчанию
    
    # Преобразуем длительность игровой сессии в секунды
    game_duration_seconds = game_duration * 60
    
    # Обновляем экономические настройки с начальным балансом и длительностью сессии
    config.economy = EconomyConfig(
        base_gold_per_sec=base_gold,
        earn_coefficient=earn_coefficient,
        starting_balance=StartingBalanceConfig(
            gold=starting_gold,
            xp=int(starting_xp),
            keys=int(starting_keys)
        ),
        game_duration=game_duration_seconds
    )
    
    # Обновляем множитель кулдауна
    for level, cooldown in config.location_cooldowns.items():
        config.location_cooldowns[level] = int(cooldown * cooldown_multiplier)
    
    # Устанавливаем алгоритм симуляции
    config.simulation_algorithm = SimulationAlgorithm(simulation_algorithm)
    
    # Обновляем расписание проверок на основе введенных времен
    _update_check_schedule_from_times(config, check_times_data)
    
    return config

def _update_check_schedule_from_times(config: SimulationConfig, check_times_data: dict) -> None:
    """
    Обновляет расписание проверок в конфигурации на основе списка времен.
    
    Args:
        config: Конфигурация симуляции
        check_times_data: Данные о временах проверок
    """
    day_seconds = 86400  # секунд в дне
    
    # Проверяем наличие данных
    if not check_times_data or "times" not in check_times_data or not check_times_data["times"]:
        # Если данных нет, используем значения по умолчанию из конфигурации
        check_schedule = [
            28800,      # 08:00
            43200,      # 12:00
            57600,      # 16:00
            72000,      # 20:00
        ]
        config.check_schedule = check_schedule
        return
    
    # Преобразуем времена в секунды от начала дня
    check_schedule = []
    for time_str in check_times_data["times"]:
        try:
            # Парсим время в формате "HH:MM"
            hours, minutes = map(int, time_str.split(":"))
            seconds = hours * 3600 + minutes * 60
            check_schedule.append(seconds)
        except (ValueError, IndexError):
            # В случае неправильного формата пропускаем
            continue
    
    # Если не удалось получить ни одного корректного времени, используем значение по умолчанию
    if not check_schedule:
        check_schedule = [
            28800,      # 08:00
            43200,      # 12:00
            57600,      # 16:00
            72000       # 20:00
        ]
    
    # Сортируем расписание
    check_schedule.sort()
    
    # Обновляем расписание в конфигурации
    config.check_schedule = check_schedule 