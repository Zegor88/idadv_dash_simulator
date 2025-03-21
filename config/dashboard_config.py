"""
Конфигурационный файл для настроек дашборда.
Содержит параметры интерфейса и отображения данных.
"""

# Общие настройки
APP_TITLE = "Анализ игровой механики Indonesian Adventure"
ASSETS_FOLDER = 'assets'
DEBUG_MODE = True
PORT = 8050

# Настройки экрана
DEFAULT_GRAPH_HEIGHT = 600
DEFAULT_FIGURE_LAYOUT = {
    "showlegend": True,
    "hovermode": "x unified",
    "legend": {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "center",
        "x": 0.5
    }
}

# Настройки интервалов и слайдеров
CHECKS_PER_DAY_MIN = 1
CHECKS_PER_DAY_MAX = 8
CHECKS_PER_DAY_DEFAULT = 5

COOLDOWN_MULTIPLIER_MIN = 0.5
COOLDOWN_MULTIPLIER_MAX = 2.0
COOLDOWN_MULTIPLIER_STEP = 0.1
COOLDOWN_MULTIPLIER_DEFAULT = 1.0

# Экономические параметры по умолчанию
DEFAULT_BASE_GOLD_PER_SEC = 0.56
DEFAULT_EARN_COEFFICIENT = 1.090824358

# Стартовый баланс по умолчанию
DEFAULT_STARTING_GOLD = 1000.0
DEFAULT_STARTING_XP = 1
DEFAULT_STARTING_KEYS = 1

# Настройки стилей
STYLE_SECTION = {
    "marginBottom": "20px"
}

STYLE_METRICS_BOX = {
    "textAlign": "center", 
    "backgroundColor": "#f8f9fa", 
    "padding": "15px", 
    "borderRadius": "8px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    "width": "30%",
    "margin": "10px"
}

# Стили для макета дашборда
STYLE_CONTAINER = {
    "display": "flex",
    "flexDirection": "row", 
    "height": "calc(100vh - 80px)",
    "width": "100%",
    "maxWidth": "1800px",
    "margin": "0 auto",
    "fontFamily": "Arial, sans-serif"
}

STYLE_SIDEBAR = {
    "width": "300px",
    "minWidth": "250px",
    "backgroundColor": "#f8f9fa",
    "padding": "20px",
    "boxShadow": "2px 0 10px rgba(0,0,0,0.1)",
    "overflow": "auto",
    "height": "100%",
    "position": "sticky",
    "top": "0"
}

STYLE_MAIN_CONTENT = {
    "flex": "1",
    "padding": "20px",
    "overflow": "auto",
    "height": "100%"
}

STYLE_HEADER = {
    "backgroundColor": "#343a40",
    "color": "white",
    "padding": "10px 20px",
    "marginBottom": "20px",
    "borderRadius": "5px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.2)"
}

STYLE_BUTTON = {
    "backgroundColor": "#007bff",
    "color": "white",
    "padding": "10px 15px",
    "border": "none",
    "borderRadius": "5px",
    "cursor": "pointer",
    "marginTop": "20px",
    "width": "100%",
    "fontWeight": "bold"
}

# Добавляем STYLE_FLEX_ROW, который используется в callbacks
STYLE_FLEX_ROW = {
    "display": "flex",
    "flexDirection": "row",
    "flexWrap": "wrap",
    "gap": "15px",
    "alignItems": "center"
}

# Настройки графиков
PLOT_COLORS = {
    "gold": "#ffd700",
    "xp": "#4CAF50",
    "keys": "#9c27b0",
    "income": "green",
    "expenses": "red",
    "balance": "blue",
    "level": "#FF5722"
}

# Интервалы времени для записи состояния (в секундах)
STATE_RECORD_INTERVAL = 86400  # 1 день

# Настройки локаций
LOCATION_COUNT = 20  # Количество локаций в игре

# Настройки расписания проверок
DEFAULT_CHECK_SCHEDULE = ["08:00", "12:00", "16:00", "20:00"]
DEFAULT_GAME_DURATION = 15  # минут

# Базовые экономические параметры
BASE_GOLD = 0.56
STARTING_GOLD = 1000.0
STARTING_XP = 1
STARTING_KEYS = 1
EARN_COEFFICIENT = 1.090824358

# Параметры тапания
DEFAULT_MAX_ENERGY = 700  # Максимальный запас энергии
DEFAULT_TAP_SPEED = 3.0  # Скорость тапания (тапов в секунду)
DEFAULT_GOLD_PER_TAP = 10.0  # Золото за 1 тап
DEFAULT_IS_TAPPING = False  # По умолчанию тапание выключено

# Цвета для графиков тапания
TAPPING_COLORS = {
    "taps": "#2196F3",  # Синий
    "gold": "#FFD700",  # Золотой
    "energy": "#4CAF50"  # Зеленый
}

# Стили для графиков тапания
TAPPING_GRAPH_LAYOUT = {
    **DEFAULT_FIGURE_LAYOUT,
    "colorway": ["#2196F3", "#FFD700", "#4CAF50"],
    "margin": {"l": 40, "r": 40, "t": 40, "b": 40}
} 