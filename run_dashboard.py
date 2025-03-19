#!/usr/bin/env python
# Скрипт для запуска дашборда

import sys
import os

# Добавляем корневую директорию проекта в sys.path для корректного импорта модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Импортируем и запускаем дашборд
from idadv_dash_simulator.dashboard import app

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)