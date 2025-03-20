#!/usr/bin/env python
"""
Скрипт для тестового запуска симулятора Indonesian Adventure.

Демонстрирует работу симулятора с настройками по умолчанию.
"""

import sys
import os

# Добавляем корневую директорию проекта в sys.path для корректного импорта модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from idadv_dash_simulator.simulator import Simulator
from idadv_dash_simulator.config.simulation_config import create_sample_config
from idadv_dash_simulator.utils.economy import format_time

def main():
    """Функция для тестового запуска симуляции."""
    # Создаем симулятор с настройками по умолчанию
    simulator = Simulator()
    
    # Запускаем симуляцию и получаем результат
    print("Запуск симуляции...")
    result = simulator.run_simulation()
    
    # Выводим результаты
    time_passed = format_time(result.timestamp)
    print(f"Симуляция завершена за {time_passed}")
    print(f"Финальное состояние: {simulator.workflow.balance}")
    print(f"Уровень пользователя: {simulator.workflow.balance.user_level}")
    print(f"Золото: {simulator.workflow.balance.gold:.2f}")
    print(f"Опыт: {simulator.workflow.balance.xp}")
    print(f"Ключи: {simulator.workflow.balance.keys}")
    print(f"Заработок в секунду: {simulator.workflow.balance.earn_per_sec:.2f}")

if __name__ == "__main__":
    main() 