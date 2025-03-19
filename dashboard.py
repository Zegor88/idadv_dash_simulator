import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
from typing import Dict, List, Tuple
from plotly.subplots import make_subplots

from idadv_dash_simulator.simulator import Simulator
from idadv_dash_simulator.sample_config import create_sample_config
from idadv_dash_simulator.models.config import SimulationConfig

# Инициализация приложения Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Определение макета приложения
app.layout = html.Div([
    html.H1("Анализ игровой механики Indonesian Adventure"),
    
    html.Div([
        html.Div([
            html.H3("Настройки симуляции"),
            html.Button("Запустить симуляцию", id="run-simulation-button", className="button"),
            html.Div(id="simulation-status"),
            
            html.Hr(),
            
            html.H4("Параметры проверок"),
            html.Div([
                html.Label("Частота проверок в день:"),
                html.Span("?", id="checks-tooltip", style={
                    "marginLeft": "10px",
                    "cursor": "pointer",
                    "backgroundColor": "#f0f0f0",
                    "padding": "2px 8px",
                    "borderRadius": "50%"
                }),
                dcc.Tooltip(
                    id="checks-tooltip-content",
                    children=["Количество раз в день, когда игрок проверяет игру и собирает накопленные ресурсы. Влияет на эффективность прогресса."],
                    style={"maxWidth": "300px", "fontSize": "14px"}
                ),
            ], style={"display": "flex", "alignItems": "center"}),
            dcc.Slider(
                id="checks-per-day-slider",
                min=1,
                max=8,
                step=1,
                value=5,
                marks={i: str(i) for i in range(1, 9)},
            ),
            
            html.Hr(),
            
            html.H4("Параметры локаций"),
            html.Label("Кулдаун между улучшениями (множитель):"),
            dcc.Slider(
                id="cooldown-multiplier-slider",
                min=0.5,
                max=2.0,
                step=0.1,
                value=1.0,
                marks={i/10: str(i/10) for i in range(5, 21, 5)},
            ),
        ], className="settings-panel", style={"width": "30%", "padding": "20px", "backgroundColor": "#f5f5f5"}),
        
        html.Div([
            html.H3("Результаты симуляции"),
            html.Div(id="simulation-results-container"),
            
            dcc.Tabs([
                dcc.Tab(label="Общая информация", children=[
                    html.Div([
                        html.Div([
                            html.H4("Основные показатели"),
                            html.Div(id="completion-time"),
                            html.Div(id="final-resources"),
                        ], style={"marginBottom": "20px"}),
                        
                        html.Div([
                            html.H4("Ключевые метрики"),
                            html.Div(id="key-metrics", style={
                                "display": "grid",
                                "gridTemplateColumns": "repeat(3, 1fr)",
                                "gap": "20px",
                                "padding": "20px",
                                "backgroundColor": "#f8f9fa",
                                "borderRadius": "8px"
                            }),
                        ]),
                    ]),
                ]),
                dcc.Tab(label="Прогресс персонажа", children=[
                    html.Div([
                        dcc.Graph(id="user-level-progress"),
                        dcc.Graph(id="resources-over-time"),
                        html.Div([
                            html.H4("Детальная информация о прогрессе"),
                            dash_table.DataTable(
                                id="progress-details-table",
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'textAlign': 'center',
                                    'padding': '10px',
                                },
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'border': '1px solid black'
                                },
                                style_data={
                                    'border': '1px solid grey'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    }
                                ]
                            )
                        ], style={"marginTop": "20px"})
                    ]),
                ]),
                dcc.Tab(label="Анализ локаций", children=[
                    html.Div([
                        dcc.Graph(id="locations-upgrades"),
                        html.Div([
                            html.H4("Временная шкала улучшений"),
                            dash_table.DataTable(
                                id="upgrades-timeline-table",
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'textAlign': 'center',
                                    'padding': '10px',
                                },
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'border': '1px solid black'
                                },
                                style_data={
                                    'border': '1px solid grey'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    }
                                ]
                            )
                        ], style={"marginTop": "20px"})
                    ]),
                ]),
                dcc.Tab(label="Экономический баланс", children=[
                    html.Div([
                        html.H4("Анализ доходов и расходов"),
                        dcc.Graph(id="economy-analysis"),
                        
                        html.Div([
                            html.H4("Эффективность улучшений (ROI)"),
                            html.P([
                                "ROI (Return on Investment) - показатель возврата инвестиций. ",
                                "Рассчитывается как отношение полученной награды (опыт + ключи * 100) к стоимости улучшения. ",
                                "Чем выше ROI, тем выгоднее улучшение."
                            ], style={"fontSize": "14px", "color": "#666", "marginBottom": "20px"}),
                            dcc.Graph(id="upgrades-efficiency"),
                        ]),
                        
                        html.H4("Скорость накопления монет по уровням"),
                        html.Div(id="coins-per-level-table"),
                    ]),
                ]),
                dcc.Tab(label="Темп игры", children=[
                    html.Div([
                        html.H4("Анализ времени между улучшениями"),
                        dcc.Graph(id="progression-pace"),
                        
                        html.H4("Анализ периодов без улучшений"),
                        dcc.Graph(id="stagnation-analysis"),
                        
                        html.H4("Статистика прогресса"),
                        html.Div(id="progression-stats"),
                    ]),
                ]),
            ]),
        ], className="results-panel", style={"width": "70%", "padding": "20px"}),
    ], style={"display": "flex", "flexDirection": "row"}),
    
    dcc.Store(id="simulation-data-store"),
    dcc.Store(id="user-levels-store"),
])

