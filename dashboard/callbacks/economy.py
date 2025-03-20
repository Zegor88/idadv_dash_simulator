"""
Коллбеки для экономического анализа.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, html

from idadv_dash_simulator.utils.economy import calculate_gold_per_sec
from idadv_dash_simulator.utils.plotting import create_subplot_figure, add_time_series, create_bar_chart
from idadv_dash_simulator.utils.data_processing import extract_upgrades_timeline
from idadv_dash_simulator.config.dashboard_config import PLOT_COLORS, STYLE_METRICS_BOX, STYLE_FLEX_ROW
from idadv_dash_simulator.dashboard import app

@app.callback(
    [Output("gold-per-sec-progression", "figure"),
     Output("gold-per-sec-table", "data")],
    [Input("base-gold-per-sec-input", "value"),
     Input("earn-coefficient-input", "value")]
)
def update_gold_progression(base_gold, earn_coefficient):
    """
    Обновляет график и таблицу прогрессии gold/sec.
    
    Args:
        base_gold: Базовое значение золота в секунду
        earn_coefficient: Коэффициент роста
        
    Returns:
        list: [figure, table_data]
    """
    if base_gold is None or earn_coefficient is None:
        return {}, []
    
    # Рассчитываем значения для первых 10 уровней
    levels = list(range(1, 11))
    gold_per_sec_values = [calculate_gold_per_sec(base_gold, earn_coefficient, level) for level in levels]
    
    # Создаем фигуру
    fig = go.Figure()
    
    # Добавляем линейный график с точками
    fig.add_trace(go.Scatter(
        x=levels,
        y=gold_per_sec_values,
        name="Gold/sec",
        mode='lines+markers',
        line=dict(color=PLOT_COLORS["gold"], width=2),
        marker=dict(size=8),
        hovertemplate="Уровень %{x}<br>Gold/sec: %{y:.4f}"
    ))
    
    # Настраиваем макет
    fig.update_layout(
        title={
            'text': "Прогрессия заработка золота по уровням",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis={
            'title': "Уровень персонажа",
            'title_font': {'size': 14},
            'tickfont': {'size': 12},
            'gridcolor': 'lightgray'
        },
        yaxis={
            'title': "Золото в секунду (Gold/sec)",
            'title_font': {'size': 14},
            'tickfont': {'size': 12},
            'gridcolor': 'lightgray',
            'tickformat': '.4f'
        },
        showlegend=False,  # Убираем легенду, так как у нас один график
        hovermode="x unified",
        plot_bgcolor='white'
    )
    
    # Подготавливаем данные для таблицы
    table_data = []
    prev_value = None
    
    for level, value in zip(levels, gold_per_sec_values):
        growth = "-"
        if prev_value is not None:
            growth_pct = (value / prev_value - 1) * 100
            growth = f"+{growth_pct:.2f}%"
        
        table_data.append({
            "level": level,
            "gold_per_sec": f"{value:.4f}",
            "growth": growth
        })
        
        prev_value = value
    
    return fig, table_data


@app.callback(
    [Output("economy-analysis", "figure"),
     Output("upgrades-efficiency", "figure")],
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_economy_analysis(data):
    """
    Обновляет графики экономического анализа.
    
    Args:
        data: Данные симуляции
        
    Returns:
        list: [экономический анализ, эффективность улучшений]
    """
    if data is None or "history" not in data:
        return {}, {}
    
    history = data["history"]
    if not history:
        return {}, {}
    
    # Извлекаем данные по ресурсам
    resources_data = []
    for state in history:
        resources_data.append({
            "day": state["timestamp"] / 86400,
            "gold": state["balance"]["gold"],
            "earn_per_sec": state["balance"]["earn_per_sec"],
            "earn_per_day": state["balance"]["earn_per_sec"] * 86400
        })
    
    # Извлекаем данные по улучшениям
    upgrades_timeline = extract_upgrades_timeline(history)
    
    # Вычисляем расходы по дням
    expenses_by_day = {}
    for upgrade in upgrades_timeline:
        day = int(upgrade["day"])
        expenses_by_day[day] = expenses_by_day.get(day, 0) + upgrade["cost"]
    
    # Вычисляем доходы по дням
    income_by_day = {}
    
    for i in range(1, len(resources_data)):
        day = int(resources_data[i]["day"])
        prev_day = int(resources_data[i-1]["day"])
        
        if day == prev_day:
            continue
            
        avg_earn_per_day = (resources_data[i]["earn_per_day"] + resources_data[i-1]["earn_per_day"]) / 2
        income_by_day[prev_day] = avg_earn_per_day
    
    # График для экономического анализа
    economy_fig = create_subplot_figure(
        rows=2, cols=1,
        subplot_titles=("Баланс золота", "Доходы и расходы по дням"),
        vertical_spacing=0.3
    )
    
    # Добавляем баланс золота
    days = [r["day"] for r in resources_data]
    gold = [r["gold"] for r in resources_data]
    
    add_time_series(
        economy_fig, 
        x=days, 
        y=gold, 
        name="Золото", 
        color=PLOT_COLORS["gold"],
        row=1, col=1
    )
    
    # Добавляем доходы и расходы
    all_days = sorted(set(list(income_by_day.keys()) + list(expenses_by_day.keys())))
    
    income_days = []
    income_values = []
    expense_days = []
    expense_values = []
    balance_days = []
    balance_values = []
    
    for day in all_days:
        income = income_by_day.get(day, 0)
        expense = expenses_by_day.get(day, 0)
        balance = income - expense
        
        income_days.append(day)
        income_values.append(income)
        
        expense_days.append(day)
        expense_values.append(expense)
        
        balance_days.append(day)
        balance_values.append(balance)
    
    add_time_series(
        economy_fig, 
        x=income_days, 
        y=income_values, 
        name="Доход", 
        color=PLOT_COLORS["income"],
        row=2, col=1
    )
    
    add_time_series(
        economy_fig, 
        x=expense_days, 
        y=expense_values, 
        name="Расход", 
        color=PLOT_COLORS["expenses"],
        row=2, col=1
    )
    
    add_time_series(
        economy_fig, 
        x=balance_days, 
        y=balance_values, 
        name="Баланс", 
        color=PLOT_COLORS["balance"],
        row=2, col=1
    )
    
    economy_fig.update_layout(
        height=800,  # Увеличиваем высоту для лучшей читаемости
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'size': 12},
        title={
            'text': "Экономический анализ",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        }
    )
    
    # Обновляем оси для графика баланса золота
    economy_fig.update_xaxes(
        title_text="День игры",
        title_font={'size': 14},
        tickfont={'size': 12},
        gridcolor='lightgray',
        row=1, col=1
    )
    economy_fig.update_yaxes(
        title_text="Баланс золота",
        title_font={'size': 14},
        tickfont={'size': 12},
        gridcolor='lightgray',
        tickformat='.0f',
        row=1, col=1
    )

    # Обновляем оси для графика доходов и расходов
    economy_fig.update_xaxes(
        title_text="День игры",
        title_font={'size': 14},
        tickfont={'size': 12},
        gridcolor='lightgray',
        row=2, col=1
    )
    economy_fig.update_yaxes(
        title_text="Золото в день",
        title_font={'size': 14},
        tickfont={'size': 12},
        gridcolor='lightgray',
        tickformat='.0f',
        row=2, col=1
    )
    
    # График для анализа эффективности улучшений
    efficiency_fig = go.Figure()

    # Собираем данные для графика эффективности
    locations = {}

    for upgrade in upgrades_timeline:
        loc_id = upgrade["location_id"]
        
        if loc_id not in locations:
            locations[loc_id] = {
                "levels": [],
                "costs": []
            }
        
        locations[loc_id]["levels"].append(upgrade["new_level"])
        locations[loc_id]["costs"].append(upgrade["cost"])

    # Отображаем стоимость улучшений
    for loc_id, loc_data in locations.items():
        x_labels = [f"Лок {loc_id} (ур.{level})" for level in loc_data["levels"]]
        
        # Добавляем график стоимости улучшений как линию с точками
        efficiency_fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=loc_data["costs"],
                name=f"Локация {loc_id}",
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=8),
                hovertemplate="Уровень: %{x}<br>Стоимость: %{y:,.0f}<extra></extra>"
            )
        )

    # Обновляем настройки графика
    efficiency_fig.update_layout(
        height=500,  # Уменьшаем высоту, так как теперь один график
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'size': 12},
        title={
            'text': "Стоимость улучшений локаций",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2,  # Размещаем легенду под графиком
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 12},
            'traceorder': 'normal'
        },
        margin={'b': 100},  # Увеличиваем нижний отступ для легенды
        hovermode='x unified'
    )

    # Обновляем оси для графика стоимости улучшений
    efficiency_fig.update_xaxes(
        title_text="Уровень локации",
        title_font={'size': 14},
        tickfont={'size': 12},
        gridcolor='lightgray',
        showgrid=True
    )
    efficiency_fig.update_yaxes(
        title_text="Стоимость улучшения (золото)",
        title_font={'size': 14},
        tickfont={'size': 12},
        gridcolor='lightgray',
        showgrid=True,
        tickformat='.0f'
    )

    return economy_fig, efficiency_fig


@app.callback(
    Output("economy-metrics", "children"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_economy_metrics(data):
    """
    Обновляет метрики экономики.
    
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
    
    # Собираем данные об экономике
    total_income = 0
    total_expenses = 0
    start_earn_per_sec = history[0]["balance"]["earn_per_sec"]
    final_earn_per_sec = history[-1]["balance"]["earn_per_sec"]
    
    for state in history:
        for action in state["actions"]:
            if action["type"] == "location_upgrade":
                total_expenses += action["cost"]
    
    # Приблизительный расчет дохода
    for i in range(1, len(history)):
        # Время между состояниями
        time_diff = history[i]["timestamp"] - history[i-1]["timestamp"]
        # Средний заработок в секунду за период
        avg_earn = (history[i]["balance"]["earn_per_sec"] + history[i-1]["balance"]["earn_per_sec"]) / 2
        # Доход за период
        period_income = avg_earn * time_diff
        total_income += period_income
    
    # Рассчитываем показатели
    earn_growth = ((final_earn_per_sec / start_earn_per_sec) - 1) * 100
    economy_efficiency = (total_income / total_expenses) * 100 if total_expenses > 0 else 0
    
    return html.Div([
        html.Div([
            html.H3(f"{total_income:,.0f}"),
            html.P("Всего заработано")
        ], style=STYLE_METRICS_BOX),
        
        html.Div([
            html.H3(f"{total_expenses:,.0f}"),
            html.P("Всего потрачено")
        ], style=STYLE_METRICS_BOX),
        
        html.Div([
            html.H3(f"{earn_growth:,.1f}%"),
            html.P("Рост заработка")
        ], style=STYLE_METRICS_BOX),
        
        html.Div([
            html.H3(f"{economy_efficiency:,.1f}%"),
            html.P("Эффективность экономики")
        ], style=STYLE_METRICS_BOX)
    ], style=STYLE_FLEX_ROW)


