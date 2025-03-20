"""
Коллбеки для анализа прогресса игрока.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Input, Output, State, callback, html

from idadv_dash_simulator.utils.plotting import create_subplot_figure, add_time_series, create_bar_chart
from idadv_dash_simulator.utils.data_processing import (
    extract_upgrades_timeline, 
    calculate_intervals,
    calculate_upgrades_per_day,
    calculate_stagnation_periods,
    extract_level_data,
    extract_resource_data,
    extract_daily_events_data
)
from idadv_dash_simulator.config.dashboard_config import PLOT_COLORS
from idadv_dash_simulator.dashboard import app

@app.callback(
    [Output("progression-pace", "figure"),
     Output("stagnation-analysis", "figure"),
     Output("progression-stats", "children")],
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_progression_analysis(data):
    """
    Обновляет анализ темпа прогрессии.
    
    Args:
        data: Данные симуляции
        
    Returns:
        list: [график темпа, график стагнации, статистика]
    """
    if data is None or "history" not in data:
        return {}, {}, "Нет данных"
    
    history = data["history"]
    if not history:
        return {}, {}, "Нет данных"
    
    # Анализ времени между улучшениями
    pace_fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Время между улучшениями (часы)",
            "Количество улучшений в день"
        ),
        vertical_spacing=0.15
    )
    
    # Собираем данные о времени между улучшениями
    upgrades_timeline = extract_upgrades_timeline(history)
    intervals = calculate_intervals(upgrades_timeline)
    
    # Статистика интервалов
    avg_interval = np.mean(intervals) if intervals else 0
    median_interval = np.median(intervals) if intervals else 0
    max_interval = np.max(intervals) if intervals else 0
    
    # График времени между улучшениями
    pace_fig.add_trace(
        go.Scatter(
            x=list(range(len(intervals))),
            y=intervals,
            mode="lines+markers",
            name="Интервал",
            line=dict(color="royalblue"),
            hovertemplate="Улучшение %{x}<br>Интервал: %{y:.2f} ч"
        ),
        row=1, col=1
    )
    
    # Добавляем средний интервал
    pace_fig.add_trace(
        go.Scatter(
            x=[0, len(intervals)-1],
            y=[avg_interval, avg_interval],
            mode="lines",
            name="Средний интервал",
            line=dict(color="red", dash="dash"),
            hovertemplate="Средний интервал: %{y:.2f} ч"
        ),
        row=1, col=1
    )
    
    # Количество улучшений в день
    upgrades_per_day = calculate_upgrades_per_day(upgrades_timeline)
    days = sorted(upgrades_per_day.keys())
    counts = [upgrades_per_day[day] for day in days]
    
    pace_fig.add_trace(
        go.Bar(
            x=days,
            y=counts,
            name="Улучшений в день",
            marker_color="green",
            hovertemplate="День %{x}<br>Улучшений: %{y}"
        ),
        row=2, col=1
    )
    
    # Средние улучшения в день
    avg_upgrades = np.mean(counts) if counts else 0
    pace_fig.add_trace(
        go.Scatter(
            x=[min(days), max(days)] if days else [0, 0],
            y=[avg_upgrades, avg_upgrades],
            mode="lines",
            name="Среднее количество",
            line=dict(color="red", dash="dash"),
            hovertemplate="Среднее: %{y:.2f}"
        ),
        row=2, col=1
    )
    
    pace_fig.update_layout(
        height=600,
        hovermode="x unified"
    )
    
    # Анализ периодов стагнации
    stagnation_fig = go.Figure()
    
    # Находим периоды стагнации
    stagnation_periods = calculate_stagnation_periods(upgrades_timeline)
    
    if stagnation_periods:
        # Сортируем по длительности
        stagnation_periods.sort(key=lambda x: x["duration"], reverse=True)
        
        # Добавляем столбцы
        days = [period["start_day"] for period in stagnation_periods]
        durations = [period["duration_days"] for period in stagnation_periods]
        
        stagnation_fig.add_trace(
            go.Bar(
                x=days,
                y=durations,
                name="Длительность",
                marker_color="indianred",
                hovertemplate="Начало: День %{x:.1f}<br>Длительность: %{y:.1f} дней"
            )
        )
        
        # Добавляем границу для значимых периодов стагнации (> 1 дня)
        stagnation_fig.add_trace(
            go.Scatter(
                x=[min(days), max(days)],
                y=[1, 1],
                mode="lines",
                name="Граница (1 день)",
                line=dict(color="black", dash="dash")
            )
        )
        
        stagnation_fig.update_layout(
            title="Периоды стагнации",
            xaxis_title="День начала",
            yaxis_title="Длительность (дни)",
            hovermode="x unified"
        )
    else:
        stagnation_fig.add_trace(
            go.Scatter(
                x=[0],
                y=[0],
                mode="markers",
                marker=dict(opacity=0),
                hoverinfo="none"
            )
        )
        stagnation_fig.update_layout(
            title="Нет периодов стагнации",
            xaxis_title="День",
            yaxis_title="Длительность (дни)"
        )
    
    # Статистика прогресса
    days_with_upgrades = len(set(int(upgrade["day"]) for upgrade in upgrades_timeline))
    total_days = int(history[-1]["timestamp"] // 86400)
    efficiency = days_with_upgrades / total_days * 100 if total_days > 0 else 0
    
    stats = html.Div([
        html.Div([
            html.H4("Статистика прогресса:"),
            html.Ul([
                html.Li(f"Среднее время между улучшениями: {avg_interval:.2f} часов"),
                html.Li(f"Медианное время между улучшениями: {median_interval:.2f} часов"),
                html.Li(f"Максимальное время между улучшениями: {max_interval:.2f} часов"),
                html.Li(f"Среднее количество улучшений в день: {avg_upgrades:.2f}"),
                html.Li(f"Дней с улучшениями: {days_with_upgrades} из {total_days} ({efficiency:.1f}%)"),
                html.Li(f"Количество периодов стагнации (>1 дня): {len([p for p in stagnation_periods if p['duration_days'] > 1])}"),
            ])
        ])
    ])
    
    return pace_fig, stagnation_fig, stats


@app.callback(
    Output("user-level-progress", "figure"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_user_level_progress(data):
    """
    Обновляет график прогресса уровня пользователя.
    
    Args:
        data: Данные симуляции
        
    Returns:
        go.Figure: График прогресса уровня
    """
    if data is None or "history" not in data:
        return {}
    
    history = data["history"]
    if not history:
        return {}
    
    # Извлекаем данные об уровне
    level_data = extract_level_data(history)
    
    # Создаем график
    fig = create_subplot_figure(
        rows=2, cols=1,
        subplot_titles=("Уровень персонажа", "Опыт персонажа"),
        vertical_spacing=0.3
    )
    
    # Добавляем график уровня
    days = [entry["day"] for entry in level_data]
    levels = [entry["level"] for entry in level_data]
    
    add_time_series(
        fig, 
        x=days, 
        y=levels, 
        name="Уровень", 
        color=PLOT_COLORS["level"],
        mode="lines+markers",
        row=1, col=1
    )
    
    # Добавляем график опыта
    xp = [entry["xp"] for entry in level_data]
    
    add_time_series(
        fig, 
        x=days, 
        y=xp, 
        name="Опыт", 
        color=PLOT_COLORS["xp"],
        row=2, col=1
    )
    
    # Настраиваем оси
    fig.update_yaxes(title="Уровень", row=1, col=1)
    fig.update_xaxes(title="День", row=1, col=1)
    
    fig.update_yaxes(title="Опыт", row=2, col=1)
    fig.update_xaxes(title="День", row=2, col=1)
    
    return fig


@app.callback(
    Output("resources-over-time", "figure"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_resources_over_time(data):
    """
    Обновляет график ресурсов во времени.
    
    Args:
        data: Данные симуляции
        
    Returns:
        go.Figure: График ресурсов
    """
    if data is None or "history" not in data:
        return {}
    
    history = data["history"]
    if not history:
        return {}
    
    # Извлекаем данные о ресурсах
    resource_data = extract_resource_data(history)
    
    # Создаем график
    fig = create_subplot_figure(
        rows=3, cols=1,
        subplot_titles=("Золото", "Ключи", "Заработок (gold/sec)"),
        row_heights=[0.33, 0.33, 0.33],
        vertical_spacing=0.15
    )
    
    # Добавляем график золота
    days = [r["day"] for r in resource_data]
    gold = [r["gold"] for r in resource_data]
    keys = [r["keys"] for r in resource_data]
    earn_per_sec = [r["earn_per_sec"] for r in resource_data]
    
    add_time_series(
        fig, 
        x=days, 
        y=gold, 
        name="Золото", 
        color=PLOT_COLORS["gold"],
        row=1, col=1
    )
    
    add_time_series(
        fig, 
        x=days, 
        y=keys, 
        name="Ключи", 
        color=PLOT_COLORS["keys"],
        row=2, col=1
    )
    
    add_time_series(
        fig, 
        x=days, 
        y=earn_per_sec, 
        name="Gold/sec", 
        color=PLOT_COLORS["income"],
        row=3, col=1
    )
    
    # Настраиваем оси
    for row in range(1, 4):
        fig.update_xaxes(title="День", row=row, col=1)
    
    fig.update_yaxes(title="Золото", row=1, col=1)
    fig.update_yaxes(title="Ключи", row=2, col=1)
    fig.update_yaxes(title="Gold/sec", row=3, col=1)
    
    return fig


@app.callback(
    Output("coins-per-level-table", "children"),
    Input("user-levels-store", "data"),
    prevent_initial_call=True
)
def update_coins_per_level_table(user_levels_data):
    """
    Обновляет таблицу gold/sec по уровням.
    
    Args:
        user_levels_data: Данные об уровнях пользователя
        
    Returns:
        html.Table: Таблица с gold/sec
    """
    if not user_levels_data:
        return "Нет данных"
    
    # Создаем таблицу
    header = html.Tr([
        html.Th("Уровень"),
        html.Th("XP требуется"),
        html.Th("Gold/sec"),
        html.Th("Награда ключей"),
        html.Th("Gold/час"),
        html.Th("Gold/день")
    ])
    
    rows = []
    prev_gold_per_sec = None
    
    for level, level_data in sorted(user_levels_data.items(), key=lambda x: int(x[0])):
        gold_per_sec = level_data["gold_per_sec"]
        xp_required = level_data["xp_required"]
        keys_reward = level_data["keys_reward"]
        
        growth = ""
        if prev_gold_per_sec is not None:
            growth_pct = (gold_per_sec / prev_gold_per_sec - 1) * 100
            growth = f" (+{growth_pct:.1f}%)"
        
        gold_per_hour = gold_per_sec * 3600
        gold_per_day = gold_per_sec * 86400
        
        row = html.Tr([
            html.Td(f"{level}"),
            html.Td(f"{xp_required:,}"),
            html.Td(f"{gold_per_sec:.4f}{growth}"),
            html.Td(f"{keys_reward}"),
            html.Td(f"{gold_per_hour:.2f}"),
            html.Td(f"{gold_per_day:.2f}")
        ])
        
        rows.append(row)
        prev_gold_per_sec = gold_per_sec
    
    return html.Table([
        html.Thead(header),
        html.Tbody(rows)
    ], style={"borderCollapse": "collapse", "width": "100%"})


@app.callback(
    [Output("daily-events-table", "data"),
     Output("daily-events-table", "columns")],
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_daily_events_table(data):
    """
    Обновляет таблицу с ежедневными событиями игры.
    
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
    
    # Получаем данные о событиях по дням
    daily_events = extract_daily_events_data(history)
    
    if not daily_events:
        return [], []
    
    # Форматируем данные для таблицы
    table_data = []
    
    for event in daily_events:
        # Форматируем диапазон уровней
        level_range = event["level_range"]
        if level_range[0] == 0 and level_range[1] == 0:
            level_range_str = "-"
        else:
            level_range_str = f"{level_range[0]} → {level_range[1]}"
        
        # Добавляем строку в таблицу
        table_data.append({
            "День": event["day"],
            "Входы в игру": event["sessions_count"],
            "Время в игре (мин)": round(event["session_minutes"], 1),
            "Повышения уровня": event["level_ups"],
            "Диапазон уровня": level_range_str,
            "Улучшения локаций": event["upgrades_count"],
            "Новые локации": event["new_locations"],
            "Золото": f"{event['gold']:,.0f}",
            "XP": f"{event['xp']:,.0f}",
            "Ключи": event["keys"]
        })
    
    # Определяем колонки
    columns = [
        {"name": "День", "id": "День", "type": "numeric"},
        {"name": "Входы в игру", "id": "Входы в игру", "type": "numeric"},
        {"name": "Время в игре (мин)", "id": "Время в игре (мин)", "type": "numeric"},
        {"name": "Повышения уровня", "id": "Повышения уровня", "type": "numeric"},
        {"name": "Диапазон уровня", "id": "Диапазон уровня"},
        {"name": "Улучшения локаций", "id": "Улучшения локаций", "type": "numeric"},
        {"name": "Новые локации", "id": "Новые локации", "type": "numeric"},
        {"name": "Золото", "id": "Золото"},
        {"name": "XP", "id": "XP"},
        {"name": "Ключи", "id": "Ключи", "type": "numeric"}
    ]
    
    return table_data, columns 