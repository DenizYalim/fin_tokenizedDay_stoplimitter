import random

class forecasterAlgorithm:
    def __init__(self, chance_percent: float): 
        self.chance = chance_percent / 100.0

    def guess(self) -> bool:
        return random.random() < self.chance

