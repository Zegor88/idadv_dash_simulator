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
    locations_data = {}
    for state in history:
        for loc_id, loc_state in state["locations"].items():
            loc_id = int(loc_id)
            if loc_id not in locations_data:
                locations_data[loc_id] = {
                    "current_level": loc_state["current_level"],
                    "available": loc_state["available"],
                    "upgrades_count": 0,
                    "total_cost": 0,
                    "total_xp": 0,
                    "total_keys": 0
                }
            else:
                locations_data[loc_id].update({
                    "current_level": loc_state["current_level"],
                    "available": loc_state["available"]
                })
    
    # Извлекаем данные об улучшениях
    upgrades_timeline = extract_upgrades_timeline(history)
    
    # Обновляем данные о локациях на основе улучшений
    for upgrade in upgrades_timeline:
        loc_id = int(upgrade["location_id"])
        if loc_id in locations_data:
            locations_data[loc_id]["upgrades_count"] += 1
            locations_data[loc_id]["total_cost"] += -upgrade["gold_change"]
            locations_data[loc_id]["total_xp"] += upgrade["xp_change"]
            locations_data[loc_id]["total_keys"] += upgrade["keys_change"]
    
    # Проверяем наличие данных об улучшениях
    if not upgrades_timeline:
        # Создаем пустой график
        fig = go.Figure()
        fig.update_layout(
            title="Нет данных об улучшениях локаций",
            height=600
        )
        return fig
    
    # Создаем график с двумя подграфиками
    fig = create_subplot_figure(
        rows=2, cols=1,
        subplot_titles=(
            "Прогресс улучшения локаций во времени",
            "Влияние Cooldown на прогресс"
        ),
        vertical_spacing=0.15,
        height=800,
        row_heights=[0.6, 0.4]
    )
    
    # 1. График прогресса улучшений во времени
    timeline_data = {}
    for upgrade in upgrades_timeline:
        loc_id = upgrade["location_id"]
        if loc_id not in timeline_data:
            timeline_data[loc_id] = {
                "days": [],
                "levels": [],
                "costs": [],
                "xp_rewards": []
            }
        timeline_data[loc_id]["days"].append(upgrade["day"])
        timeline_data[loc_id]["levels"].append(upgrade["new_level"])
        timeline_data[loc_id]["costs"].append(-upgrade["gold_change"])  # Стоимость - это отрицательное изменение золота
        timeline_data[loc_id]["xp_rewards"].append(upgrade["xp_change"])
    
    # Создаем цветовую схему для локаций
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, (loc_id, data) in enumerate(timeline_data.items()):
        color = colors[i % len(colors)]  # Циклически используем цвета
        fig.add_trace(
            go.Scatter(
                x=data["days"],
                y=data["levels"],
                name=f"Локация {loc_id}",
                mode="lines+markers",
                line=dict(width=2, color=color),
                marker=dict(size=8, color=color),
                hovertemplate="День: %{x:.1f}<br>Уровень: %{y}<extra>Локация %{customdata}</extra>",
                legendgroup=f"Локация {loc_id}",
                customdata=[loc_id] * len(data["days"])
            ),
            row=1, col=1
        )
    
    # 2. График влияния Cooldown
    cooldown_data = {}
    for upgrade in upgrades_timeline:
        loc_id = upgrade["location_id"]
        if loc_id not in cooldown_data:
            cooldown_data[loc_id] = {
                "upgrade_intervals": [],
                "levels": []
            }
        
        # Находим интервал до следующего улучшения этой локации
        next_upgrade = next(
            (u for u in upgrades_timeline 
             if u["location_id"] == loc_id and u["day"] > upgrade["day"]),
            None
        )
        if next_upgrade:
            # Преобразуем интервал из дней в минуты (дни * 24 часа * 60 минут)
            interval = (next_upgrade["day"] - upgrade["day"]) * 24
            cooldown_data[loc_id]["upgrade_intervals"].append(interval)
            cooldown_data[loc_id]["levels"].append(upgrade["new_level"])
    
    for i, (loc_id, data) in enumerate(cooldown_data.items()):
        if data["upgrade_intervals"]:
            color = colors[i % len(colors)]  # Используем тот же цвет, что и в первом графике
            fig.add_trace(
                go.Scatter(
                    x=data["levels"],
                    y=data["upgrade_intervals"],
                    name=f"Локация {loc_id}",
                    mode="lines+markers",
                    line=dict(width=2, color=color),
                    marker=dict(size=8, color=color),
                    hovertemplate="Уровень: %{x}<br>Интервал: %{y:.1f} часов<extra>Локация %{customdata}</extra>",
                    legendgroup=f"Локация {loc_id}",
                    showlegend=False,  # Не показываем в легенде, так как уже есть в первом графике
                    customdata=[loc_id] * len(data["upgrade_intervals"])
                ),
                row=2, col=1
            )
    
    # Обновляем оси
    fig.update_xaxes(
        title_text="День игры",
        gridcolor='lightgray',
        showgrid=True,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Уровень локации",
        gridcolor='lightgray',
        showgrid=True,
        row=1, col=1
    )
    
    fig.update_xaxes(
        title_text="Уровень локации",
        gridcolor='lightgray',
        showgrid=True,
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="Интервал до следующего улучшения (часы)",
        gridcolor='lightgray',
        showgrid=True,
        row=2, col=1
    )
    
    # Обновляем layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=100, r=50, b=50, l=50),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


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
        time = state["timestamp"] % 86400
        # Пропускаем промежуточные состояния в тот же день
        if table_data and table_data[-1]["День"] == day:
            continue
        
        table_data.append({
            "День": day,
            "Время": f"{time // 3600:02d}:{time % 3600 // 60:02d}:{time % 60:02d}",
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
        {"name": "Время", "id": "Время"},
        {"name": "Золото", "id": "Золото", "type": "numeric", "format": {"specifier": ",.2f"}},
        {"name": "XP", "id": "XP", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Ключи", "id": "Ключи"},
        {"name": "Уровень", "id": "Уровень"},
        {"name": "Доход (gold/sec)", "id": "Доход (gold/sec)", "type": "numeric", "format": {"specifier": ",.4f"}},
        {"name": "Доход (gold/день)", "id": "Доход (gold/день)", "type": "numeric", "format": {"specifier": ",.2f"}},
    ]
    
    return table_data, columns

@app.callback(
    [Output("location-history-table", "data"),
     Output("location-history-table", "columns")],
    [Input("simulation-data-store", "data")],
    prevent_initial_call=True
)
def update_location_history(data):
    """
    Обновляет таблицу истории улучшений локаций.
    
    Args:
        data: Данные симуляции
        
    Returns:
        tuple: (данные таблицы, колонки таблицы)
    """
    if data is None or "history" not in data:
        return [], []
    
    history = data["history"]
    if not history:
        return [], []
    
    # Получаем данные об улучшениях
    upgrades_timeline = extract_upgrades_timeline(history)
    
    if not upgrades_timeline:
        return [], []
    
    # Форматируем данные для таблицы
    table_data = []
    
    for upgrade in upgrades_timeline:
        # Вычисляем день и время
        timestamp = upgrade["timestamp"]
        day = int(timestamp // 86400)
        time_seconds = int(timestamp % 86400)
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        seconds = (time_seconds % 3600) % 60
        
        table_data.append({
            "День": day + 1,  # День начинается с 1
            "Время": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            "Локация": f"Локация {upgrade['location_id']}",
            "Новый уровень": upgrade["new_level"],
            "Золото ДО": f"{upgrade['gold_before']:,.0f}",
            "Стоимость": f"{-upgrade['gold_change']:,.0f}",  # Стоимость - это отрицательное изменение золота
            "Баланс золота": f"{upgrade['gold_after']:,.0f}",
            "XP ДО": f"{upgrade['xp_before']:,.0f}",
            "Награда XP": f"{upgrade['xp_change']:,.0f}",
            "Баланс XP": f"{upgrade['xp_after']:,.0f}",
            "Ключи ДО": f"{upgrade['keys_before']:,.0f}",
            "Награда Ключи": f"{upgrade['keys_change']:,.0f}",
            "Баланс Ключи": f"{upgrade['keys_after']:,.0f}"
        })
    
    # Сортируем по дню и времени
    table_data = sorted(table_data, key=lambda x: (x["День"], x["Время"]))
    
    # Определяем колонки
    columns = [
        {"name": "День", "id": "День", "type": "numeric"},
        {"name": "Время", "id": "Время"},
        {"name": "Локация", "id": "Локация"},
        {"name": "Новый уровень", "id": "Новый уровень", "type": "numeric"},
        {"name": "Золото ДО", "id": "Золото ДО"},
        {"name": "Стоимость", "id": "Стоимость"},
        {"name": "Баланс золота", "id": "Баланс золота"},
        {"name": "XP ДО", "id": "XP ДО"},
        {"name": "Награда XP", "id": "Награда XP"},
        {"name": "Баланс XP", "id": "Баланс XP"},
        {"name": "Ключи ДО", "id": "Ключи ДО"},
        {"name": "Награда Ключи", "id": "Награда Ключи"},
        {"name": "Баланс Ключи", "id": "Баланс Ключи"}
    ]
    
    return table_data, columns 