"""
Модуль коллбеков для дашборда Indonesian Adventure.
"""

# Импортируем все коллбеки для автоматической регистрации
from idadv_dash_simulator.dashboard.simulation import *
from idadv_dash_simulator.dashboard.callbacks.economy import *
from idadv_dash_simulator.dashboard.callbacks.progression import *
from idadv_dash_simulator.dashboard.callbacks.locations import *
from idadv_dash_simulator.dashboard.callbacks.tapping import *
# Не импортируем callbacks/simulation.py, т.к. все его функции уже есть в dashboard/simulation.py 