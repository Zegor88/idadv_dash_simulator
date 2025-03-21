"""
Модуль дашборда для симулятора Indonesian Adventure.
"""

import dash
from dash import html, dcc

from idadv_dash_simulator.config.dashboard_config import APP_TITLE, ASSETS_FOLDER

def create_dash_app():
    """
    Создаёт и настраивает экземпляр приложения Dash.
    
    Returns:
        dash.Dash: Настроенное приложение Dash
    """
    app_instance = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder=ASSETS_FOLDER,
        title=APP_TITLE
    )
    
    # Импортируем компоненты
    from idadv_dash_simulator.dashboard.layout import create_layout
    
    # Устанавливаем макет с хранилищем auto-run
    full_layout = create_layout(APP_TITLE)
    full_layout.children.insert(0, dcc.Store(id="auto-run-store", data={"auto_run": False}))
    app_instance.layout = full_layout
    
    return app_instance

# Создаем экземпляр приложения
app = create_dash_app()

# Регистрируем все коллбеки (импорт должен быть здесь, чтобы избежать циклических импортов)
from idadv_dash_simulator.dashboard import callbacks 