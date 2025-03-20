"""
Коллбеки для анализа локаций.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, html

from idadv_dash_simulator.utils.plotting import create_subplot_figure, add_time_series, create_bar_chart
from idadv_dash_simulator.utils.data_processing import extract_location_data, extract_upgrades_timeline
from idadv_dash_simulator.dashboard import app

@app.callback(
    Output("locations-upgrades", "figure"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_locations_analysis(data):
    """
    Обновляет анализ локаций.
    
    Args:
        data: Данные симуляции
        
    Returns:
        go.Figure: График с анализом локаций
    """
    if data is None or "history" not in data:
        return {}
    
    history = data["history"]
    if not history:
        return {}
    
    # Извлекаем данные о локациях
    locations_data = extract_location_data(history)
    
    # Создаем график для локаций
    fig = create_subplot_figure(
        rows=2, cols=1,
        subplot_titles=(
            "Уровни локаций",
            "Стоимость и награды"
        ),
        vertical_spacing=0.3
    )
    
    # Сортируем локации по ID
    locations_sorted = sorted(locations_data.items())
    
    # Собираем информацию об уровнях локаций
    location_ids = []
    final_levels = []
    costs = []
    xp_rewards = []
    keys_rewards = []
    
    for loc_id, loc_data in locations_sorted:
        location_ids.append(loc_id)
        final_levels.append(loc_data["current_level"])
        costs.append(loc_data["total_cost"])
        xp_rewards.append(loc_data["total_xp"])
        keys_rewards.append(loc_data["total_keys"])
    
    # График уровней локаций
    create_bar_chart(
        fig,
        x=[f"Локация {loc_id}" for loc_id in location_ids],
        y=final_levels,
        name="Уровень",
        color="royalblue",
        row=1, col=1
    )
    
    # График стоимости
    create_bar_chart(
        fig,
        x=[f"Локация {loc_id}" for loc_id in location_ids],
        y=costs,
        name="Стоимость",
        color="indianred",
        row=2, col=1
    )
    
    # График XP наград
    create_bar_chart(
        fig,
        x=[f"Локация {loc_id}" for loc_id in location_ids],
        y=xp_rewards,
        name="Награда XP",
        color="green",
        row=2, col=1
    )
    
    # График ключей
    create_bar_chart(
        fig,
        x=[f"Локация {loc_id}" for loc_id in location_ids],
        y=keys_rewards,
        name="Награда ключи",
        color="purple",
        row=2, col=1
    )
    
    fig.update_layout(
        height=700,
        hovermode="closest"
    )
    
    # Обновляем оси
    fig.update_yaxes(title="Уровень", row=1, col=1)
    fig.update_yaxes(title="Значение", row=2, col=1)
    
    return fig


@app.callback(
    Output("upgrades-timeline-table", "data"),
    Output("upgrades-timeline-table", "columns"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_upgrades_timeline(data):
    """
    Обновляет таблицу временной шкалы улучшений.
    
    Args:
        data: Данные симуляции
        
    Returns:
        list: [данные таблицы, столбцы]
    """
    if data is None or "history" not in data:
        return [], []
    
    history = data["history"]
    if not history:
        return [], []
    
    # Извлекаем временную шкалу улучшений
    upgrades_timeline = extract_upgrades_timeline(history)
    
    if not upgrades_timeline:
        return [], []
    
    # Формируем данные для таблицы
    table_data = []
    
    for upgrade in upgrades_timeline:
        day = upgrade["day"]
        day_int = int(day)
        hour = (day - day_int) * 24
        
        table_data.append({
            "День": day_int,
            "Локация": f"Локация {upgrade['location_id']}",
            "Новый уровень": upgrade["new_level"],
            "Золото до улучшения": 0,  # Заполним позже
            "Стоимость": upgrade["cost"],
            "Золото после улучшения": 0,  # Заполним позже
            "Награда XP": upgrade["reward_xp"],
            "Награда ключи": upgrade["reward_keys"],
        })
    
    # Добавляем балансы до и после улучшения
    for i, upgrade in enumerate(upgrades_timeline):
        timestamp = upgrade["timestamp"]
        
        # Находим ближайшее состояние до улучшения
        prev_state = None
        for state in history:
            if state["timestamp"] <= timestamp:
                prev_state = state
            else:
                break
        
        # Находим ближайшее состояние после улучшения
        next_state = None
        for state in reversed(history):
            if state["timestamp"] >= timestamp:
                next_state = state
            else:
                break
        
        if prev_state:
            table_data[i]["Золото до улучшения"] = prev_state["balance"]["gold"] + upgrade["cost"]
        
        if next_state:
            table_data[i]["Золото после улучшения"] = next_state["balance"]["gold"]
    
    # Сортируем по дню
    table_data.sort(key=lambda x: (x["День"], x["Локация"]))
    
    # Определяем столбцы
    columns = [
        {"name": "День", "id": "День"},
        {"name": "Локация", "id": "Локация"},
        {"name": "Новый уровень", "id": "Новый уровень"},
        {"name": "Золото до улучшения", "id": "Золото до улучшения", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Стоимость", "id": "Стоимость", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Золото после улучшения", "id": "Золото после улучшения", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Награда XP", "id": "Награда XP"},
        {"name": "Награда ключи", "id": "Награда ключи"},
    ]
    
    return table_data, columns


@app.callback(
    Output("progress-details-table", "data"),
    Output("progress-details-table", "columns"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_progress_details(data):
    """
    Обновляет таблицу с детальной информацией о прогрессе.
    
    Args:
        data: Данные симуляции
        
    Returns:
        list: [данные таблицы, столбцы]
    """
    if data is None or "history" not in data:
        return [], []
    
    history = data["history"]
    if not history:
        return [], []
    
    # Формируем данные для таблицы
    table_data = []
    
    for state in history:
        day = state["timestamp"] // 86400
        # Пропускаем промежуточные состояния в тот же день
        if table_data and table_data[-1]["День"] == day:
            continue
        
        table_data.append({
            "День": day,
            "Золото": state["balance"]["gold"],
            "XP": state["balance"]["xp"],
            "Ключи": state["balance"]["keys"],
            "Уровень": state["balance"]["user_level"],
            "Доход (gold/sec)": state["balance"]["earn_per_sec"],
            "Доход (gold/день)": state["balance"]["earn_per_sec"] * 86400,
        })
    
    # Определяем столбцы
    columns = [
        {"name": "День", "id": "День"},
        {"name": "Золото", "id": "Золото", "type": "numeric", "format": {"specifier": ",.2f"}},
        {"name": "XP", "id": "XP", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Ключи", "id": "Ключи"},
        {"name": "Уровень", "id": "Уровень"},
        {"name": "Доход (gold/sec)", "id": "Доход (gold/sec)", "type": "numeric", "format": {"specifier": ",.4f"}},
        {"name": "Доход (gold/день)", "id": "Доход (gold/день)", "type": "numeric", "format": {"specifier": ",.2f"}},
    ]
    
    return table_data, columns 