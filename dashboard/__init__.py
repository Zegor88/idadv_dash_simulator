"""
Модуль дашборда для симулятора Indonesian Adventure.
"""

import dash
from dash import html

from idadv_dash_simulator.config.dashboard_config import APP_TITLE, ASSETS_FOLDER

# Инициализация приложения Dash
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    assets_folder=ASSETS_FOLDER
)

# Импортируем компоненты
from idadv_dash_simulator.dashboard.layout import create_layout
from idadv_dash_simulator.dashboard import callbacks

# Устанавливаем макет
app.layout = create_layout(APP_TITLE) 