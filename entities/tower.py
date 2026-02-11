# entities/tower.py

from entities.types import TowerType

class Tower:
    def __init__(self, tower_type: str):
        if tower_type not in TowerType.ALL:
            raise ValueError(f"Invalid tower type: {tower_type}")

        self.type = tower_type
        self.level = 1

    def upgrade(self):
        self.level += 1

    def __repr__(self):
        return f"Tower(type={self.type}, level={self.level})"
