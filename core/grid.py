import random
import pygame
from core.cell import Cell

CELL_SIZE = 70
GRID_SIZE = 8

COLORS = {
    Cell.EMPTY: (40, 40, 40),
    Cell.OBSTACLE: (100, 100, 100),
    Cell.G: (80, 160, 80),
    Cell.A: (80, 80, 180),
    Cell.C: (180, 120, 60),
}

class Grid:
    def __init__(self):
        self.size = GRID_SIZE
        self.cells = [[Cell(x, y) for y in range(self.size)] for x in range(self.size)]
        self.generate_obstacles(10)
        self.energy_lines = []  # 存储能量传播线段

    def generate_obstacles(self, n):
        positions = [(x, y) for x in range(self.size) for y in range(self.size)]
        random.shuffle(positions)

        count = 0
        for x, y in positions:
            if count >= n:
                break
            cell = self.cells[x][y]
            if cell.is_empty():
                cell.set_obstacle()
                count += 1

    def draw(self, screen):
        for x in range(self.size):
            for y in range(self.size):
                cell = self.cells[x][y]
                color = COLORS[cell.type]
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE + 40, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (70,70,70), rect, 1)

                # 左上角等级角标
                if cell.type in (Cell.G, Cell.A, Cell.C):
                    font = pygame.font.SysFont(None, 18)
                    lvl_txt = font.render(str(cell.level), True, (255, 255, 255))
                    screen.blit(lvl_txt, (x*CELL_SIZE + 4, y*CELL_SIZE + 44))

                # level display
                if cell.type in (Cell.G, Cell.A, Cell.C):
                    font2 = pygame.font.SysFont(None, 36, bold=True)
                    letter = {Cell.G: 'G', Cell.A: 'A', Cell.C: 'C'}[cell.type]
                    ttxt = font2.render(letter, True, (240, 240, 240))

                    tx = x * CELL_SIZE + CELL_SIZE // 2 - ttxt.get_width() // 2
                    ty = y * CELL_SIZE + 40 + CELL_SIZE // 2 - ttxt.get_height() // 2

                    screen.blit(ttxt, (tx, ty))

        # 绘制能量传播线
        self.draw_energy_lines(screen)

    def get_cell_by_pixel(self, px, py):
        x = px // CELL_SIZE
        y = py // CELL_SIZE
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.cells[x][y]
        return None

    def calculate_energy_lines(self):
        """计算所有 Generator 的能量传播路径"""
        self.energy_lines = []
        
        for x in range(self.size):
            for y in range(self.size):
                cell = self.cells[x][y]
                if cell.type == Cell.G:
                    # 向四个方向发射能量
                    self._propagate_energy(x, y, 0, 1)   # 下
                    self._propagate_energy(x, y, 0, -1)  # 上
                    self._propagate_energy(x, y, 1, 0)   # 右
                    self._propagate_energy(x, y, -1, 0)  # 左

    def _propagate_energy(self, start_x, start_y, dx, dy):
        """从起点向指定方向传播能量，返回传播路径的所有坐标"""
        path = [(start_x, start_y)]
        x, y = start_x + dx, start_y + dy
        
        while 0 <= x < self.size and 0 <= y < self.size:
            cell = self.cells[x][y]
            path.append((x, y))
            
            # 遇到障碍物停止
            if cell.is_obstacle():
                break
            
            x += dx
            y += dy
        
        self.energy_lines.append(path)

    def draw_energy_lines(self, screen):
        """绘制能量传播线"""
        for path in self.energy_lines:
            if len(path) < 2:
                continue
            
            # 将网格坐标转换为像素坐标
            points = []
            for x, y in path:
                px = x * CELL_SIZE + CELL_SIZE // 2
                py = y * CELL_SIZE + 40 + CELL_SIZE // 2
                points.append((px, py))
            
            # 绘制能量线（使用绿色发光效果）
            if len(points) >= 2:
                # 外发光
                pygame.draw.lines(screen, (100, 200, 100), False, points, 6)
                # 内层亮线
                pygame.draw.lines(screen, (200, 255, 200), False, points, 3)
