class Cell:
    EMPTY = 0
    OBSTACLE = -1
    G = 1
    A = 2
    C = 3
    MAX_LEVEL = 5

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

        # 1级: 100, 2级: 125, 3级: 150, 4级: 175, 5级: 200
        return 100 + (self.level - 1) * 25

    def get_amplifier_multiplier(self):
        """获取 A 塔的放大倍数"""
        if self.type != Cell.A:
            return 1.0

        # 1级: 1.25, 2级: 1.45, 3级: 1.6, 4级: 1.72, 5级: 1.82
        multipliers = {1: 1.25, 2: 1.45, 3: 1.6, 4: 1.72, 5: 1.82}
        return multipliers.get(self.level, 1.25)

    def get_collector_efficiency(self):
        """获取 C 塔的收集效率（0-1之间的值）"""
        if self.type != Cell.C:
            return 0.0

        # 1级: 60%, 2级: 72%, 3级: 81%, 4级: 87%, 5级: 91%
        efficiencies = {1: 0.60, 2: 0.72, 3: 0.81, 4: 0.87, 5: 0.91}
        return efficiencies.get(self.level, 0.60)
