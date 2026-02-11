class Cell:
    EMPTY = 0
    OBSTACLE = -1
    G = 1
    A = 2
    C = 3
    MAX_LEVEL = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = Cell.EMPTY
        self.level = 1

    def is_empty(self):
        return self.type == Cell.EMPTY

    def is_obstacle(self):
        return self.type == Cell.OBSTACLE

    def set_obstacle(self):
        self.type = Cell.OBSTACLE

    def set_tower(self, t):
        self.type = t
        self.level = 1

    def upgrade(self):
        if self.type in (Cell.G, Cell.A, Cell.C) and self.level < self.MAX_LEVEL:
            self.level += 1

    def get_base_energy(self):
        """获取 G 塔的基础能量"""
        if self.type != Cell.G:
            return 0
        
        level = self.level
        if level <= 5:
            return 5 + (level - 1) * 5  # 5, 10, 15, 20, 25
        elif level <= 10:
            return 25 + (level - 5) * 3  # 28, 31, 34, 37, 40
        else:
            return 40 + (level - 10) * 1.5  # 41.5, 43, ..., 55

    def get_amplifier_multiplier(self):
        """获取 A 塔的放大倍数"""
        if self.type != Cell.A:
            return 1.0
        
        level = self.level
        if level <= 5:
            return 1.2 + (level - 1) * 0.2  # 1.2, 1.4, 1.6, 1.8, 2.0
        elif level <= 10:
            return 2.0 + (level - 5) * 0.15  # 2.15, 2.3, 2.45, 2.6, 2.75
        else:
            return 2.75 + (level - 10) * 0.08  # 2.83, 2.91, ..., 3.47

    def get_collector_efficiency(self):
        """获取 C 塔的收集效率（0-1之间的值）"""
        if self.type != Cell.C:
            return 0.0
        
        return min(1.5, 0.6 + (self.level - 1) * 0.05)  # 60%, 65%, ..., 150%