@app.callback(
    Output("roi-analysis-table", "data"),
    Output("roi-analysis-table", "columns"),
    Input("simulation-data-store", "data"),
    prevent_initial_call=True
)
def update_roi_analysis(data):
    """
    Обновляет таблицу анализа улучшений.
    
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
    
    # Собираем данные об улучшениях
    upgrades_timeline = extract_upgrades_timeline(history)
    
    if not upgrades_timeline:
        return [], []
    
    # Группируем по локациям и уровням
    upgrades_data = []
    
    for upgrade in upgrades_timeline:
        gold_before = upgrade["gold_before"]
        cost = upgrade["cost"]
        gold_after = gold_before - cost
        
        upgrades_data.append({
            "День": f"{upgrade['day']:.1f}",
            "Локация": f"Локация {upgrade['location_id']}",
            "Уровень": upgrade["new_level"],
            "Золото до покупки": f"{gold_before:,.0f}",
            "Стоимость, золото": f"{cost:,.0f}",
            "Золото после покупки": f"{gold_after:,.0f}",
            "Награда XP": upgrade["reward_xp"],
            "Награда ключи": upgrade["reward_keys"]
        })
    
    # Сортируем по дню (хронологически)
    upgrades_data = sorted(upgrades_data, key=lambda x: float(x["День"]))
    
    # Определяем столбцы
    columns = [
        {"name": "День", "id": "День"},
        {"name": "Локация", "id": "Локация"},
        {"name": "Уровень", "id": "Уровень"},
        {"name": "Золото до покупки", "id": "Золото до покупки"},
        {"name": "Стоимость, золото", "id": "Стоимость, золото"},
        {"name": "Золото после покупки", "id": "Золото после покупки"},
        {"name": "Награда XP", "id": "Награда XP"},
        {"name": "Награда ключи", "id": "Награда ключи"}
    ]
    
    return upgrades_data, columns


@app.callback(
    Output("sensitivity-analysis", "figure"),
    [Input("base-gold-per-sec-input", "value"),
     Input("earn-coefficient-input", "value")]
)
def update_sensitivity_analysis(base_gold, earn_coefficient):
    """
    Обновляет график анализа чувствительности.
    
    Args:
        base_gold: Базовое значение золота в секунду
        earn_coefficient: Коэффициент роста
        
    Returns:
        go.Figure: График анализа чувствительности
    """
    if base_gold is None or earn_coefficient is None:
        return {}
    
    # Создаем вариации параметров
    base_variations = [base_gold * (1 + i*0.05) for i in range(-4, 5)]
    coef_variations = [earn_coefficient * (1 + i*0.01) for i in range(-4, 5)]
    
    # Фиксируем один параметр и варьируем другой
    levels = [1, 5, 10]
    
    # Создаем график
    fig = create_subplot_figure(
        rows=2, cols=1,
        subplot_titles=(
            "Влияние базового значения gold/sec",
            "Влияние коэффициента роста"
        ),
        vertical_spacing=0.3
    )
    
    # Анализ влияния базового значения
    for level in levels:
        values = [calculate_gold_per_sec(base, earn_coefficient, level) for base in base_variations]
        add_time_series(
            fig, 
            x=base_variations, 
            y=values, 
            name=f"Уровень {level}",
            mode="lines+markers",
            row=1, col=1
        )
    
    # Анализ влияния коэффициента
    for level in levels:
        values = [calculate_gold_per_sec(base_gold, coef, level) for coef in coef_variations]
        add_time_series(
            fig, 
            x=coef_variations, 
            y=values, 
            name=f"Уровень {level}",
            mode="lines+markers",
            row=2, col=1
        )
    
    # Обновляем макет
    fig.update_layout(
        height=700
    )
    
    # Обновляем подписи осей
    fig.update_xaxes(title="Базовое значение gold/sec", row=1, col=1)
    fig.update_yaxes(title="Итоговое значение gold/sec", row=1, col=1)
    
    fig.update_xaxes(title="Коэффициент роста", row=2, col=1)
    fig.update_yaxes(title="Итоговое значение gold/sec", row=2, col=1)
    
    return fig 