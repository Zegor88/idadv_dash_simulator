"""
Модуль макета дашборда Indonesian Adventure.
"""

from typing import List, Dict, Any
from dash import dcc, html
from dash.dash_table import DataTable

from idadv_dash_simulator.config.dashboard_config import (
    CHECKS_PER_DAY_MIN, CHECKS_PER_DAY_MAX, CHECKS_PER_DAY_DEFAULT,
    COOLDOWN_MULTIPLIER_MIN, COOLDOWN_MULTIPLIER_MAX, COOLDOWN_MULTIPLIER_STEP, COOLDOWN_MULTIPLIER_DEFAULT,
    DEFAULT_BASE_GOLD_PER_SEC, DEFAULT_EARN_COEFFICIENT,
    DEFAULT_STARTING_GOLD, DEFAULT_STARTING_XP, DEFAULT_STARTING_KEYS,
    STYLE_SECTION, STYLE_CONTAINER, STYLE_SIDEBAR, STYLE_MAIN_CONTENT, 
    STYLE_HEADER, STYLE_BUTTON,
    BASE_GOLD, STARTING_GOLD, STARTING_XP, STARTING_KEYS, EARN_COEFFICIENT, LOCATION_COUNT,
    DEFAULT_GAME_DURATION, DEFAULT_CHECK_SCHEDULE,
    DEFAULT_MAX_ENERGY, DEFAULT_TAP_SPEED, DEFAULT_GOLD_PER_TAP, DEFAULT_IS_TAPPING
)
from idadv_dash_simulator.models.config import SimulationAlgorithm
from idadv_dash_simulator.simulator import Simulator

