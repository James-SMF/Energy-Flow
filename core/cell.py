class Cell:
    EMPTY = 0
    OBSTACLE = -1
    G = 1
    A = 2
    C = 3

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
        if self.type in (Cell.G, Cell.A, Cell.C):
            self.level += 1
