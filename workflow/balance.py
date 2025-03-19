from dataclasses import dataclass

@dataclass
class Balance:
    gold: float = 0.0
    xp: int = 0
    keys: int = 0
    user_level: int = 1
    earn_per_sec: float = 0.0
    
    def __str__(self) -> str:
        return (f"Balance(gold={self.gold:.2f}, xp={self.xp}, keys={self.keys}, "
                f"user_level={self.user_level}, earn_per_sec={self.earn_per_sec:.2f})") 