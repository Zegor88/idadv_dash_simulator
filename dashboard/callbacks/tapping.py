"""
Коллбеки для анализа тапания.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Input, Output, State, callback, html, dcc
from typing import Dict, List, Any, Tuple, Optional

from idadv_dash_simulator.models.config import TappingConfig
from idadv_dash_simulator.workflow.tapping import TappingEngine, TapDay, TapSession
from idadv_dash_simulator.config.dashboard_config import TAPPING_COLORS, TAPPING_GRAPH_LAYOUT
from idadv_dash_simulator.dashboard import app

@app.callback(
    [Output("tapping-stats-store", "data")],
    [Input("simulation-data-store", "data"),
     Input("auto-run-store", "data")],
    [State("is-tapping-checkbox", "value"),
     State("max-energy-input", "value"),
     State("tap-speed-input", "value"),
     State("gold-per-tap-input", "value"),
     State("game-duration-input", "value")],
    prevent_initial_call=True
)
def calculate_tapping_stats(sim_data, auto_run_data, is_tapping, max_energy, tap_speed, gold_per_tap, game_duration):
    """
    Расчет статистики тапания на основе данных симуляции.
    
    Args:
        sim_data: Данные симуляции
        auto_run_data: Данные о состоянии автозапуска
        is_tapping: Флаг активности тапания
        max_energy: Максимальный запас энергии
        tap_speed: Скорость тапания (тапов в секунду)
        gold_per_tap: Золото за 1 тап
        game_duration: Длительность игровой сессии в минутах
        
    Returns:
        dict: Данные статистики тапания
    """
    # Проверка на наличие данных симуляции
    if not auto_run_data or not auto_run_data.get("auto_run") or not sim_data or "history" not in sim_data:
        return [{}]
    
    # Получаем историю симуляции
    history = sim_data.get("history", [])
    if not history:
        return [{}]
    
    # Проверка активации тапания
    is_tapping_active = 'is_tapping' in (is_tapping or [])
    
    # Создаем конфигурацию тапания
    tapping_config = TappingConfig(
        is_tapping=is_tapping_active,
        max_energy_capacity=max_energy,
        tap_speed=tap_speed,
        gold_per_tap=gold_per_tap
    )
    
    # Если тапание отключено, возвращаем пустые данные
    if not is_tapping_active:
        return [{"is_tapping": False, "days": [], "stats": {}}]
    
    # Извлекаем времена сессий из истории
    session_times = []
    
    for state in history:
        if "timestamp" in state:
            session_times.append(state["timestamp"])
    
    # Создаем движок тапания и запускаем симуляцию
    tapping_engine = TappingEngine(tapping_config)
    days_data = tapping_engine.simulate_sessions(session_times, game_duration)
    
    # Преобразуем данные дней в формат для хранилища
    days_json = []
    for day in days_data:
        day_dict = {
            "day": day.day,
            "total_taps": day.total_taps,
            "total_energy": day.total_energy,
            "total_gold": day.total_gold,
            "sessions": []
        }
        
        for session in day.sessions:
            session_dict = {
                "start_time": session.start_time,
                "duration": session.duration,
                "energy_used": session.energy_used,
                "taps_count": session.taps_count,
                "gold_earned": session.gold_earned,
                "energy_history": session.energy_history
            }
            day_dict["sessions"].append(session_dict)
            
        days_json.append(day_dict)
    
    # Рассчитываем суммарную статистику
    total_taps = sum(day.total_taps for day in days_data)
    total_gold = sum(day.total_gold for day in days_data)
    total_energy = sum(day.total_energy for day in days_data)
    total_sessions = sum(len(day.sessions) for day in days_data)
    avg_taps_per_session = total_taps / total_sessions if total_sessions > 0 else 0
    
    # Формируем результат
    result = {
        "is_tapping": True,
        "days": days_json,
        "stats": {
            "total_taps": total_taps,
            "total_gold": total_gold,
            "total_energy": total_energy,
            "total_sessions": total_sessions,
            "avg_taps_per_session": avg_taps_per_session
        },
        "config": {
            "max_energy_capacity": max_energy,
            "tap_speed": tap_speed,
            "gold_per_tap": gold_per_tap
        }
    }
    
    return [result]

@app.callback(
    [Output("taps-gold-by-day-graph", "figure"),
     Output("total-taps", "children"),
     Output("total-gold-from-taps", "children"),
     Output("avg-taps-per-session", "children")],
    [Input("tapping-stats-store", "data")],
    prevent_initial_call=True
)
def update_taps_gold_by_day(tapping_data):
    """
    Обновляет график тапов и золота по дням.
    
    Args:
        tapping_data: Данные о тапании
        
    Returns:
        go.Figure: График тапов и золота по дням
        str: Общее количество тапов
        str: Общее количество золота от тапов
        str: Среднее количество тапов за сессию
    """
    # Проверка на наличие данных о тапании
    if not tapping_data or not tapping_data.get("is_tapping", False):
        empty_figure = go.Figure()
        empty_figure.update_layout(
            title="Необходимо включить тапание в настройках",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "Нет данных. Активируйте функцию тапания в настройках и запустите симуляцию.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16}
            }]
        )
        return empty_figure, "Н/Д", "Н/Д", "Н/Д"
    
    # Получаем данные дней
    days = tapping_data.get("days", [])
    if not days:
        empty_figure = go.Figure()
        empty_figure.update_layout(
            title="Нет данных о тапании",
            xaxis={"visible": False},
            yaxis={"visible": False}
        )
        return empty_figure, "0", "0", "0"
    
    # Статистика
    stats = tapping_data.get("stats", {})
    total_taps = stats.get("total_taps", 0)
    total_gold = stats.get("total_gold", 0)
    avg_taps_per_session = stats.get("avg_taps_per_session", 0)
    
    # Подготавливаем данные для графика
    days_numbers = [day["day"] + 1 for day in days]  # +1 для отображения с дня 1
    taps_counts = [day["total_taps"] for day in days]
    gold_earned = [day["total_gold"] for day in days]
    
    # Создаем график с двумя осями Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Добавляем линию тапов
    fig.add_trace(
        go.Bar(
            x=days_numbers,
            y=taps_counts,
            name="Количество тапов",
            marker_color=TAPPING_COLORS["taps"]
        ),
        secondary_y=False
    )
    
    # Добавляем линию золота
    fig.add_trace(
        go.Scatter(
            x=days_numbers,
            y=gold_earned,
            name="Полученное золото",
            marker_color=TAPPING_COLORS["gold"],
            mode="lines+markers"
        ),
        secondary_y=True
    )
    
    # Обновляем макет
    fig.update_layout(
        title="Тапы и золото по дням",
        xaxis_title="День",
        **TAPPING_GRAPH_LAYOUT
    )
    
    # Настраиваем оси Y
    fig.update_yaxes(title_text="Количество тапов", secondary_y=False)
    fig.update_yaxes(title_text="Полученное золото", secondary_y=True)
    
    # Форматируем метрики
    formatted_total_taps = f"{total_taps:,.0f}".replace(",", " ")
    formatted_total_gold = f"{total_gold:,.0f}".replace(",", " ")
    formatted_avg_taps = f"{avg_taps_per_session:,.1f}".replace(",", " ")
    
    return fig, formatted_total_taps, formatted_total_gold, formatted_avg_taps

@app.callback(
    [Output("session-select-dropdown", "options"),
     Output("session-select-dropdown", "value")],
    [Input("tapping-stats-store", "data")],
    prevent_initial_call=True
)
def update_session_dropdown(tapping_data):
    """
    Обновляет выпадающий список сессий для анализа энергии.
    
    Args:
        tapping_data: Данные о тапании
        
    Returns:
        list: Список опций для выпадающего списка
        str: Значение выбранной опции по умолчанию
    """
    # Проверка на наличие данных о тапании
    if not tapping_data or not tapping_data.get("is_tapping", False):
        return [], None
    
    # Получаем данные дней
    days = tapping_data.get("days", [])
    if not days:
        return [], None
    
    # Создаем список опций для выпадающего списка
    options = []
    for day_idx, day in enumerate(days):
        day_num = day["day"] + 1  # +1 для отображения с дня 1
        
        for session_idx, session in enumerate(day.get("sessions", [])):
            # Форматируем время начала сессии
            start_time_hours = (session["start_time"] % 86400) // 3600
            start_time_minutes = ((session["start_time"] % 86400) % 3600) // 60
            start_time_str = f"{start_time_hours:02d}:{start_time_minutes:02d}"
            
            label = f"День {day_num}, сессия {session_idx + 1} ({start_time_str})"
            value = f"{day_idx}_{session_idx}"
            
            options.append({"label": label, "value": value})
    
    # Выбираем первую сессию по умолчанию, если она есть
    default_value = options[0]["value"] if options else None
    
    return options, default_value

@app.callback(
    Output("energy-over-time-graph", "figure"),
    [Input("session-select-dropdown", "value"),
     Input("tapping-stats-store", "data")],
    prevent_initial_call=True
)
def update_energy_over_time(selected_session, tapping_data):
    """
    Обновляет график энергии по времени для выбранной сессии.
    
    Args:
        selected_session: Выбранная сессия в формате "{day_idx}_{session_idx}"
        tapping_data: Данные о тапании
        
    Returns:
        go.Figure: График энергии по времени
    """
    # Проверка на наличие данных о тапании
    if not tapping_data or not tapping_data.get("is_tapping", False) or not selected_session:
        empty_figure = go.Figure()
        empty_figure.update_layout(
            title="Выберите сессию для анализа",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "Нет данных. Выберите сессию для анализа.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16}
            }]
        )
        return empty_figure
    
    # Парсим индексы дня и сессии
    day_idx, session_idx = map(int, selected_session.split("_"))
    
    # Получаем данные дней
    days = tapping_data.get("days", [])
    if not days or day_idx >= len(days):
        return go.Figure()
    
    # Получаем данные сессии
    sessions = days[day_idx].get("sessions", [])
    if not sessions or session_idx >= len(sessions):
        return go.Figure()
    
    session = sessions[session_idx]
    
    # Получаем историю энергии
    energy_history = session.get("energy_history", [])
    if not energy_history:
        return go.Figure()
    
    # Преобразуем историю в относительное время (от начала сессии)
    start_time = session["start_time"]
    times = [(t - start_time) / 60 for t, _ in energy_history]  # Переводим в минуты
    energy_values = [e for _, e in energy_history]
    
    # Создаем график с двумя осями Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Добавляем линию энергии (основная ось Y)
    fig.add_trace(
        go.Scatter(
            x=times,
            y=energy_values,
            name="Энергия",
            line={"color": TAPPING_COLORS["energy"], "width": 2},
            mode="lines"
        ),
        secondary_y=False
    )
    
    # Добавляем область под кривой энергии
    fig.add_trace(
        go.Scatter(
            x=times,
            y=energy_values,
            name="Энергия (область)",
            fill="tozeroy",
            fillcolor=f"rgba(76, 175, 80, 0.2)",
            line={"width": 0},
            showlegend=False
        ),
        secondary_y=False
    )
    
    # Рассчитываем количество тапов для каждого момента времени
    # На самом деле мы не знаем точное количество тапов в каждый момент,
    # но можем оценить его по изменению энергии
    tap_values = []
    cumulative_taps = 0
    prev_energy = energy_values[0] if energy_values else 0
    
    for i, energy in enumerate(energy_values):
        if i == 0:
            tap_values.append(0)
        else:
            # Оцениваем количество тапов как уменьшение энергии плюс восстановление (0.1 энергии/сек)
            # Это приблизительная оценка
            energy_change = prev_energy - energy
            recovery = 0.1  # предполагаемое восстановление энергии за секунду
            
            # Если энергия уменьшилась, значит были тапы
            taps = max(0, energy_change + recovery)
            cumulative_taps += taps
            tap_values.append(cumulative_taps)
        
        prev_energy = energy
    
    # Добавляем линию тапов (вторичная ось Y)
    fig.add_trace(
        go.Scatter(
            x=times,
            y=tap_values,
            name="Количество тапов",
            line={"color": TAPPING_COLORS["taps"], "width": 1.5, "dash": "dot"},
            mode="lines"
        ),
        secondary_y=True
    )
    
    # Добавляем максимальный уровень энергии
    max_energy = tapping_data.get("config", {}).get("max_energy_capacity", 700)
    fig.add_shape(
        type="line",
        x0=min(times),
        y0=max_energy,
        x1=max(times),
        y1=max_energy,
        line=dict(
            color="rgba(255, 0, 0, 0.4)",
            width=1,
            dash="dash",
        )
    )
    
    # Добавляем аннотацию для максимального уровня
    fig.add_annotation(
        x=min(times),
        y=max_energy,
        text="Макс. энергия",
        showarrow=False,
        yshift=10,
        font=dict(size=10, color="red")
    )
    
    # Статистика сессии
    taps_count = session.get("taps_count", 0)
    energy_used = session.get("energy_used", 0)
    gold_earned = session.get("gold_earned", 0)
    duration_min = session.get("duration", 0) / 60  # Переводим в минуты
    
    # Добавляем аннотацию с информацией о сессии
    fig.add_annotation(
        x=0.5,
        y=1.1,
        text=f"Тапов: {taps_count:.0f} | Энергии: {energy_used:.0f} | Золота: {gold_earned:.0f} | Длительность: {duration_min:.1f} мин",
        showarrow=False,
        xref="paper",
        yref="paper",
        font=dict(size=12)
    )
    
    # Обновляем макет
    fig.update_layout(
        title="Изменение энергии и тапов во время сессии",
        xaxis_title="Время (минуты от начала сессии)",
        **TAPPING_GRAPH_LAYOUT
    )
    
    # Настраиваем оси Y
    fig.update_yaxes(title_text="Энергия", secondary_y=False)
    fig.update_yaxes(title_text="Количество тапов", secondary_y=True)
    
    # Переопределяем параметры легенды
    fig.update_layout(
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1}
    )
    
    return fig

@app.callback(
    Output("tapping-stats-table", "data"),
    [Input("tapping-stats-store", "data")],
    prevent_initial_call=True
)
def update_tapping_stats_table(tapping_data):
    """
    Обновляет таблицу статистики тапания по дням.
    
    Args:
        tapping_data: Данные о тапании
        
    Returns:
        list: Данные для таблицы
    """
    # Проверка на наличие данных о тапании
    if not tapping_data or not tapping_data.get("is_tapping", False):
        return []
    
    # Получаем данные дней
    days = tapping_data.get("days", [])
    if not days:
        return []
    
    # Создаем данные для таблицы
    table_data = []
    for day in days:
        day_num = day["day"] + 1  # +1 для отображения с дня 1
        total_taps = day["total_taps"]
        total_energy = day["total_energy"]
        total_gold = day["total_gold"]
        
        # Форматируем числа
        table_data.append({
            "day": f"День {day_num}",
            "taps": f"{total_taps:,.0f}".replace(",", " "),
            "energy": f"{total_energy:,.0f}".replace(",", " "),
            "gold": f"{total_gold:,.0f}".replace(",", " ")
        })
    
    return table_data 