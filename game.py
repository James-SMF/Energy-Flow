import pygame
from core.grid import Grid
from core.cell import Cell

CELL = 70
HUD_H = 40
WIDTH = 8 * CELL
HEIGHT = 8 * CELL + HUD_H * 3

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.grid = Grid()
        self.action_points = 20
        self.score = 0
        self.selected_tower_type = Cell.G
        self.last_click_time = 0
        self.double_click_time_threshold = 300

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(60)
            running = self.handle_events()
            self.render()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # tower select
                if event.key == pygame.K_1:
                    self.selected_tower_type = Cell.G
                elif event.key == pygame.K_2:
                    self.selected_tower_type = Cell.A
                elif event.key == pygame.K_3:
                    self.selected_tower_type = Cell.C
                # upgrade via SPACE
                elif event.key == pygame.K_SPACE:
                    mx, my = mouse_pos
                    cell = self.grid.get_cell_by_pixel(mx, my-40)
                    if cell and cell.type in (Cell.G, Cell.A, Cell.C):
                        cell.upgrade()
                        if self.action_points > 0:
                            self.action_points -= 1


            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.action_points <= 0:
                    return True

                if event.button == 1:
                    now = pygame.time.get_ticks()
                    delta = now - self.last_click_time
                    self.last_click_time = now

                    # double click - remove
                    if delta < self.double_click_time_threshold:
                        self.handle_remove(event.pos)
                    else:
                        # single click - build only
                        self.handle_action(event.pos)
        return True

    def handle_action(self, pos):
        cell = self.grid.get_cell_by_pixel(pos[0], pos[1]-40)
        if not cell or cell.is_obstacle():
            return

        # Move system
        if cell.is_empty():
            cell.set_tower(self.selected_tower_type)
            self.action_points -= 1
            # 更新能量传播线
            self.grid.calculate_energy_lines()


    def handle_remove(self, pos):
        cell = self.grid.get_cell_by_pixel(pos[0], pos[1] - 40)
        if not cell:
            return

        # only remove tower
        if cell.type in (Cell.G, Cell.A, Cell.C):
            cell.type = Cell.EMPTY
            cell.level = 1
            if self.action_points > 0:
                self.action_points -= 1
            # 更新能量传播线
            self.grid.calculate_energy_lines()

    def render(self):
        self.screen.fill((20,20,20))
        self.grid.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self):
        font = pygame.font.SysFont(None, 26)
        pygame.draw.rect(self.screen, (30,30,30), (0,0, WIDTH, HUD_H))

        name_map = {Cell.G: "Generator", Cell.A: "Amplifier", Cell.C: "Collector"}
        t = self.selected_tower_type
        txt = font.render(f"action points: {self.action_points} | selected: {name_map[t]}", True, (220,220,220))
        self.screen.blit(txt, (10,8))
