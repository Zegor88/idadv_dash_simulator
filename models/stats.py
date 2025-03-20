from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class LocationUpgrade:
    """Информация об улучшении локации"""
    location_id: int
    from_level: int
    to_level: int

@dataclass
class GameSession:
    """Информация об игровой сессии"""
    start_time: int  # Unix timestamp
    end_time: int    # Unix timestamp
    
    @property
    def duration_minutes(self) -> float:
        """Длительность сессии в минутах"""
        return (self.end_time - self.start_time) / 60

@dataclass
class DailyStats:
    """Статистика за игровой день"""
    day: int  # Номер дня от начала симуляции
    
    # Сессии
    sessions: List[GameSession] = field(default_factory=list)
    
    # Прогресс уровней
    level_start: int = 1
    level_end: int = 1
    
    # Улучшения локаций
    location_upgrades: List[LocationUpgrade] = field(default_factory=list)
    new_locations_opened: List[int] = field(default_factory=list)  # ID открытых локаций
    
    # Балансы на конец дня
    gold_balance: float = 0
    xp_balance: int = 0
    keys_balance: int = 0
    
    @property
    def sessions_count(self) -> int:
        """Количество входов в игру"""
        return len(self.sessions)
    
    @property
    def total_play_time(self) -> float:
        """Общее время в игре в минутах"""
        return sum(session.duration_minutes for session in self.sessions)
    
    @property
    def levels_gained(self) -> int:
        """Количество полученных уровней"""
        return self.level_end - self.level_start
    
    @property
    def upgrades_count(self) -> int:
        """Количество улучшений локаций"""
        return len(self.location_upgrades)
    
    @property
    def new_locations_count(self) -> int:
        """Количество открытых новых локаций"""
        return len(self.new_locations_opened)

@dataclass
class GameStats:
    """Статистика игры"""
    daily_stats: Dict[int, DailyStats] = field(default_factory=dict)
    
    def add_session(self, day: int, start_time: int, end_time: int) -> None:
        """Добавляет информацию о сессии"""
        if day not in self.daily_stats:
            self.daily_stats[day] = DailyStats(day=day)
        self.daily_stats[day].sessions.append(GameSession(start_time, end_time))
    
    def add_level_change(self, day: int, from_level: int, to_level: int) -> None:
        """Обновляет информацию об изменении уровня"""
        if day not in self.daily_stats:
            self.daily_stats[day] = DailyStats(day=day)
        self.daily_stats[day].level_start = min(self.daily_stats[day].level_start, from_level)
        self.daily_stats[day].level_end = max(self.daily_stats[day].level_end, to_level)
    
    def add_location_upgrade(self, day: int, location_id: int, from_level: int, to_level: int) -> None:
        """Добавляет информацию об улучшении локации"""
        if day not in self.daily_stats:
            self.daily_stats[day] = DailyStats(day=day)
        self.daily_stats[day].location_upgrades.append(
            LocationUpgrade(location_id, from_level, to_level)
        )
    
    def add_new_location(self, day: int, location_id: int) -> None:
        """Добавляет информацию об открытии новой локации"""
        if day not in self.daily_stats:
            self.daily_stats[day] = DailyStats(day=day)
        self.daily_stats[day].new_locations_opened.append(location_id)
    
    def update_balances(self, day: int, gold: float, xp: int, keys: int) -> None:
        """Обновляет балансы на конец дня"""
        if day not in self.daily_stats:
            self.daily_stats[day] = DailyStats(day=day)
        self.daily_stats[day].gold_balance = gold
        self.daily_stats[day].xp_balance = xp
        self.daily_stats[day].keys_balance = keys 