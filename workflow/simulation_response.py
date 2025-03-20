from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from uuid import uuid4

@dataclass
class SimulationResponse:
    simulation_id: str = ""
    timestamp: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    stop_reason: str = ""  # Причина остановки симуляции
    
    def __post_init__(self):
        if not self.simulation_id:
            self.simulation_id = str(uuid4()) 