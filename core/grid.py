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
                # 检查上下左右是否有障碍物
                has_adjacent = False
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.cells[nx][ny].is_obstacle():
                            has_adjacent = True
                            break
                
                # 如果没有相邻障碍物，则生成
                if not has_adjacent:
                    cell.set_obstacle()
                    count += 1

    def draw(self, screen, hud_offset=60):
        for x in range(self.size):
            for y in range(self.size):
                cell = self.cells[x][y]
                color = COLORS[cell.type]
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE + hud_offset, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (70,70,70), rect, 1)

                # 左上角等级角标
                if cell.type in (Cell.G, Cell.A, Cell.C):
                    font = pygame.font.SysFont(None, 18)
                    lvl_txt = font.render(str(cell.level), True, (255, 255, 255))
                    screen.blit(lvl_txt, (x*CELL_SIZE + 4, y*CELL_SIZE + hud_offset + 4))

                # level display
                if cell.type in (Cell.G, Cell.A, Cell.C):
                    font2 = pygame.font.SysFont(None, 36, bold=True)
                    letter = {Cell.G: 'G', Cell.A: 'A', Cell.C: 'C'}[cell.type]
                    ttxt = font2.render(letter, True, (240, 240, 240))

                    tx = x * CELL_SIZE + CELL_SIZE // 2 - ttxt.get_width() // 2
                    ty = y * CELL_SIZE + hud_offset + CELL_SIZE // 2 - ttxt.get_height() // 2

                    screen.blit(ttxt, (tx, ty))

        # 绘制能量传播线
        self.draw_energy_lines(screen, hud_offset)

    def get_cell_by_pixel(self, px, py):
        x = px // CELL_SIZE
        y = py // CELL_SIZE
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.cells[x][y]
        return None

    def calculate_energy_lines(self):
        """计算所有 Generator 的能量传播路径，并计算得分"""
        self.energy_lines = []  # 存储路径段，每段为 (路径坐标点列表, 能量值)
        collected_energy = 0  # 收集的能量
        wasted_energy = 0  # 浪费的能量
        max_single_waste = 0  # 最大单次损失
        total_output = 0  # 总输出能量

        for x in range(self.size):
            for y in range(self.size):
                cell = self.cells[x][y]
                if cell.type == Cell.G:
                    base_energy = cell.get_base_energy()
                    total_output += base_energy * 4  # G向四个方向发射

                    collected, wasted, segments, single_waste = self._propagate_energy(x, y, 0, 1, base_energy)   # 下
                    collected_energy += collected
                    wasted_energy += wasted
                    max_single_waste = max(max_single_waste, single_waste)
                    self.energy_lines.extend(segments)

                    collected, wasted, segments, single_waste = self._propagate_energy(x, y, 0, -1, base_energy)  # 上
                    collected_energy += collected
                    wasted_energy += wasted
                    max_single_waste = max(max_single_waste, single_waste)
                    self.energy_lines.extend(segments)

                    collected, wasted, segments, single_waste = self._propagate_energy(x, y, 1, 0, base_energy)   # 右
                    collected_energy += collected
                    wasted_energy += wasted
                    max_single_waste = max(max_single_waste, single_waste)
                    self.energy_lines.extend(segments)

                    collected, wasted, segments, single_waste = self._propagate_energy(x, y, -1, 0, base_energy)  # 左
                    collected_energy += collected
                    wasted_energy += wasted
                    max_single_waste = max(max_single_waste, single_waste)
                    self.energy_lines.extend(segments)

        return (collected_energy, wasted_energy, max_single_waste, total_output)

    def _propagate_energy(self, start_x, start_y, dx, dy, base_energy):
        """
        从起点向指定方向传播能量
        返回: (收集的能量值, 浪费的能量值, 路径段列表, 最大单次损失)
        每个路径段为 (坐标点列表, 能量值)
        """
        segments = []
        collected_energy = 0
        wasted_energy = 0
        current_energy = base_energy
        max_single_waste = 0  # 记录最大单次损失
        
        current_segment = [(start_x, start_y)]
        x, y = start_x + dx, start_y + dy
        
        while 0 <= x < self.size and 0 <= y < self.size:
            cell = self.cells[x][y]
            
            # 遇到障碍物，添加边缘点后停止，能量浪费
            if cell.is_obstacle():
                # 计算障碍物边缘的坐标（相对于网格单元的边缘）
                edge_x = x - dx * 0.5
                edge_y = y - dy * 0.5
                current_segment.append((edge_x, edge_y))
                # 能量没有被收集，算作浪费
                wasted_energy += current_energy
                max_single_waste = max(max_single_waste, current_energy)
                break
            
            # 将当前格子加入当前段
            current_segment.append((x, y))
            
            # 遇到其他塔
            if cell.type == Cell.A:
                # 放大能量为 n 倍（使用塔的放大倍数），可穿透
                current_energy *= cell.get_amplifier_multiplier()
                # 保存当前段（放大前的能量）
                segments.append((current_segment, current_energy / cell.get_amplifier_multiplier()))
                # 开始新的一段（放大后的能量）
                current_segment = [(x, y)]
            elif cell.type == Cell.C:
                # 收集能量，使用收集效率
                efficiency = cell.get_collector_efficiency()
                collected_energy += current_energy * efficiency
                # 如果效率小于100%，能量穿透继续传播
                if efficiency < 1.0:
                    # 保存当前段（穿透前的能量）
                    segments.append((current_segment, current_energy))
                    # 能量穿透，剩余能量继续传播
                    current_energy = current_energy * (1.0 - efficiency)
                    # 开始新的一段
                    current_segment = [(x, y)]
                else:
                    # 效率为100%或更高，能量被完全收集
                    segments.append((current_segment, current_energy))
                    break
            elif cell.type == Cell.G:
                # 遇到另一个 Generator，停止传播，能量不算浪费（被另一个G吸收）
                # 保存当前段
                segments.append((current_segment, current_energy))
                break
            
            x += dx
            y += dy
        
        # 检查是否到达墙壁（边界），能量浪费
        if not (0 <= x < self.size and 0 <= y < self.size):
            # 添加墙壁边缘点
            edge_x = x - dx * 0.5
            edge_y = y - dy * 0.5
            current_segment.append((edge_x, edge_y))
            # 能量没有被收集，算作浪费
            wasted_energy += current_energy
            max_single_waste = max(max_single_waste, current_energy)

        # 如果循环正常结束，保存最后一段
        if current_segment and not (segments and segments[-1][0] == current_segment and segments[-1][1] == current_energy):
            segments.append((current_segment, current_energy))

        return (collected_energy, wasted_energy, segments, max_single_waste)

    def draw_energy_lines(self, screen, hud_offset=60):
        """绘制能量传播线，根据能量值动态调整粗细"""
        for path, energy in self.energy_lines:
            if len(path) < 2:
                continue

            # 将网格坐标转换为像素坐标
            points = []
            for x, y in path:
                px = x * CELL_SIZE + CELL_SIZE // 2
                py = y * CELL_SIZE + hud_offset + CELL_SIZE // 2
                points.append((px, py))

            # 根据能量值计算线宽（能量越大，线条越粗）
            # 能量范围大致在 30-600 之间（G的100-200经过A放大后可达600+）
            energy_factor = min(3.0, max(0.4, energy / 80.0))  # 归一化因子 0.4-3.0，变化更明显
            outer_width = int(10 * energy_factor)
            mid_width = int(5 * energy_factor)
            inner_width = int(2 * energy_factor)
            # 确保至少有最小宽度
            outer_width = max(outer_width, 4)
            mid_width = max(mid_width, 2)
            inner_width = max(inner_width, 1)

            # 绘制能量线（使用渐变绿色发光效果）
            if len(points) >= 2:
                # 外发光（绿色）
                pygame.draw.lines(screen, (50, 180, 50), False, points, outer_width)
                # 中层（亮绿）
                pygame.draw.lines(screen, (100, 255, 100), False, points, mid_width)
                # 内层（高亮白）
                pygame.draw.lines(screen, (220, 255, 220), False, points, inner_width)

                # 在线段端点绘制能量光点（跳过边缘点）
                for i, (px, py) in enumerate(points):
                    # 检查是否是边缘点（坐标不是整数）
                    orig_x, orig_y = path[i]
                    if orig_x == int(orig_x) and orig_y == int(orig_y):
                        radius = max(3, int(5 * energy_factor))
                        pygame.draw.circle(screen, (150, 255, 150), (px, py), radius)
                        pygame.draw.circle(screen, (255, 255, 255), (px, py), max(1, radius // 2))