# Обновляем коллбек для запуска симуляции (убираем user_level)
@app.callback(
    [Output("simulation-status", "children"),
     Output("simulation-data-store", "data"),
     Output("user-levels-store", "data")],
    [Input("run-simulation-button", "n_clicks")],
    [State("cooldown-multiplier-slider", "value"),
     State("checks-per-day-slider", "value")],
    prevent_initial_call=True
)
def run_simulation(n_clicks, cooldown_multiplier, checks_per_day):
    if n_clicks is None:
        return "Симуляция не запущена", None, None
    
    config = create_sample_config()
    
    user_levels_data = {
        level: {
            "xp_required": level_config.xp_required,
            "gold_per_sec": level_config.gold_per_sec,
            "keys_reward": level_config.keys_reward
        } for level, level_config in config.user_levels.items()
    }
    
    # Применяем множитель кулдауна
    for level in config.location_cooldowns:
        config.location_cooldowns[level] = int(config.location_cooldowns[level] * cooldown_multiplier)
    
    # Настраиваем частоту проверок
    active_seconds = 16 * 3600
    check_interval = active_seconds // checks_per_day
    
    config.check_schedule = [
        (8 * 3600) + (i * check_interval)
        for i in range(checks_per_day)
    ]
    
    simulator = Simulator(config)
    result = simulator.run_simulation()
    
    simulation_data = {
        "completion_time": result.timestamp,
        "final_balance": {
            "gold": simulator.workflow.balance.gold,
            "xp": simulator.workflow.balance.xp,
            "keys": simulator.workflow.balance.keys,
            "user_level": simulator.workflow.balance.user_level,
            "earn_per_sec": simulator.workflow.balance.earn_per_sec
        },
        "config": {
            "cooldown_multiplier": cooldown_multiplier,
            "checks_per_day": checks_per_day
        },
        "history": result.history
    }
    
    return f"Симуляция завершена за {result.timestamp} секунд (≈ {result.timestamp // 86400} дней)", simulation_data, user_levels_data

