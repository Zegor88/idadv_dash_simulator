import logging
from typing import Dict, List, Optional

from idadv_dash_simulator.models.config import SimulationConfig
from idadv_dash_simulator.models.enums import LocationRarityType
from idadv_dash_simulator.workflow.location import Location
from idadv_dash_simulator.workflow.workflow import Workflow
from idadv_dash_simulator.workflow.simulation_response import SimulationResponse

from idadv_dash_simulator.sample_config import create_sample_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Simulator")

class Simulator:
    def __init__(self, config: Optional[SimulationConfig] = None):
        """
        Инициализирует симулятор с указанной конфигурацией.
        
        Args:
            config: Конфигурация симуляции. Если не указана, используется пример конфигурации.
        """
        self.config = config or create_sample_config()
        self.workflow = Workflow()
        
    def setup_workflow(self) -> None:
        """Настраивает рабочий процесс (workflow) для симуляции."""
        
        # Добавляем все локации
        self.workflow.locations.clear()
        for index, loc_config in self.config.locations.items():
            if not loc_config.levels:
                continue
                
            self.workflow.locations[index] = Location(
                rarity=loc_config.rarity,
                min_character_level=self.config.location_rarity_config[loc_config.rarity].user_level_required,
                levels=loc_config.levels,
                keys=self.config.location_rarity_config[loc_config.rarity].keys_reward
            )
        
        # Добавляем информацию о кулдаунах
        self.workflow.cooldowns.clear()
        self.workflow.cooldowns.update(self.config.location_cooldowns)
        
        # Добавляем конфигурацию уровней пользователя
        self.workflow.user_levels.clear()
        self.workflow.user_levels.update(self.config.user_levels)
        
        # Добавляем расписание проверок
        self.workflow.check_schedule.clear()
        self.workflow.check_schedule.extend(self.config.check_schedule)
        
    def run_simulation(self, simulation_id: str = None) -> SimulationResponse:
        """
        Запускает симуляцию и возвращает результат.
        
        Args:
            simulation_id: Опциональный ID симуляции. Если не указан, генерируется автоматически.
            
        Returns:
            Результат симуляции (SimulationResponse).
        """
        self.setup_workflow()
        return self.workflow.simulate(simulation_id)


def main():
    """Функция для тестового запуска симуляции."""
    simulator = Simulator()
    result = simulator.run_simulation()
    logger.info(f"Simulation completed. Time passed: {result.timestamp} seconds.")
    logger.info(f"Final balance: {simulator.workflow.balance}")


if __name__ == "__main__":
    main() 