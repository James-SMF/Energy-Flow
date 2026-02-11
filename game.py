import pygame
import json
import os
from datetime import datetime
from core.grid import Grid
from core.cell import Cell

CELL = 70
HUD_H = 30
HUD_LINES = 2
WIDTH = 8 * CELL
HEIGHT = 8 * CELL + HUD_H * HUD_LINES
LEADERBOARD_FILE = ".codebuddy/leaderboard.json"

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.grid = Grid()
        self.action_points = 50
        self.collected_score = 0  # 收集的能量得分
        self.penalty_score = 0  # 惩罚得分
        self.final_score = 0  # 综合得分
        self.selected_tower_type = Cell.G
        self.last_click_time = 0
        self.double_click_time_threshold = 300
        self.game_state = "playing"  # playing, name_input, leaderboard
        self.player_name = ""
        self.max_name_length = 10
        self.cached_leaderboard = None  # 缓存排行榜数据
        self.needs_redraw = True  # 是否需要重绘
        
        # 初始化中文字体
        self.init_chinese_font()

    def init_chinese_font(self):
        """初始化中文字体"""
        # 尝试常见的中文字体
        font_names = [
            "simhei",  # 黑体
            "simsun",  # 宋体
            "microsoftyahei",  # 微软雅黑
            "pingfangsc",  # 苹方（macOS）
            "heiti",  # 黑体（macOS）
            "stheitilight",  # 华文黑体（macOS）
            "arialunicode",  # Arial Unicode
        ]
        
        # 在 macOS 上使用系统字体
        import platform
        if platform.system() == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/Arial Unicode.ttf",
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.chinese_font = pygame.font.Font(font_path, 24)
                    self.chinese_font_title = pygame.font.Font(font_path, 40)
                    return
        
        # 尝试系统字体
        for font_name in font_names:
            try:
                self.chinese_font = pygame.font.SysFont(font_name, 24)
                self.chinese_font_title = pygame.font.SysFont(font_name, 40)
                # 测试是否能显示中文
                test = self.chinese_font.render("测试", True, (255, 255, 255))
                return
            except:
                continue
        
        # 如果都失败，使用默认字体
        self.chinese_font = pygame.font.SysFont(None, 24)
        self.chinese_font_title = pygame.font.SysFont(None, 40)

    def load_leaderboard(self):
        """加载排行榜数据"""
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_score(self, name):
        """保存分数到排行榜"""
        leaderboard = self.load_leaderboard()
        entry = {
            "name": name,
            "score": self.final_score,
            "date": datetime.now().strftime("%Y-%m-%d")  # 只显示年月日
        }
        leaderboard.append(entry)
        # 按分数降序排序，保留前10
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        leaderboard = leaderboard[:10]
        # 确保目录存在
        os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=2)

    def draw_name_input(self):
        """绘制名字输入弹窗"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 弹窗背景
        dialog_w, dialog_h = 400, 320
        dialog_x = (WIDTH - dialog_w) // 2
        dialog_y = (HEIGHT - dialog_h) // 2
        pygame.draw.rect(self.screen, (50, 50, 60), (dialog_x, dialog_y, dialog_w, dialog_h), border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 120), (dialog_x, dialog_y, dialog_w, dialog_h), 2, border_radius=10)
        
        # 标题
        title = self.chinese_font_title.render("游戏结束!", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, dialog_y + 50))
        self.screen.blit(title, title_rect)
        
        # 分数显示
        score_text = self.chinese_font.render(f"最终得分: {self.final_score:.2f}", True, (255, 255, 100))
        score_rect = score_text.get_rect(center=(WIDTH // 2, dialog_y + 90))
        self.screen.blit(score_text, score_rect)
        
        # 输入框
        input_w, input_h = 300, 40
        input_x = (WIDTH - input_w) // 2
        input_y = dialog_y + 130
        pygame.draw.rect(self.screen, (30, 30, 35), (input_x, input_y, input_w, input_h), border_radius=5)
        pygame.draw.rect(self.screen, (150, 150, 170), (input_x, input_y, input_w, input_h), 2, border_radius=5)
        
        # 输入的文字
        name_surface = self.chinese_font.render(self.player_name, True, (255, 255, 255))
        self.screen.blit(name_surface, (input_x + 10, input_y + 8))
        
        # 光标（闪烁效果）
        import time
        cursor_visible = int(time.time() * 2) % 2 == 0
        if cursor_visible:
            cursor_x = input_x + 10 + name_surface.get_width()
            cursor_y = input_y + 8
            cursor_h = self.chinese_font.get_height()
            pygame.draw.line(self.screen, (255, 255, 255), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)
        
        # 提示文字
        hint_font = self.chinese_font
        hint = hint_font.render(f"请输入名字 (最多{self.max_name_length}字)", True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(WIDTH // 2, input_y + input_h + 20))
        self.screen.blit(hint, hint_rect)
        
        # 确认按钮
        btn_w, btn_h = 120, 40
        btn_x = (WIDTH - btn_w) // 2
        btn_y = dialog_y + dialog_h - 60
        pygame.draw.rect(self.screen, (80, 160, 80), (btn_x, btn_y, btn_w, btn_h), border_radius=5)
        btn_text = self.chinese_font.render("确认", True, (255, 255, 255))
        btn_rect = btn_text.get_rect(center=(btn_x + btn_w // 2, btn_y + btn_h // 2))
        self.screen.blit(btn_text, btn_rect)
        
        return (btn_x, btn_y, btn_w, btn_h)

    def draw_leaderboard(self):
        """绘制排行榜弹窗"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 弹窗窗背景（增大宽度）
        dialog_w, dialog_h = 550, 450
        dialog_x = (WIDTH - dialog_w) // 2
        dialog_y = (HEIGHT - dialog_h) // 2
        pygame.draw.rect(self.screen, (50, 50, 60), (dialog_x, dialog_y, dialog_w, dialog_h), border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 120), (dialog_x, dialog_y, dialog_w, dialog_h), 2, border_radius=10)
        
        # 标题
        title = self.chinese_font_title.render("排行榜", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, dialog_y + 40))
        self.screen.blit(title, title_rect)
        
        # 表头（使用中文字体，稍微增大）
        headers = ["排名", "名字", "得分", "日期"]
        header_x = [dialog_x + 30, dialog_x + 90, dialog_x + 250, dialog_x + 370]
        for i, header in enumerate(headers):
            h = self.chinese_font.render(header, True, (200, 200, 200))
            self.screen.blit(h, (header_x[i], dialog_y + 80))
        
        # 分隔线
        pygame.draw.line(self.screen, (100, 100, 120), (dialog_x + 20, dialog_y + 110), (dialog_x + dialog_w - 20, dialog_y + 110), 2)
        
        # 排行榜数据（使用缓存，使用中文字体）
        leaderboard = self.cached_leaderboard if self.cached_leaderboard is not None else []
        start_y = dialog_y + 130
        row_height = 28
        
        for i, entry in enumerate(leaderboard[:10]):
            y = start_y + i * row_height
            if y > dialog_y + dialog_h - 80:
                break
            
            # 排名颜色
            if i == 0:
                rank_color = (255, 215, 0)  # 金
            elif i == 1:
                rank_color = (192, 192, 192)  # 银
            elif i == 2:
                rank_color = (205, 127, 50)  # 铜
            else:
                rank_color = (220, 220, 220)
            
            rank = self.chinese_font.render(str(i + 1), True, rank_color)
            name = self.chinese_font.render(entry["name"][:10], True, (255, 255, 255))
            score = self.chinese_font.render(f"{entry['score']:.2f}", True, (255, 255, 100))
            date = self.chinese_font.render(entry["date"], True, (180, 180, 180))
            
            self.screen.blit(rank, (header_x[0], y))
            self.screen.blit(name, (header_x[1], y))
            self.screen.blit(score, (header_x[2], y))
            self.screen.blit(date, (header_x[3], y))
        
        # 按钮
        btn_w, btn_h = 120, 40
        btn_y = dialog_y + dialog_h - 60
        btn1_x = dialog_x + (dialog_w - btn_w * 2 - 20) // 2
        btn2_x = btn1_x + btn_w + 20
        
        # 再玩一局按钮
        pygame.draw.rect(self.screen, (80, 160, 80), (btn1_x, btn_y, btn_w, btn_h), border_radius=5)
        btn1_text = self.chinese_font.render("再玩一局", True, (255, 255, 255))
        btn1_rect = btn1_text.get_rect(center=(btn1_x + btn_w // 2, btn_y + btn_h // 2))
        self.screen.blit(btn1_text, btn1_rect)
        
        # 结束游戏按钮
        pygame.draw.rect(self.screen, (180, 80, 80), (btn2_x, btn_y, btn_w, btn_h), border_radius=5)
        btn2_text = self.chinese_font.render("结束游戏", True, (255, 255, 255))
        btn2_rect = btn2_text.get_rect(center=(btn2_x + btn_w // 2, btn_y + btn_h // 2))
        self.screen.blit(btn2_text, btn2_rect)

    def handle_name_input(self, event):
        """处理名字输入"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # 确认输入
                if self.player_name:
                    self.save_score(self.player_name)
                    self.cached_leaderboard = self.load_leaderboard()  # 缓存排行榜
                    self.game_state = "leaderboard"
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
                self.needs_redraw = True
            elif len(self.player_name) < self.max_name_length:
                # 支持中英文+数字
                char = event.unicode
                # 只接受中文字符、英文和数字，过滤掉拼音字母
                if char and (char.isalnum() or '\u4e00' <= char <= '\u9fff'):
                    # 英文字母只接受单字节（避免中文输入法的拼音）
                    if char.isalpha() and len(char.encode('utf-8')) > 1 and not ('\u4e00' <= char <= '\u9fff'):
                        # 多字节但不是中文，跳过（可能是拼音）
                        pass
                    else:
                        self.player_name += char
                        self.needs_redraw = True

    def handle_leaderboard_click(self, pos):
        """处理排行榜按钮点击"""
        # 重新计算按钮位置（与 draw_leaderboard 一致）
        dialog_w, dialog_h = 550, 450
        dialog_x = (WIDTH - dialog_w) // 2
        dialog_y = (HEIGHT - dialog_h) // 2
        btn_w, btn_h = 120, 40
        btn_y = dialog_y + dialog_h - 60
        btn1_x = dialog_x + (dialog_w - btn_w * 2 - 20) // 2
        btn2_x = btn1_x + btn_w + 20
        
        x, y = pos
        
        if btn1_x <= x <= btn1_x + btn_w and btn_y <= y <= btn_y + btn_h:
            # 再玩一局
            self.__init__(self.screen)
            self.needs_redraw = True
        elif btn2_x <= x <= btn2_x + btn_w and btn_y <= y <= btn_y + btn_h:
            # 结束游戏
            return False
        return True

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(60)
            
            if self.game_state == "playing":
                running = self.handle_events()
                if self.action_points <= 0 and self.game_state == "playing":
                    self.game_state = "name_input"
                    self.needs_redraw = True
                self.render()
            elif self.game_state == "name_input":
                # 名字输入状态需要持续渲染（光标闪烁）
                btn_rect = None
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN:
                        old_name = self.player_name
                        self.handle_name_input(event)
                        if self.player_name != old_name or self.game_state == "leaderboard":
                            self.needs_redraw = True
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # 检查是否点击确认按钮
                        btn_rect = self.draw_name_input()
                        if btn_rect:
                            x, y = event.pos
                            if btn_rect[0] <= x <= btn_rect[0] + btn_rect[2] and btn_rect[1] <= y <= btn_rect[1] + btn_rect[3]:
                                if self.player_name:
                                    self.save_score(self.player_name)
                                    self.cached_leaderboard = self.load_leaderboard()
                                    self.game_state = "leaderboard"
                                    self.needs_redraw = True
                
                # 持续渲染以显示光标闪烁
                self.screen.fill((20, 20, 20))
                self.grid.draw(self.screen, HUD_H * HUD_LINES)
                self.draw_name_input()
                pygame.display.flip()
            elif self.game_state == "leaderboard":
                # 排行榜状态只在需要重绘时渲染
                if self.needs_redraw:
                    self.screen.fill((20, 20, 20))
                    self.grid.draw(self.screen, HUD_H * HUD_LINES)
                    self.draw_leaderboard()
                    pygame.display.flip()
                    self.needs_redraw = False
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if not self.handle_leaderboard_click(event.pos):
                            return False

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
                    cell = self.grid.get_cell_by_pixel(mx, my - HUD_H * HUD_LINES)
                    if cell and cell.type in (Cell.G, Cell.A, Cell.C):
                        old_level = cell.level
                        cell.upgrade()
                        if cell.level != old_level:  # 确实升级了
                            if self.action_points > 0:
                                self.action_points -= 1
                            # 重新计算能量传播并更新得分
                            self.update_scores()


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
        cell = self.grid.get_cell_by_pixel(pos[0], pos[1] - HUD_H * HUD_LINES)
        if not cell or cell.is_obstacle():
            return

        # Move system
        if cell.is_empty():
            cell.set_tower(self.selected_tower_type)
            self.action_points -= 1
            # 计算能量传播并更新得分
            self.update_scores()


    def update_scores(self):
        """更新各项得分"""
        collected, wasted = self.grid.calculate_energy_lines()
        self.collected_score = collected
        self.penalty_score = wasted * 0.2  # 惩罚系数 0.2
        self.final_score = self.collected_score - self.penalty_score

    def handle_remove(self, pos):
        cell = self.grid.get_cell_by_pixel(pos[0], pos[1] - HUD_H * HUD_LINES)
        if not cell:
            return

        # only remove tower
        if cell.type in (Cell.G, Cell.A, Cell.C):
            cell.type = Cell.EMPTY
            cell.level = 1
            if self.action_points > 0:
                self.action_points -= 1
            # 重新计算能量传播并更新得分
            self.update_scores()

    def render(self):
        self.screen.fill((20,20,20))
        self.grid.draw(self.screen, HUD_H * HUD_LINES)
        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self):
        font = pygame.font.SysFont(None, 24)
        
        # 第一行：AP 和选中的塔
        pygame.draw.rect(self.screen, (30,30,30), (0, 0, WIDTH, HUD_H))
        name_map = {Cell.G: "Generator", Cell.A: "Amplifier", Cell.C: "Collector"}
        color_map = {Cell.G: (80, 160, 80), Cell.A: (80, 80, 180), Cell.C: (180, 120, 60)}
        t = self.selected_tower_type
        
        base_txt = font.render(f"AP: {self.action_points} | selected: ", True, (220,220,220))
        self.screen.blit(base_txt, (10, 5))
        
        offset_x = base_txt.get_width() + 10
        name_txt = font.render(name_map[t], True, color_map[t])
        self.screen.blit(name_txt, (offset_x, 5))
        
        # 第二行：得分信息
        pygame.draw.rect(self.screen, (25,25,25), (0, HUD_H, WIDTH, HUD_H))
        
        offset_x = 10
        collected_txt = font.render(f"collected: {self.collected_score:.2f}", True, (100, 255, 100))
        self.screen.blit(collected_txt, (offset_x, HUD_H + 5))
        
        offset_x += collected_txt.get_width() + 15
        penalty_txt = font.render(f"penalty: -{self.penalty_score:.2f}", True, (255, 100, 100))
        self.screen.blit(penalty_txt, (offset_x, HUD_H + 5))
        
        offset_x += penalty_txt.get_width() + 15
        final_txt = font.render(f"final: {self.final_score:.2f}", True, (255, 255, 100))
        self.screen.blit(final_txt, (offset_x, HUD_H + 5))