def create_settings_panel():
    """
    Создает панель настроек симуляции.
    
    Returns:
        html.Div: Панель настроек
    """
    return html.Div([
        html.Div([
            html.H3("Настройки симуляции", style={"color": "#343a40", "marginBottom": "20px"}),
        ], style=STYLE_HEADER),
        
        # Экономические параметры
        html.Div([
            html.H4("Параметры экономики", className="settings-section-title"),
            
            html.Div([
                html.Label("Базовое значение золота в секунду:", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="base-gold-per-sec-input",
                    type="number",
                    value=DEFAULT_BASE_GOLD_PER_SEC,
                    step=0.01,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
            
            html.Div([
                html.Label("Коэффициент роста золота:", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="earn-coefficient-input",
                    type="number",
                    value=DEFAULT_EARN_COEFFICIENT,
                    step=0.001,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
        ], className="settings-section"),
        
        html.Hr(style={"margin": "20px 0", "opacity": "0.3"}),
        
        # Начальный баланс
        html.Div([
            html.H4("Стартовый баланс", className="settings-section-title"),
            
            html.Div([
                html.Label("Начальное количество золота:", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="starting-gold-input",
                    type="number",
                    value=DEFAULT_STARTING_GOLD,
                    step=100,
                    min=0,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
            
            html.Div([
                html.Label("Начальный опыт:", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="starting-xp-input",
                    type="number",
                    value=DEFAULT_STARTING_XP,
                    step=1,
                    min=0,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
            
            html.Div([
                html.Label("Начальное количество ключей:", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="starting-keys-input",
                    type="number",
                    value=DEFAULT_STARTING_KEYS,
                    step=1,
                    min=0,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
        ], className="settings-section"),
        
        html.Hr(style={"margin": "20px 0", "opacity": "0.3"}),
        
        # Параметры проверок
        html.Div([
            html.H4("Параметры проверок", className="settings-section-title"),
            
            html.Div([
                html.Label("Расписание проверок:", style={"display": "block", "marginBottom": "10px", "fontWeight": "bold"}),
                
                # Контейнер для динамического списка времени
                html.Div(id="check-times-container", style={"marginBottom": "15px"}),
                
                # Кнопка добавления нового времени
                html.Button(
                    "+", 
                    id="add-check-time-button",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#4CAF50",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "4px",
                        "width": "30px",
                        "height": "30px",
                        "fontSize": "18px",
                        "cursor": "pointer",
                        "marginBottom": "15px"
                    }
                ),
                
                # Хранилище для времен проверок
                dcc.Store(id="check-times-store", data={"schedule": ["08:00", "12:00", "16:00", "20:00"]}),
                
                # Длительность игровой сессии
                html.Div([
                    html.Label("Длительность сессии в минутах:", style={"display": "block", "marginBottom": "5px", "fontWeight": "bold"}),
                    dcc.Input(
                        id="game-duration-input",
                        type="number",
                        value=15,  # Значение по умолчанию: 15 минут
                        min=1,
                        max=60,
                        step=1,
                        style={"width": "100%", "padding": "8px", "borderRadius": "4px", "border": "1px solid #ddd"}
                    ),
                ], style={"marginTop": "20px"}),
            ], style={"marginBottom": "20px"}),
        ], className="settings-section"),
        
        html.Hr(style={"margin": "20px 0", "opacity": "0.3"}),
        
        # Параметры локаций
        html.Div([
            html.H4("Параметры локаций", className="settings-section-title"),
            
            html.Div([
                html.Label("Кулдаун между улучшениями (множитель):", style={"display": "block", "marginBottom": "10px"}),
                dcc.Slider(
                    id="cooldown-multiplier-slider",
                    min=COOLDOWN_MULTIPLIER_MIN,
                    max=COOLDOWN_MULTIPLIER_MAX,
                    step=COOLDOWN_MULTIPLIER_STEP,
                    value=COOLDOWN_MULTIPLIER_DEFAULT,
                    marks={i/10: str(i/10) for i in range(int(COOLDOWN_MULTIPLIER_MIN*10), int(COOLDOWN_MULTIPLIER_MAX*10) + 1, 5)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], style={"marginBottom": "20px"}),
            
            # Алгоритм симуляции
            html.Div([
                html.Label("Алгоритм улучшения локаций:", style={"display": "block", "marginBottom": "10px"}),
                dcc.RadioItems(
                    id="simulation-algorithm-radio",
                    options=[
                        {'label': ' Последовательное улучшение', 'value': SimulationAlgorithm.SEQUENTIAL.value},
                        {'label': ' Первое доступное улучшение', 'value': SimulationAlgorithm.FIRST_AVAILABLE.value},
                    ],
                    value=SimulationAlgorithm.SEQUENTIAL.value,
                    style={"marginBottom": "15px"},
                    inputStyle={"marginRight": "5px"},
                    labelStyle={"display": "block", "marginBottom": "10px"}
                ),
                html.Div([
                    html.P("Последовательное улучшение: локации улучшаются по порядку, требуется полное улучшение предыдущих локаций.", 
                           className="description-text", style={"fontSize": "12px", "color": "#666"}),
                    html.P("Первое доступное улучшение: улучшается первая доступная локация с истекшим кулдауном.",
                           className="description-text", style={"fontSize": "12px", "color": "#666"}),
                ], style={"marginTop": "5px"})
            ], style={"marginBottom": "20px"}),
        ], className="settings-section"),
        
        html.Hr(style={"margin": "20px 0", "opacity": "0.3"}),
        
        # Параметры тапания
        html.Div([
            html.H4("Параметры тапания", className="settings-section-title"),
            
            # Включение/отключение тапания
            html.Div([
                html.Label(
                    html.Div([
                        dcc.Checklist(
                            id="is-tapping-checkbox",
                            options=[{'label': ' Активировать тапание', 'value': 'is_tapping'}],
                            value=['is_tapping'] if DEFAULT_IS_TAPPING else [],
                            inputStyle={"marginRight": "5px"},
                            style={"fontWeight": "bold"}
                        ),
                        html.P(
                            "При активации пользователь будет тапать во время игровых сессий, расходуя энергию и получая золото.",
                            style={"fontSize": "12px", "color": "#666", "marginTop": "5px", "marginLeft": "25px"}
                        )
                    ]),
                    style={"display": "block", "marginBottom": "15px"}
                ),
            ]),
            
            # Максимальный запас энергии
            html.Div([
                html.Label("Максимальный запас энергии:", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="max-energy-input",
                    type="number",
                    value=DEFAULT_MAX_ENERGY,
                    step=50,
                    min=100,
                    max=2000,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
            
            # Скорость тапания
            html.Div([
                html.Label("Скорость тапания (тапов в секунду):", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="tap-speed-input",
                    type="number",
                    value=DEFAULT_TAP_SPEED,
                    step=0.5,
                    min=0.5,
                    max=10,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
            
            # Золото за тап
            html.Div([
                html.Label("Золото за 1 тап:", style={"display": "block", "marginBottom": "5px"}),
                dcc.Input(
                    id="gold-per-tap-input",
                    type="number",
                    value=DEFAULT_GOLD_PER_TAP,
                    step=1,
                    min=1,
                    max=100,
                    style={"width": "100%", "marginBottom": "15px", "padding": "8px"}
                ),
            ]),
            
            # Описание механики
            html.Div([
                html.P(
                    "Энергия расходуется по 1 ед. за 1 тап и восстанавливается со скоростью 1 ед/сек.",
                    style={"fontSize": "12px", "color": "#666", "marginTop": "5px"}
                ),
                html.P(
                    "Если энергия = 0, пользователь больше не тапает в рамках текущей сессии.",
                    style={"fontSize": "12px", "color": "#666", "marginTop": "5px"}
                ),
            ], style={"backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "5px"}),
            
        ], className="settings-section"),
        
        html.Button(
            "Запустить симуляцию", 
            id="run-simulation-button", 
            n_clicks=0,
            style=STYLE_BUTTON
        ),
        
        html.Div(id="simulation-status", style={"marginTop": "15px", "padding": "10px", "backgroundColor": "#e9ecef", "borderRadius": "5px"}),
    ], style=STYLE_SIDEBAR)

def create_overview_tab():
    """
    Создает вкладку с общей информацией.
    
    Returns:
        html.Div: Содержимое вкладки
    """
    return html.Div([
        html.Div([
            html.H4("Основные показатели", className="tab-section-title"),
            html.Div([
                html.Div(id="completion-time", className="info-card"),
                html.Div(id="final-resources", className="info-card"),
            ], style={"display": "flex", "gap": "20px", "marginBottom": "20px"}),
        ], className="tab-section"),
        
        html.Div([
            html.H4("Ключевые метрики", className="tab-section-title"),
            html.Div(id="key-metrics"),
        ], className="tab-section"),
    ])

def create_progress_tab():
    """
    Создает вкладку с прогрессом персонажа.
    
    Returns:
        html.Div: Содержимое вкладки
    """
    return html.Div([
        html.Div([
            html.H4("Рост уровня персонажа", className="tab-section-title"),
            dcc.Graph(id="user-level-progress"),
        ], className="tab-section"),
        
        html.Div([
            html.H4("Накопление ресурсов", className="tab-section-title"),
            dcc.Graph(id="resources-over-time"),
        ], className="tab-section"),
    ])

def create_locations_tab():
    """
    Создает вкладку анализа локаций.
    
    Returns:
        html.Div: Контейнер с содержимым вкладки
    """
    return html.Div([
        # Таблица стоимостей локаций
        html.Div([
            html.H4("Анализ локаций", className="tab-section-title"),
            html.Div([
                DataTable(
                    id="locations-cost-table",
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold',
                        'border': '1px solid #ddd'
                    },
                    style_cell={
                        'padding': '8px 15px',
                        'textAlign': 'center',
                        'backgroundColor': 'white',
                        'border': '1px solid #ddd',
                        'minWidth': '70px',
                        'maxWidth': '100px',
                        'whiteSpace': 'normal'
                    },
                    style_table={
                        'overflowX': 'auto',
                        'maxHeight': '400px',
                        'overflowY': 'auto'
                    },
                    fixed_rows={'headers': True},
                    tooltip_delay=0,
                    tooltip_duration=None
                ),
                # Легенда для цветов редкости
                html.Div([
                    html.Div([
                        html.Span("Редкость локаций:", style={"marginRight": "10px", "fontWeight": "bold"}),
                        html.Span([
                            html.Span("", style={
                                "display": "inline-block", 
                                "width": "12px", 
                                "height": "12px", 
                                "backgroundColor": "#f0f8ff", 
                                "marginRight": "5px",
                                "border": "1px solid #ddd"
                            }),
                            "Обычные",
                        ], style={"marginRight": "10px"}),
                        html.Span([
                            html.Span("", style={
                                "display": "inline-block", 
                                "width": "12px", 
                                "height": "12px", 
                                "backgroundColor": "#f5f0ff", 
                                "marginRight": "5px",
                                "border": "1px solid #ddd"
                            }),
                            "Редкие",
                        ], style={"marginRight": "10px"}),
                        html.Span([
                            html.Span("", style={
                                "display": "inline-block", 
                                "width": "12px", 
                                "height": "12px", 
                                "backgroundColor": "#fffbeb", 
                                "marginRight": "5px",
                                "border": "1px solid #ddd"
                            }),
                            "Легендарные",
                        ]),
                    ], style={"display": "flex", "alignItems": "center", "fontSize": "12px", "color": "#666"})
                ], style={"marginTop": "10px", "textAlign": "right"})
            ], style={"marginBottom": "30px"}),
        ], className="tab-section"),
        
        # График анализа локаций
        html.Div([
            html.H4("Прогресс локаций", className="tab-section-title"),
            dcc.Graph(id="locations-upgrades"),
        ], className="tab-section"),
        
        # Таблица истории улучшений локаций
        html.Div([
            html.H4("История улучшений локаций", className="tab-section-title"),
            DataTable(
                id="location-history-table",
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'padding': '8px 15px',
                    'textAlign': 'center',
                    'backgroundColor': 'white',
                    'border': '1px solid #ddd',
                    'minWidth': '100px',
                    'maxWidth': '180px',
                    'whiteSpace': 'normal'
                },
                style_table={
                    'overflowX': 'auto'
                }
            ),
        ], className="tab-section"),
    ])

def create_economy_tab():
    """
    Создает вкладку экономического анализа.
    
    Returns:
        html.Div: Контейнер с содержимым вкладки
    """
    return html.Div([
        # 1. Базовая экономика
        html.Div([
            html.H4("Базовая экономика", className="tab-section-title"),
            dcc.Graph(id="gold-per-sec-progression"),
            DataTable(
                id="gold-per-sec-table",
                columns=[
                    {"name": "Уровень", "id": "level"},
                    {"name": "Gold/sec", "id": "gold_per_sec"},
                    {"name": "Gold/hour", "id": "gold_per_hour"},
                    {"name": "Gold/day", "id": "gold_per_day"},
                    {"name": "Прирост", "id": "growth"},
                ],
                style_table={"overflowX": "auto", "borderRadius": "5px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"},
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'padding': '8px 15px',
                    'textAlign': 'center',
                    'backgroundColor': 'white',
                    'border': '1px solid #ddd'
                },
            ),
        ], className="tab-section"),
        
        # 2. Динамика экономики
        html.Div([
            html.H4("Динамика экономики", className="tab-section-title"),
            dcc.Graph(id="economy-analysis"),
            html.Div([
                html.H5("Ключевые показатели", className="subsection-title"),
                html.Div(id="economy-metrics", className="metrics-container"),
            ]),
        ], className="tab-section"),
        
        # 3. Баланс золота
        html.Div([
            html.H4("Баланс золота", className="tab-section-title"),
            DataTable(
                id="upgrades-history-table",
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'padding': '8px 15px',
                    'textAlign': 'center',
                    'backgroundColor': 'white',
                    'border': '1px solid #ddd'
                }
            ),
        ], className="tab-section"),
    ])

def create_pace_tab():
    """
    Создает вкладку с анализом темпа игры.
    
    Returns:
        html.Div: Содержимое вкладки
    """
    return html.Div([
        html.Div([
            html.H4("Анализ времени между улучшениями", className="tab-section-title"),
            dcc.Graph(id="progression-pace"),
        ], className="tab-section"),
        
        html.Div([
            html.H4("Анализ периодов без улучшений", className="tab-section-title"),
            dcc.Graph(id="stagnation-analysis"),
        ], className="tab-section"),
        
        html.Div([
            html.H4("Статистика прогресса", className="tab-section-title"),
            html.Div(id="progression-stats", className="stats-container"),
        ], className="tab-section"),
        
        html.Div([
            html.H4("События по дням", className="tab-section-title"),
            DataTable(
                id="daily-events-table",
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '10px',
                    'minWidth': '80px',
                    'maxWidth': '180px',
                    'whiteSpace': 'normal',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                page_size=10,
                sort_action='native',
            ),
        ], className="tab-section"),
    ])

def create_tapping_tab():
    """
    Создает вкладку анализа тапания.
    
    Returns:
        html.Div: Контейнер с содержимым вкладки
    """
    return html.Div([
        # 1. График "Тапы и Золото по дням"
        html.Div([
            html.H4("Тапы и Золото по дням", className="tab-section-title"),
            dcc.Graph(id="taps-gold-by-day-graph"),
            html.Div([
                html.H5("Сводная статистика", className="subsection-title", style={"marginTop": "15px"}),
                html.Div([
                    html.Div([
                        html.P("Всего тапов:", style={"fontWeight": "bold", "margin": "0"}),
                        html.P(id="total-taps", className="metric-value")
                    ], className="metric-box"),
                    html.Div([
                        html.P("Всего золота от тапов:", style={"fontWeight": "bold", "margin": "0"}),
                        html.P(id="total-gold-from-taps", className="metric-value")
                    ], className="metric-box"),
                    html.Div([
                        html.P("Среднее тапов за сессию:", style={"fontWeight": "bold", "margin": "0"}),
                        html.P(id="avg-taps-per-session", className="metric-value")
                    ], className="metric-box"),
                ], style={"display": "flex", "flexWrap": "wrap", "gap": "15px", "marginTop": "10px", "justifyContent": "space-between"})
            ]),
        ], className="tab-section"),
        
        # 2. График "Энергия по времени" (внутри одной сессии)
        html.Div([
            html.H4("Энергия по времени (в рамках сессии)", className="tab-section-title"),
            dcc.Dropdown(
                id="session-select-dropdown",
                placeholder="Выберите сессию для анализа",
                style={"marginBottom": "15px"}
            ),
            dcc.Graph(id="energy-over-time-graph"),
        ], className="tab-section"),
        
        # 3. Таблица по дням
        html.Div([
            html.H4("Статистика тапания по дням", className="tab-section-title"),
            DataTable(
                id="tapping-stats-table",
                columns=[
                    {"name": "День", "id": "day"},
                    {"name": "Количество тапов", "id": "taps"},
                    {"name": "Потрачено энергии", "id": "energy"},
                    {"name": "Получено золота", "id": "gold"},
                ],
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd'
                },
                style_cell={
                    'padding': '8px 15px',
                    'textAlign': 'center',
                    'backgroundColor': 'white',
                    'border': '1px solid #ddd'
                },
                style_table={
                    'overflowX': 'auto'
                }
            ),
        ], className="tab-section"),
    ])

def create_tabs():
    """
    Создает набор вкладок для отображения результатов симуляции.
    
    Returns:
        dcc.Tabs: Компонент с вкладками
    """
    return dcc.Tabs([
        dcc.Tab(label="Обзор", children=create_overview_tab(), className="custom-tab", selected_className="custom-tab--selected"),
        dcc.Tab(label="Прогресс", children=create_progress_tab(), className="custom-tab", selected_className="custom-tab--selected"),
        dcc.Tab(label="Локации", children=create_locations_tab(), className="custom-tab", selected_className="custom-tab--selected"),
        dcc.Tab(label="Экономика", children=create_economy_tab(), className="custom-tab", selected_className="custom-tab--selected"),
        dcc.Tab(label="Темп", children=create_pace_tab(), className="custom-tab", selected_className="custom-tab--selected"),
        dcc.Tab(label="Тапание", children=create_tapping_tab(), className="custom-tab", selected_className="custom-tab--selected"),
    ], className="custom-tabs")

def create_layout(title):
    """
    Создает основной макет дашборда.
    
    Args:
        title: Заголовок дашборда
        
    Returns:
        html.Div: Макет дашборда
    """
    return html.Div([
        # Добавляем стили через external_stylesheets
        html.Link(
            rel='stylesheet',
            href='/assets/style.css'
        ),
        
        # Заголовок
        html.Div([
            html.H1(title, style={"margin": "0", "color": "white"})
        ], style={"backgroundColor": "#343a40", "padding": "15px 20px", "boxShadow": "0 2px 5px rgba(0,0,0,0.2)"}),
        
        # Основной контейнер (сайдбар + контент)
        html.Div([
            # Панель настроек (слева)
            create_settings_panel(),
            
            # Основной контент (справа)
            html.Div([
                create_tabs(),
            ], style=STYLE_MAIN_CONTENT),
        ], style=STYLE_CONTAINER),
        
        # Хранилища данных
        dcc.Store(id="simulation-data-store"),
        dcc.Store(id="user-levels-store"),
        # Добавляем флаг, указывающий, что симуляция еще не запущена
        dcc.Store(id="auto-run-store", data={"auto_run": False}),
        # Хранилище для данных о тапании
        dcc.Store(id="tapping-stats-store")
    ]) 