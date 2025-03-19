import logging
import uuid
import copy
from typing import Dict, List

from idadv_dash_simulator.models.config import UserLevelConfig
from idadv_dash_simulator.workflow.balance import Balance
from idadv_dash_simulator.workflow.location import Location
from idadv_dash_simulator.workflow.simulation_response import SimulationResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Workflow")

class Workflow:
    def __init__(self):
        self.locations: Dict[int, Location] = {}
        self.cooldowns: Dict[int, int] = {}
        self.user_levels: Dict[int, UserLevelConfig] = {}
        self.check_schedule: List[int] = []
        self.balance = Balance()
    
    def simulate(self, simulation_id: str = None) -> SimulationResponse:
        if not simulation_id:
            simulation_id = str(uuid.uuid4())
        
        timestamp = 0
        history = []
        
        logger.info("Starting simulation...")
        
        self.balance.earn_per_sec = self.user_levels[self.balance.user_level].gold_per_sec
        
        while any(location.available for location in self.locations.values()):
            try:
                self._do_actions(timestamp, history)
                
                # Каждый день записываем состояние симуляции в историю
                if timestamp % 86400 == 0:
                    state = {
                        "timestamp": timestamp,
                        "balance": copy.deepcopy(self.__dict__["balance"].__dict__),
                        "locations": {
                            loc_id: {
                                "current_level": loc.current_level,
                                "available": loc.available,
                                "cooldown_until": loc.cooldown_until
                            } for loc_id, loc in self.locations.items()
                        },
                        "actions": []  # Будем добавлять сюда действия, которые произошли в этот период
                    }
                    history.append(state)
                
            except Exception as e:
                logger.error(f"Error while doing actions on timestamp {timestamp}", exc_info=e)
            
            timestamp += 1
        
        logger.info(f"Finished simulation.\nTime passed: {self._timestamp_to_human_readable(timestamp)}\nBalances:\n{self.balance}")
        
        response = SimulationResponse(simulation_id, timestamp)
        response.history = history
        return response
    
    def _do_actions(self, t: int, history: List[Dict] = None) -> None:
        # Check the game on specified timestamps (5 times per day with 8-hour sleep interval)
        if t % 86400 in self.check_schedule:
            # Запись действий для истории
            current_day = t // 86400
            current_history = None
            if history and current_day < len(history):
                current_history = history[current_day]
            
            # Step 1. Try to upgrade locations
            available_locations = {idx: loc for idx, loc in self.locations.items() 
                                if loc.available and loc.cooldown_until <= t}
            
            # Сортируем локации по индексу для последовательного улучшения
            sorted_locations = sorted(available_locations.items())
            
            # Проверяем, что предыдущие локации полностью улучшены
            for index, location in sorted_locations:
                # Проверяем все предыдущие локации
                previous_locations_maxed = True
                for prev_idx, prev_loc in self.locations.items():
                    if prev_idx < index and prev_loc.available:
                        # Если предыдущая локация не улучшена до максимума, пропускаем текущую
                        previous_locations_maxed = False
                        break
                
                if not previous_locations_maxed:
                    continue
                
                # Skip locations that require higher user level
                if self.balance.user_level < location.min_character_level:
                    continue
                
                # Get cost of the location upgrade
                cost = location.get_upgrade_cost()
                
                if self.balance.gold >= cost:
                    # Upgrade location
                    logger.info(f"Upgrading location {index}. Timestamp: {self._timestamp_to_human_readable(t)}, "
                                f"cost: {cost}, gold balance: {self.balance.gold}, "
                                f"current level: {location.current_level}, xp level: {self.balance.xp}")
                    
                    reward_xp = location.get_upgrade_xp_reward()
                    reward_keys = location.get_upgrade_keys_reward()
                    cooldown = self.cooldowns[location.current_level + 1]
                    
                    # Добавляем запись о действии в историю
                    if current_history is not None:
                        action = {
                            "type": "location_upgrade",
                            "location_id": index,
                            "timestamp": t,
                            "cost": cost,
                            "reward_xp": reward_xp,
                            "reward_keys": reward_keys,
                            "new_level": location.current_level + 1
                        }
                        current_history["actions"].append(action)
                    
                    # Charge the cost from the balance
                    self.balance.gold -= cost
                    
                    # Add experience
                    self.balance.xp += reward_xp
                    
                    # Add keys
                    self.balance.keys += reward_keys
                    
                    # Update location
                    location.current_level += 1
                    
                    # If this was the last upgrade, deactivate location
                    if location.current_level >= max(location.levels.keys()):
                        location.available = False
                    
                    # Set the cooldown
                    location.cooldown_until = t + cooldown
                    
                    logger.info(f"Location {index} upgraded. Cooldown until: {location.cooldown_until}, "
                                f"gold balance: {self.balance.gold}, xp level: {self.balance.xp}")
                    
                    # Try to upgrade character
                    self._try_upgrade_character(t, current_history)
            
            # Step 2. Try to perform all tasks
            # TODO: Implement tasks
            
            # Step 3. Try to buy NFTs
            # TODO: Implement NFTs
        
        # Step 4. Accrue gold
        self.balance.gold += self.balance.earn_per_sec
    
    def _try_upgrade_character(self, t: int, current_history: Dict = None) -> None:
        cur_level = self.balance.user_level
        if cur_level >= max(self.user_levels.keys()):
            return
        
        # TODO: Add checks for level numbers validity
        required_xp = self.user_levels[cur_level + 1].xp_required
        
        # Upgrade as many times as needed
        while self.balance.xp >= required_xp:
            logger.info(f"Upgrading character. Timestamp: {self._timestamp_to_human_readable(t)}, "
                        f"current level: {cur_level}, earn per sec: {self.balance.earn_per_sec}")
            
            # Добавляем запись о повышении уровня в историю
            if current_history is not None:
                action = {
                    "type": "level_up",
                    "timestamp": t,
                    "old_level": self.balance.user_level,
                    "new_level": self.balance.user_level + 1,
                    "new_earn_per_sec": self.user_levels[self.balance.user_level + 1].gold_per_sec
                }
                current_history["actions"].append(action)
            
            self.balance.user_level += 1
            self.balance.earn_per_sec = self.user_levels[self.balance.user_level].gold_per_sec
            self.balance.keys += self.user_levels[self.balance.user_level].keys_reward
            
            logger.info(f"Character upgraded. New level: {self.balance.user_level}, "
                        f"earn per sec: {self.balance.earn_per_sec}")
            
            if self.balance.user_level < max(self.user_levels.keys()):
                required_xp = self.user_levels[self.balance.user_level + 1].xp_required
            else:
                return
    
    @staticmethod
    def _timestamp_to_human_readable(timestamp: int) -> str:
        weeks = timestamp // 604800
        days = (timestamp % 604800) // 86400
        hours = ((timestamp % 604800) % 86400) // 3600
        minutes = (((timestamp % 604800) % 86400) % 3600) // 60
        seconds = (((timestamp % 604800) % 86400) % 3600) % 60
        
        result = []
        if weeks > 0:
            result.append(f"{weeks}W")
        if days > 0:
            result.append(f"{days}D")
        
        result.append(f"{hours}:{minutes}:{seconds}")
        
        return " ".join(result) 