# Обновляем отображение ключевых метрик
@app.callback(
    Output("key-metrics", "children"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_key_metrics(data):
    if data is None:
        return "Нет данных"
    
    history = data.get("history", [])
    if not history:
        return "Нет данных"
    
    # Подсчитываем метрики
    total_upgrades = sum(
        1 for state in history
        for action in state["actions"]
        if action["type"] == "location_upgrade"
    )
    
    total_gold_spent = sum(
        action["cost"]
        for state in history
        for action in state["actions"]
        if action["type"] == "location_upgrade"
    )
    
    avg_gold_per_day = total_gold_spent / (data["completion_time"] / 86400)
    
    metrics = [
        html.Div([
            html.H5("Всего улучшений"),
            html.P(f"{total_upgrades}", style={"fontSize": "24px", "fontWeight": "bold"}),
        ], style={"textAlign": "center"}),
        
        html.Div([
            html.H5("Потрачено золота"),
            html.P(f"{total_gold_spent:,.0f}", style={"fontSize": "24px", "fontWeight": "bold"}),
        ], style={"textAlign": "center"}),
        
        html.Div([
            html.H5("Среднее в день"),
            html.P(f"{avg_gold_per_day:,.0f}", style={"fontSize": "24px", "fontWeight": "bold"}),
        ], style={"textAlign": "center"}),
    ]
    
    return metrics

# Обновляем таблицу с деталями прогресса
@app.callback(
    Output("progress-details-table", "data"),
    Output("progress-details-table", "columns"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_progress_details(data):
    if data is None or "history" not in data:
        return [], []
    
    history = data["history"]
    if not history:
        return [], []
    
    # Создаем данные для таблицы
    table_data = []
    for state in history:
        level_ups = [action for action in state["actions"] if action["type"] == "level_up"]
        if level_ups:
            for action in level_ups:
                table_data.append({
                    "День": f"{action['timestamp'] / 86400:.1f}",
                    "Новый уровень": action["new_level"],
                    "Накоплено XP": state["balance"]["xp"],
                    "Золота в час": state["balance"]["earn_per_sec"] * 3600,
                    "Золота в день": state["balance"]["earn_per_sec"] * 86400,
                })
    
    columns = [
        {"name": "День", "id": "День"},
        {"name": "Новый уровень", "id": "Новый уровень"},
        {"name": "Накоплено XP", "id": "Накоплено XP"},
        {"name": "Золота в час", "id": "Золота в час", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Золота в день", "id": "Золота в день", "type": "numeric", "format": {"specifier": ",.0f"}},
    ]
    
    return table_data, columns

# Обновляем таблицу временной шкалы улучшений
@app.callback(
    Output("upgrades-timeline-table", "data"),
    Output("upgrades-timeline-table", "columns"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_upgrades_timeline(data):
    if data is None or "history" not in data:
        return [], []
    
    history = data["history"]
    if not history:
        return [], []
    
    # Создаем данные для таблицы
    table_data = []
    for state in history:
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                # Находим баланс до улучшения
                gold_before = state["balance"]["gold"] + action["cost"]  # Добавляем стоимость, так как она уже вычтена
                gold_after = state["balance"]["gold"]
                
                table_data.append({
                    "День": f"{action['timestamp'] / 86400:.1f}",
                    "Локация": action["location_id"],
                    "Новый уровень": action["new_level"],
                    "Золото до улучшения": gold_before,
                    "Стоимость": action["cost"],
                    "Золото после улучшения": gold_after,
                    "Награда XP": action["reward_xp"],
                    "Награда ключи": action["reward_keys"],
                })
    
    # Сортируем по времени
    table_data.sort(key=lambda x: float(x["День"]))
    
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

# Обновляем анализ темпа игры
@app.callback(
    [Output("progression-pace", "figure"),
     Output("stagnation-analysis", "figure"),
     Output("progression-stats", "children")],
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_progression_analysis(data):
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
    upgrades_timeline = []
    for state in history:
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                upgrades_timeline.append({
                    "timestamp": action["timestamp"],
                    "location_id": action["location_id"],
                    "level": action["new_level"]
                })
    
    # Сортируем по времени
    upgrades_timeline.sort(key=lambda x: x["timestamp"])
    
    # Рассчитываем интервалы между улучшениями
    intervals = []
    for i in range(1, len(upgrades_timeline)):
        interval = (upgrades_timeline[i]["timestamp"] - upgrades_timeline[i-1]["timestamp"]) / 3600  # в часах
        intervals.append(interval)
    
    if intervals:
        pace_fig.add_trace(
            go.Scatter(
                x=list(range(len(intervals))),
                y=intervals,
                mode="lines+markers",
                name="Интервал (часы)",
                hovertemplate="Улучшение №%{x}<br>Интервал: %{y:.1f} часов"
            ),
            row=1, col=1
        )
    
    # Гистограмма улучшений по дням
    upgrades_per_day = {}
    for upgrade in upgrades_timeline:
        day = upgrade["timestamp"] // 86400
        upgrades_per_day[day] = upgrades_per_day.get(day, 0) + 1
    
    if upgrades_per_day:
        pace_fig.add_trace(
            go.Bar(
                x=list(upgrades_per_day.keys()),
                y=list(upgrades_per_day.values()),
                name="Улучшений",
                hovertemplate="День %{x}<br>Улучшений: %{y}"
            ),
            row=2, col=1
        )
    
    pace_fig.update_layout(
        height=600,
        title="Анализ темпа улучшений",
        showlegend=True
    )
    
    pace_fig.update_xaxes(title_text="Номер улучшения", row=1, col=1)
    pace_fig.update_xaxes(title_text="День симуляции", row=2, col=1)
    pace_fig.update_yaxes(title_text="Интервал (часы)", row=1, col=1)
    pace_fig.update_yaxes(title_text="Количество улучшений", row=2, col=1)
    
    # Анализ "зависаний"
    stagnation_fig = go.Figure()
    
    # Определяем периоды "зависания" (более 24 часов без улучшений)
    stagnation_periods = []
    for i in range(1, len(upgrades_timeline)):
        interval = upgrades_timeline[i]["timestamp"] - upgrades_timeline[i-1]["timestamp"]
        if interval > 86400:  # более 24 часов
            stagnation_periods.append({
                "start": upgrades_timeline[i-1]["timestamp"] / 86400,  # в днях
                "end": upgrades_timeline[i]["timestamp"] / 86400,
                "duration": interval / 86400
            })
    
    # Визуализация периодов зависания
    if stagnation_periods:
        for period in stagnation_periods:
            stagnation_fig.add_trace(
                go.Bar(
                    x=[f"День {int(period['start'])}"],
                    y=[period["duration"]],
                    name=f"Период {period['duration']:.1f} дней",
                    hovertemplate=(
                        "Начало: День %{x}<br>"
                        "Длительность: %{y:.1f} дней"
                    )
                )
            )
    
    stagnation_fig.update_layout(
        height=400,
        title="Периоды без улучшений (>24 часов)",
        showlegend=False,
        xaxis_title="Начало периода",
        yaxis_title="Длительность (дни)"
    )
    
    # Статистика прогресса
    total_time = history[-1]["timestamp"] / 86400
    total_upgrades = len(upgrades_timeline)
    avg_upgrades_per_day = total_upgrades / total_time if total_time > 0 else 0
    stagnation_time = sum(p["duration"] for p in stagnation_periods)
    stagnation_percentage = (stagnation_time / total_time * 100) if total_time > 0 else 0
    
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        max_interval = max(intervals)
        min_interval = min(intervals)
    else:
        avg_interval = max_interval = min_interval = 0
    
    stats = html.Div([
        html.P(f"Общее время симуляции: {total_time:.1f} дней"),
        html.P(f"Всего улучшений: {total_upgrades}"),
        html.P(f"Среднее количество улучшений в день: {avg_upgrades_per_day:.2f}"),
        html.P(f"Среднее время между улучшениями: {avg_interval:.1f} часов"),
        html.P(f"Минимальное время между улучшениями: {min_interval:.1f} часов"),
        html.P(f"Максимальное время между улучшениями: {max_interval:.1f} часов"),
        html.P(f"Общее время без улучшений (>24ч): {stagnation_time:.1f} дней ({stagnation_percentage:.1f}%)"),
        html.P(f"Количество периодов без улучшений: {len(stagnation_periods)}"),
    ])
    
    return pace_fig, stagnation_fig, stats

# Обновляем анализ экономики (убираем круговую диаграмму)
@app.callback(
    [Output("economy-analysis", "figure"),
     Output("upgrades-efficiency", "figure")],
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_economy_analysis(data):
    if data is None or "history" not in data:
        return {}, {}
    
    history = data["history"]
    if not history:
        return {}, {}
    
    # Анализ доходов и расходов
    economy_fig = go.Figure()
    
    # Собираем данные о доходах и расходах
    timestamps = []
    income = []
    expenses = []
    balance = []
    
    for state in history:
        timestamps.append(state["timestamp"] / 86400)  # переводим в дни
        
        # Доход
        current_income = state["balance"]["earn_per_sec"] * 86400  # доход в день
        income.append(current_income)
        
        # Расходы
        daily_expenses = sum(
            action["cost"]
            for action in state["actions"]
            if action["type"] == "location_upgrade"
        )
        
        expenses.append(daily_expenses)
        balance.append(state["balance"]["gold"])
    
    # График баланса
    economy_fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=income,
            name="Доход/день",
            line=dict(color='green', width=2),
            hovertemplate="День %{x:.1f}<br>Доход: %{y:,.0f}/день"
        )
    )
    
    economy_fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=expenses,
            name="Расходы/день",
            line=dict(color='red', width=2),
            hovertemplate="День %{x:.1f}<br>Расходы: %{y:,.0f}"
        )
    )
    
    economy_fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=balance,
            name="Баланс",
            line=dict(color='blue', width=2),
            hovertemplate="День %{x:.1f}<br>Баланс: %{y:,.0f}"
        )
    )
    
    economy_fig.update_layout(
        height=500,
        title="Экономический анализ",
        xaxis_title="Время (дни)",
        yaxis_title="Золото",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    # Анализ эффективности улучшений
    efficiency_fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("ROI улучшений", "Стоимость улучшений по уровням"),
        specs=[[{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # Собираем данные об улучшениях
    upgrades_data = {}
    for state in history:
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                loc_id = action["location_id"]
                if loc_id not in upgrades_data:
                    upgrades_data[loc_id] = []
                
                roi = (action["reward_xp"] + action["reward_keys"] * 100) / action["cost"]
                upgrades_data[loc_id].append({
                    "level": action["new_level"],
                    "cost": action["cost"],
                    "roi": roi
                })
    
    # График ROI
    for loc_id, upgrades in upgrades_data.items():
        levels = [u["level"] for u in upgrades]
        rois = [u["roi"] for u in upgrades]
        
        efficiency_fig.add_trace(
            go.Bar(
                x=[f"Локация {loc_id}"] * len(levels),
                y=rois,
                name=f"Локация {loc_id}",
                text=levels,
                textposition="auto",
                hovertemplate=(
                    "Локация %{x}<br>"
                    "Уровень: %{text}<br>"
                    "ROI: %{y:.2f}"
                )
            ),
            row=1, col=1
        )
        
        # График стоимости
        efficiency_fig.add_trace(
            go.Scatter(
                x=levels,
                y=[u["cost"] for u in upgrades],
                name=f"Локация {loc_id}",
                mode="lines+markers",
                hovertemplate=(
                    "Уровень: %{x}<br>"
                    "Стоимость: %{y:,.0f}"
                )
            ),
            row=1, col=2
        )
    
    efficiency_fig.update_layout(
        height=500,
        showlegend=True,
        barmode="group"
    )
    
    efficiency_fig.update_xaxes(title_text="Локация", row=1, col=1)
    efficiency_fig.update_xaxes(title_text="Уровень локации", row=1, col=2)
    efficiency_fig.update_yaxes(title_text="ROI", row=1, col=1)
    efficiency_fig.update_yaxes(title_text="Стоимость улучшения", row=1, col=2)
    
    return economy_fig, efficiency_fig

# Отображение прогресса уровня пользователя
@app.callback(
    Output("user-level-progress", "figure"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_user_level_progress(data):
    if data is None or "history" not in data:
        return {}
    
    history = data["history"]
    if not history:
        return {}
    
    # Создаем DataFrame из истории
    level_data = []
    for state in history:
        level_data.append({
            "timestamp": state["timestamp"],
            "level": state["balance"]["user_level"],
            "xp": state["balance"]["xp"]
        })
        
        # Добавляем действия повышения уровня для более точного графика
        for action in state["actions"]:
            if action["type"] == "level_up":
                level_data.append({
                    "timestamp": action["timestamp"],
                    "level": action["new_level"],
                    "xp": state["balance"]["xp"]  # Используем XP из состояния
                })
    
    # Сортируем по времени
    level_data.sort(key=lambda x: x["timestamp"])
    
    # Создаем подграфики: уровень и XP
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Рост уровня персонажа", "Накопление опыта"),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # График уровня
    fig.add_trace(
        go.Scatter(
            x=[x["timestamp"] / 86400 for x in level_data],
            y=[x["level"] for x in level_data],
            mode="lines+markers",
            name="Уровень",
            line=dict(color='blue', width=2),
            hovertemplate="День %{x:.1f}<br>Уровень: %{y}"
        ),
        row=1, col=1
    )
    
    # График XP
    fig.add_trace(
        go.Scatter(
            x=[x["timestamp"] / 86400 for x in level_data],
            y=[x["xp"] for x in level_data],
            mode="lines",
            name="Опыт",
            line=dict(color='green', width=2),
            hovertemplate="День %{x:.1f}<br>XP: %{y}"
        ),
        row=2, col=1
    )
    
    # Добавляем аннотации для важных событий (повышение уровня)
    level_ups = [x for x in level_data if x.get("timestamp") and x["level"] > level_data[0]["level"]]
    for level_up in level_ups:
        fig.add_annotation(
            x=level_up["timestamp"] / 86400,
            y=level_up["level"],
            text=f"Уровень {level_up['level']}",
            showarrow=True,
            arrowhead=1,
            row=1, col=1
        )
    
    # Настройка макета
    fig.update_layout(
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    fig.update_xaxes(title_text="Время (дни)", row=1, col=1)
    fig.update_xaxes(title_text="Время (дни)", row=2, col=1)
    fig.update_yaxes(title_text="Уровень", row=1, col=1)
    fig.update_yaxes(title_text="Опыт (XP)", row=2, col=1)
    
    return fig

# Отображение ресурсов во времени
@app.callback(
    Output("resources-over-time", "figure"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_resources_over_time(data):
    if data is None or "history" not in data:
        return {}
    
    history = data["history"]
    if not history:
        return {}
    
    # Создаем DataFrame из истории
    resources_data = []
    for state in history:
        resources_data.append({
            "timestamp": state["timestamp"],
            "gold": state["balance"]["gold"],
            "keys": state["balance"]["keys"],
            "earn_per_sec": state["balance"]["earn_per_sec"]
        })
    
    # Сортируем по времени
    resources_data.sort(key=lambda x: x["timestamp"])
    
    # Создаем подграфики для разных метрик
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Накопление золота",
            "Скорость заработка золота",
            "Накопление ключей",
            "Заработок в час"
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. График накопления золота
    fig.add_trace(
        go.Scatter(
            x=[x["timestamp"] / 86400 for x in resources_data],
            y=[x["gold"] for x in resources_data],
            mode="lines",
            name="Золото",
            line=dict(color='gold', width=2),
            hovertemplate="День %{x:.1f}<br>Золото: %{y:,.0f}"
        ),
        row=1, col=1
    )
    
    # 2. График скорости заработка в секунду
    fig.add_trace(
        go.Scatter(
            x=[x["timestamp"] / 86400 for x in resources_data],
            y=[x["earn_per_sec"] for x in resources_data],
            mode="lines",
            name="Золото/сек",
            line=dict(color='orange', width=2),
            hovertemplate="День %{x:.1f}<br>Золото/сек: %{y:.2f}"
        ),
        row=1, col=2
    )
    
    # 3. График накопления ключей
    fig.add_trace(
        go.Scatter(
            x=[x["timestamp"] / 86400 for x in resources_data],
            y=[x["keys"] for x in resources_data],
            mode="lines+markers",
            name="Ключи",
            line=dict(color='purple', width=2),
            hovertemplate="День %{x:.1f}<br>Ключи: %{y}"
        ),
        row=2, col=1
    )
    
    # 4. График заработка в час
    fig.add_trace(
        go.Scatter(
            x=[x["timestamp"] / 86400 for x in resources_data],
            y=[x["earn_per_sec"] * 3600 for x in resources_data],
            mode="lines",
            name="Золото/час",
            line=dict(color='red', width=2),
            hovertemplate="День %{x:.1f}<br>Золото/час: %{y:,.0f}"
        ),
        row=2, col=2
    )
    
    # Настройка макета
    fig.update_layout(
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    # Настройка осей
    fig.update_xaxes(title_text="Время (дни)", row=1, col=1)
    fig.update_xaxes(title_text="Время (дни)", row=1, col=2)
    fig.update_xaxes(title_text="Время (дни)", row=2, col=1)
    fig.update_xaxes(title_text="Время (дни)", row=2, col=2)
    
    fig.update_yaxes(title_text="Золото", row=1, col=1)
    fig.update_yaxes(title_text="Золото/сек", row=1, col=2)
    fig.update_yaxes(title_text="Ключи", row=2, col=1)
    fig.update_yaxes(title_text="Золото/час", row=2, col=2)
    
    return fig

# Отображение информации о локациях
@app.callback(
    Output("locations-upgrades", "figure"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_locations_analysis(data):
    if data is None or "history" not in data:
        return {}
    
    history = data["history"]
    if not history:
        return {}
    
    # Собираем данные о локациях из истории
    locations_data = {}
    upgrades_timeline = []
    
    # Сначала инициализируем все локации из первого состояния
    if history:
        first_state = history[0]
        for loc_id, loc_state in first_state["locations"].items():
            locations_data[str(loc_id)] = {
                "current_level": loc_state["current_level"],
                "available": loc_state["available"],
                "upgrades_count": 0,
                "total_cost": 0,
                "total_xp": 0,
                "total_keys": 0,
                "upgrade_times": []
            }
    
    # Теперь обрабатываем историю
    for state in history:
        # Обновляем состояние локаций
        for loc_id, loc_state in state["locations"].items():
            loc_id = str(loc_id)
            locations_data[loc_id].update({
                "current_level": loc_state["current_level"],
                "available": loc_state["available"]
            })
        
        # Собираем информацию об улучшениях
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                loc_id = str(action["location_id"])
                locations_data[loc_id]["upgrades_count"] += 1
                locations_data[loc_id]["total_cost"] += action["cost"]
                locations_data[loc_id]["total_xp"] += action["reward_xp"]
                locations_data[loc_id]["total_keys"] += action["reward_keys"]
                locations_data[loc_id]["upgrade_times"].append(action["timestamp"])
                
                upgrades_timeline.append({
                    "timestamp": action["timestamp"],
                    "location_id": loc_id,
                    "cost": action["cost"],
                    "new_level": action["new_level"]
                })
    
    # Создаем подграфики
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Прогресс улучшения локаций",
            "Временная шкала улучшений"
        ),
        vertical_spacing=0.2
    )
    
    # 1. График прогресса улучшения локаций
    location_levels = []
    location_ids = []
    for loc_id in sorted(locations_data.keys(), key=int):
        location_levels.append(locations_data[loc_id]["current_level"])
        location_ids.append(f"Локация {loc_id}")
    
    fig.add_trace(
        go.Bar(
            x=location_ids,
            y=location_levels,
            name="Текущий уровень",
            marker_color='blue',
            hovertemplate="Локация: %{x}<br>Уровень: %{y}"
        ),
        row=1, col=1
    )
    
    # 2. Временная шкала улучшений
    if upgrades_timeline:
        for loc_id in sorted(locations_data.keys(), key=int):
            loc_upgrades = [u for u in upgrades_timeline if u["location_id"] == loc_id]
            if loc_upgrades:
                fig.add_trace(
                    go.Scatter(
                        x=[u["timestamp"] / 86400 for u in loc_upgrades],
                        y=[u["new_level"] for u in loc_upgrades],
                        mode="markers+lines",
                        name=f"Локация {loc_id}",
                        hovertemplate=(
                            "День %{x:.1f}<br>"
                            "Локация %{text}<br>"
                            "Уровень: %{y}"
                        ),
                        text=[f"Локация {loc_id}" for _ in loc_upgrades]
                    ),
                    row=2, col=1
                )
    
    # Настройка макета
    fig.update_layout(
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    # Настройка осей
    fig.update_xaxes(title_text="Локации", row=1, col=1)
    fig.update_xaxes(title_text="Время (дни)", row=2, col=1)
    fig.update_yaxes(title_text="Уровень", row=1, col=1)
    fig.update_yaxes(title_text="Уровень", row=2, col=1)
    
    return fig

# Таблица скорости накопления монет по уровням
@app.callback(
    Output("coins-per-level-table", "children"),
    Input("user-levels-store", "data"),
    prevent_initial_call=True
)
def update_coins_per_level_table(user_levels_data):
    if user_levels_data is None:
        return "Нет данных"
    
    # Создаем данные для таблицы
    table_data = [
        {
            "Уровень": level,
            "Монет/сек": level_data["gold_per_sec"],
            "Монет/час": level_data["gold_per_sec"] * 3600,
            "Монет/день": level_data["gold_per_sec"] * 86400,
            "XP для следующего уровня": level_data["xp_required"] if int(level) < max(map(int, user_levels_data.keys())) else "-"
        }
        for level, level_data in sorted(user_levels_data.items(), key=lambda x: int(x[0]))
    ]
    
    # Создаем таблицу
    return dash_table.DataTable(
        data=table_data,
        columns=[
            {"name": "Уровень", "id": "Уровень"},
            {"name": "Монет/сек", "id": "Монет/сек", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Монет/час", "id": "Монет/час", "type": "numeric", "format": {"specifier": ",.0f"}},
            {"name": "Монет/день", "id": "Монет/день", "type": "numeric", "format": {"specifier": ",.0f"}},
            {"name": "XP для следующего уровня", "id": "XP для следующего уровня"}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
            'padding': '10px',
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'border': '1px solid black'
        },
        style_data={
            'border': '1px solid grey'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )

# Обновляем отображение общей информации
@app.callback(
    [Output("completion-time", "children"),
     Output("final-resources", "children")],
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_completion_info(data):
    if data is None:
        return "Нет данных", "Нет данных"
    
    # Форматируем время завершения
    seconds = data["completion_time"]
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    completion_info = html.Div([
        html.H5("Время симуляции", style={"marginBottom": "10px"}),
        html.P([
            f"Симуляция завершена за {seconds:,} секунд",
            html.Br(),
            f"≈ {days} дней, {hours} часов, {minutes} минут"
        ], style={"fontSize": "16px", "color": "#666"})
    ], style={"marginBottom": "20px"})
    
    # Подсчитываем общие заработанные ресурсы
    history = data.get("history", [])
    if not history:
        return completion_info, "Нет данных"
    
    total_gold_earned = sum(
        state["balance"]["earn_per_sec"] * 
        (state["timestamp"] - history[i-1]["timestamp"] if i > 0 else state["timestamp"])
        for i, state in enumerate(history)
    )
    
    total_xp_earned = sum(
        action["reward_xp"]
        for state in history
        for action in state["actions"]
        if action["type"] == "location_upgrade"
    )
    
    total_keys_earned = sum(
        action["reward_keys"]
        for state in history
        for action in state["actions"]
        if action["type"] == "location_upgrade"
    )
    
    # Определяем максимальные достижения
    max_location_level = max(
        (loc_state["current_level"], loc_id)
        for state in history
        for loc_id, loc_state in state["locations"].items()
    )
    
    final_state = history[-1]
    final_user_level = final_state["balance"]["user_level"]
    
    resources_info = html.Div([
        html.Div([
            html.H5("Заработано за всю игру"),
            html.Div([
                html.P([
                    "Золото: ",
                    html.Span(f"{total_gold_earned:,.0f}", style={"fontWeight": "bold", "color": "#ffd700"})
                ]),
                html.P([
                    "Опыт: ",
                    html.Span(f"{total_xp_earned:,}", style={"fontWeight": "bold", "color": "#4CAF50"})
                ]),
                html.P([
                    "Ключи: ",
                    html.Span(f"{total_keys_earned:,}", style={"fontWeight": "bold", "color": "#9c27b0"})
                ])
            ], style={"marginLeft": "20px"})
        ], style={"marginBottom": "20px"}),
        
        html.Div([
            html.H5("Максимальные достижения"),
            html.Div([
                html.P([
                    "Локация: ",
                    html.Span(
                        f"#{max_location_level[1]} (уровень {max_location_level[0]})",
                        style={"fontWeight": "bold", "color": "#2196F3"}
                    )
                ]),
                html.P([
                    "Уровень персонажа: ",
                    html.Span(f"{final_user_level}", style={"fontWeight": "bold", "color": "#FF5722"})
                ])
            ], style={"marginLeft": "20px"})
        ])
    ], style={
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    })
    
    return completion_info, resources_info

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True, port=8050) 