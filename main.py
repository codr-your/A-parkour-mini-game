import math
import pygame
import sys
# 这是一个用 Pygame 做的横版跳跃小游戏（类似超级马里奥），有选关界面、3 个关卡、金币、敌人、跳跃这些元素
# ① 导入库 & 初始化（第1~31行）
# ② 图片加载工具 & 常量（第34~49行）
# ③ Player 类（第52~94行）—— 描述"玩家"这个角色
# ④ Game 类（第96~513行）—— 整个游戏的大脑
# ⑤ 关卡数据（第516~628行）—— 3个关卡的地图信息
# ⑥ main 函数 & 程序入口（第631~652行）—— 程序启动点

pygame.init()

WIDTH, HEIGHT = 960, 540   # 游戏窗口大小，宽960，高540，单位是像素
screen = pygame.display.set_mode((WIDTH, HEIGHT))#创建窗口的函数,参数是一个元组，里面放宽和高，返回值screen是一个Surface对象，表示窗口的画布
pygame.display.set_caption("Mini Mario Adventure")
clock = pygame.time.Clock()#创建一个时钟对象，用于控制游戏的帧率
FPS = 60#游戏的帧率，单位是帧/秒,Python社区约定，全大写的变量名不应该被改变

# 颜色常量
WHITE = (255, 255, 255)  #y颜色用rgb表示，这是白色
BLACK = (0, 0, 0)#黑色
RED = (210, 70, 70)#偏暗的红色
YELLOW = (255, 220, 80)#黄色
BLUE = (90, 150, 220)#蓝色
SKY_TOP = (140, 210, 255)#天空顶部颜色
DARK_BLUE = (28, 50, 110)#深蓝色
GOLD = (255, 192, 72)#金色
PURPLE = (138, 110, 255)#紫色
MINT = (111, 216, 156)
BROWN = (98, 74, 52)#棕色
#pygame.font.SysFont(...) 是"使用系统安装的字体"，参数依次是：字体名、字号、是否粗体。
font = pygame.font.SysFont("arial", 28, bold=True)#默认字体，28号，加粗
title_font = pygame.font.SysFont("arial", 48, bold=True)#标题字体，48号，加粗
small_font = pygame.font.SysFont("arial", 20, bold=True)#小字体，20号，加粗
card_title_font = pygame.font.SysFont("arial", 36, bold=True)#卡片标题字体，36号，加粗
card_help_font = pygame.font.SysFont("arial", 18, bold=True)#卡片帮助字体，18号，加粗

base_path = "assets"#一个普通字符串变量，表示游戏资源的目录路径

#定义一个加载缩放函数，参数是图片路径和目标大小，返回值是一个Surface对象，表示缩放后的图片
def load_scaled(path, size):
    img = pygame.image.load(path).convert_alpha()#加载图片，返回值是一个Surface对象，表示图片，convert_alpha()方法将图片转换为透明模式
    return pygame.transform.scale(img, size)#将图片缩放到目标大小，返回值是一个Surface对象，表示缩放后的图片

#加载玩家的图片
player_idle = load_scaled(f"{base_path}/characters/platformChar_idle.png", (42, 52))
player_jump = load_scaled(f"{base_path}/characters/platformChar_jump.png", (42, 52))
player_walk1 = load_scaled(f"{base_path}/characters/platformChar_walk1.png", (42, 52))
player_walk2 = load_scaled(f"{base_path}/characters/platformChar_walk2.png", (42, 52))
coin_img = load_scaled(f"{base_path}/items/item_coin.png", (26, 26))

ground_tile = load_scaled(f"{base_path}/tiles/tile_ground.png", (64, 64))
grass_tile = load_scaled(f"{base_path}/tiles/tile_grass.png", (64, 64))
grass_mid = load_scaled(f"{base_path}/tiles/tile_grassMid.png", (64, 64))

GROUND_Y = 470#地面的y坐标，单位是像素，从窗口的底部开始计数，地面的y坐标是470，玩家的y坐标是470-52=418


class Player:
    def __init__(self):
        self.x = 80#玩家的x坐标，单位是像素，从窗口的左侧开始计数，玩家的x坐标是80
        self.y = GROUND_Y - 52#玩家的y坐标，单位是像素，从窗口的底部开始计数，玩家的y坐标是418
        self.w = 42#玩家的宽度，单位是像素，玩家的宽度是42
        self.h = 52#玩家的高度，单位是像素，玩家的高度是52
        self.vx = 0.0#玩家的x方向速度，单位是像素/帧
        self.vy = 0.0#玩家的y方向速度，单位是像素/帧
        self.speed = 4.0#玩家的移动速度，单位是像素/帧
        self.jump = -13.5#玩家的跳跃力度，单位是像素/帧
        self.gravity = 0.65#玩家受到的重力，单位是像素/帧²
        self.on_ground = True#玩家是否在地面上
        self.facing = 1#玩家 facing 的方向，1表示向右，-1表示向左
        self.anim_timer = 0.0#动画计时器
        self.lives = 3#玩家的生命值
        self.score = 0#玩家的得分
        self.state = "idle"#玩家的状态，idle表示空闲，jump表示跳跃，walk1表示走1，walk2表示走2
        self.jump_count = 0#玩家跳跃跳跃的次数
        self.jump_lock = False#玩家是否跳跃锁定，防止连续跳跃

    def rect(self):#返回玩家的矩形区域，单位是像素，返回值是一个pygame.Rect对象，表示玩家的矩形区域
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def reset_position(self):#把玩家的位置和运动状态重置，但保留 lives 和 score。什么时候用？被敌人撞了减血，但还没 GAME OVER，把人传送回起点继续。
        self.x = 80#玩家的x坐标，单位是像素，从窗口的左侧开始计数，玩家的x坐标是80
        self.y = GROUND_Y - 52#玩家的y坐标，单位是像素，从窗口的底部开始计数，玩家的y坐标是418
        self.vx = 0.0#玩家的x方向速度，单位是像素/帧
        self.vy = 0.0#玩家的y方向速度，单位是像素/帧
        self.on_ground = True#玩家是否在地面上
        self.facing = 1#玩家 facing 的方向，1表示向右，-1表示向左
        self.state = "idle"#玩家的状态，idle表示空闲，jump表示跳跃，walk1表示走1，walk2表示走2
        self.jump_count = 0#玩家跳跃跳跃的次数
        self.jump_lock = False#玩家是否跳跃锁定，防止连续跳跃

    def reset_stats(self):#把玩家的统计信息重置，包括保留 lives 和 score。
        self.speed = 4.0
        self.jump = -13.5
        self.gravity = 0.65
        self.anim_timer = 0.0
        self.lives = 3
        self.score = 0
        self.reset_position()
#调用reset_position方法，把玩家的位置和运动状态重置，但保留 lives 和 score。

# 游戏类，管理游戏的状态、关卡、玩家、敌人等元素
class Game:
    def __init__(self):
        self.levels = prepare_level_data()
        self.player = Player()#创建一个玩家对象
        self.platforms = []  #平台列表，用于存储游戏中的平台对象
        self.coins = []  #金币列表，用于存储游戏中的金币对象
        self.enemies = []
        self.flag_x = 0
        self.world_width = self.levels[0]["world_width"]
        self.the_end = False
        self.camera_x = 0
        self.game_state = "start"
        self.current_level_index = 0
        self.level_buttons = []
        self.transition_timer = 0
        self.transition_duration = 70
        self.transition_text = "STAGE 1"
        self.load_level(0)

# 重置游戏状态，包括玩家位置、敌人位置、金币状态等
    def reset_game(self):
        self.player.reset_stats()      #玩家血量，分数，位置全部重置
        for coin in self.coins:        #把每个金币的 collected 属性设置为 False，表示金币未被收集  
            coin["collected"] = False
        for i, enemy in enumerate(self.enemies):
            enemy["x"] = enemy["min_x"] if i % 2 == 0 else enemy["max_x"]   #敌人位置也重置
            enemy["dir"] = 1 if i % 2 == 0 else -1                          #敌人方向也重置
            if enemy.get("kind") == "flyer":
                enemy["float_offset"] = 0.0                          #敌人飞行高度也重置
                enemy["y"] = enemy.get("base_y", GROUND_Y - 30)
            elif enemy.get("kind") == "jumper":
                enemy["jump_v"] = -1.2                          #敌人跳跃高度也重置
                enemy["y"] = enemy.get("base_y", GROUND_Y - 30)
        self.camera_x = 0
        self.the_end = False
        self.transition_timer = 0

# 加载指定关卡的数据，包括平台、金币、敌人等
    def load_level(self, index):
        self.current_level_index = index
        level = self.levels[index]  #取出第index个关卡字典
        self.platforms = [platform.copy() for platform in level["platforms"]]  #复制平台列表，避免修改原始数据
        self.coins = [coin.copy() for coin in level["coins"]]  #复制金币列表，避免修改原始数据
        self.enemies = [enemy.copy() for enemy in level["enemies"]]  #复制敌人列表，避免修改原始数据
        for enemy in self.enemies:
            enemy.setdefault("kind", "walker")
            enemy.setdefault("base_y", enemy["y"])
            enemy.setdefault("float_offset", 0.0)
            enemy.setdefault("jump_v", 0.0)
        self.flag_x = level["flag_x"]
        self.world_width = level["world_width"]
        self.camera_x = 0
        self.the_end = False
        self.reset_game()

    def start_level(self, index):
        self.load_level(index)
        self.transition_text = f"STAGE {index + 1}"
        self.transition_timer = 0
        self.game_state = "transition"

    def handle_player_damage(self):
        self.player.lives -= 1
        self.player.reset_position()
        self.camera_x = 0
        if self.player.lives <= 0:
            self.player.state = "dead"
            self.game_state = "dead"

    def get_enemy_color(self, enemy):
        kind = enemy.get("kind", "walker")
        if kind == "jumper":
            return (255, 170, 70)
        if kind == "flyer":
            return (170, 130, 255)
        return RED

    def update_player(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.vx = -self.player.speed
            self.player.facing = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.vx = self.player.speed
            self.player.facing = 1
        else:
            self.player.vx *= 0.8
            if abs(self.player.vx) < 0.1:
                self.player.vx = 0

        jump_pressed = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]
        if jump_pressed and not self.player.jump_lock:
            if self.player.on_ground:
                self.player.vy = self.player.jump
                self.player.on_ground = False
                self.player.jump_count = 1
            elif self.player.jump_count < 2:
                self.player.vy = self.player.jump * 0.9
                self.player.jump_count += 1
            self.player.jump_lock = True
        elif not jump_pressed:
            self.player.jump_lock = False

        if self.player.on_ground:
            self.player.vy = 0
        else:
            self.player.vy += self.player.gravity

        prev_x = self.player.x
        prev_y = self.player.y

        self.player.x += self.player.vx
        rect = self.player.rect()
        for p in self.platforms:
            pr = pygame.Rect(p["x"], p["y"], p["w"], p["h"])
            if rect.colliderect(pr):
                if prev_x + self.player.w <= pr.left + 10 and self.player.vx > 0:
                    self.player.x = pr.left - self.player.w
                elif prev_x >= pr.right - 10 and self.player.vx < 0:
                    self.player.x = pr.right
                self.player.vx = 0

        self.player.y += self.player.vy
        rect = self.player.rect()
        self.player.on_ground = False
        for p in self.platforms:
            pr = pygame.Rect(p["x"], p["y"], p["w"], p["h"])
            if rect.colliderect(pr):
                if prev_y + self.player.h <= pr.top + 18 and self.player.vy >= 0:
                    self.player.y = pr.top - self.player.h
                    self.player.vy = 0
                    self.player.on_ground = True
                    self.player.jump_count = 0
                elif prev_y >= pr.bottom - 18 and self.player.vy < 0:
                    self.player.y = pr.bottom
                    self.player.vy = 0

        if self.player.on_ground:
            self.player.vy = 0
            self.player.jump_count = 0

        if self.player.y > HEIGHT + 80:
            self.handle_player_damage()
            return

        if abs(self.player.vx) > 0.2 and self.player.on_ground:
            self.player.state = "moving"
        elif not self.player.on_ground:
            self.player.state = "jumping"
        else:
            self.player.state = "idle"

        self.player.anim_timer += abs(self.player.vx) * 0.7 + 1

        for coin in self.coins:
            if not coin["collected"]:
                c_rect = pygame.Rect(coin["x"], coin["y"], 26, 26)
                if rect.colliderect(c_rect):
                    coin["collected"] = True
                    self.player.score += 10

        for enemy in self.enemies:
            e_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["w"], enemy["h"])
            if rect.colliderect(e_rect):
                if self.player.vy > 0 and prev_y + self.player.h <= enemy["y"] + 10:
                    self.player.vy = -10
                    enemy["x"] = -999
                else:
                    self.handle_player_damage()
                    return

        if self.player.x > self.flag_x:
            self.the_end = True

        self.camera_x = max(0, min(self.player.x - WIDTH * 0.35, self.world_width - WIDTH))

    def update_enemies(self):
        for enemy in self.enemies:
            kind = enemy.get("kind", "walker")
            enemy["x"] += enemy["speed"] * enemy["dir"]

            if kind == "flyer":
                enemy["float_offset"] += 0.12
                enemy["y"] = enemy["base_y"] + math.sin(enemy["float_offset"]) * 18
            elif kind == "jumper":
                enemy["jump_v"] += 0.14
                enemy["y"] += enemy["jump_v"]
                if enemy["y"] >= enemy["base_y"]:
                    enemy["y"] = enemy["base_y"]
                    enemy["jump_v"] = -3.8

            if enemy["x"] <= enemy["min_x"] or enemy["x"] >= enemy["max_x"]:
                enemy["dir"] *= -1

    def draw_background(self, surface):
        surface.fill(SKY_TOP)
        for i in range(0, WIDTH + 200, 180):
            pygame.draw.rect(surface, (160, 210, 255), (i - 40, 110, 90, 50))
            pygame.draw.circle(surface, WHITE, (i, 100), 20)
            pygame.draw.circle(surface, WHITE, (i + 25, 100), 20)
            pygame.draw.circle(surface, WHITE, (i + 12, 80), 20)
        for i in range(0, WIDTH + 500, 220):
            pygame.draw.polygon(surface, (110, 140, 90), [(i, HEIGHT), (i + 70, 250), (i + 140, HEIGHT)])

    def draw_ground_tiles(self, surface, world_x):
        for p in self.platforms:
            sx = p["x"] - world_x
            tile_w = ground_tile.get_width()
            if p["y"] >= GROUND_Y - 10:
                for i in range(0, p["w"], tile_w):
                    surface.blit(ground_tile, (sx + i, p["y"]))
                    surface.blit(grass_mid, (sx + i, p["y"] - 64))
            else:
                pygame.draw.rect(surface, (145, 130, 100), (sx, p["y"], p["w"], p["h"]))

    def draw_platforms(self, surface, world_x):
        for p in self.platforms:
            sx = p["x"] - world_x
            if p["y"] >= GROUND_Y - 10:
                continue
            pygame.draw.rect(surface, (190, 160, 120), (sx, p["y"], p["w"], p["h"]))
            for tile_index in range(0, p["w"], 64):
                surface.blit(grass_tile, (sx + tile_index, p["y"]))

    def draw_coins(self, surface, world_x):
        for coin in self.coins:
            if not coin["collected"]:
                surface.blit(coin_img, (coin["x"] - world_x, coin["y"]))

    def draw_flag(self, surface, world_x):
        flag_x_screen = self.flag_x - world_x
        pygame.draw.rect(surface, WHITE, (flag_x_screen, 240, 6, 200))
        pygame.draw.polygon(surface, RED, [(flag_x_screen + 6, 240), (flag_x_screen + 6 + 60, 270), (flag_x_screen + 6, 300)])

    def get_enemy_rect(self, enemy, world_x):
        px = enemy["x"] - world_x
        return pygame.Rect(px, enemy["y"], enemy["w"], enemy["h"])

    def draw_enemies(self, surface, world_x):
        for enemy in self.enemies:
            if enemy["x"] < -100:
                continue
            px = enemy["x"] - world_x
            color = self.get_enemy_color(enemy)
            pygame.draw.rect(surface, color, (px, enemy["y"], enemy["w"], enemy["h"]))
            if enemy.get("kind") == "flyer":
                pygame.draw.circle(surface, WHITE, (int(px + 8), int(enemy["y"] + 8)), 3)
                pygame.draw.circle(surface, WHITE, (int(px + 22), int(enemy["y"] + 8)), 3)
            else:
                pygame.draw.circle(surface, BLACK, (int(px + 8), int(enemy["y"] + 8)), 4)
                pygame.draw.circle(surface, BLACK, (int(px + 22), int(enemy["y"] + 8)), 4)

    def get_player_image(self):
        return player_walk1

    def draw_life_icons(self, surface, x, y):
        heart_size = 12
        spacing = 18
        for i in range(3):
            heart_x = x + i * spacing
            active = i < self.player.lives
            fill = RED if active else (100, 100, 110)
            border = (255, 255, 255) if active else (70, 70, 80)
            heart = pygame.Rect(heart_x, y, heart_size, heart_size)
            inner = pygame.Rect(heart_x + 3, y + 3, heart_size - 6, heart_size - 6)
            pygame.draw.rect(surface, border, heart, 2)
            pygame.draw.rect(surface, fill, inner)

    def draw_player(self, surface, world_x):
        px = self.player.x - world_x
        py = self.player.y
        if self.player.state == "dead":
            return
        img = self.get_player_image()
        img = pygame.transform.flip(img, self.player.facing == -1, False)
        surface.blit(img, (px, py))

    def draw_hud(self, surface):
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        life_label = font.render("HP", True, WHITE)
        stage_text = font.render(f"Stage {self.current_level_index + 1}", True, WHITE)
        surface.blit(score_text, (20, 18))
        surface.blit(life_label, (20, 48))
        self.draw_life_icons(surface, 58, 52)
        surface.blit(stage_text, (WIDTH - 180, 18))
        if self.the_end:
            win_text = font.render("LEVEL CLEAR!", True, YELLOW)
            surface.blit(win_text, (WIDTH // 2 - 90, 20))
        elif self.player.state == "dead":
            over_text = font.render("GAME OVER", True, RED)
            surface.blit(over_text, (WIDTH // 2 - 90, 20))

    def draw_start_screen(self):
        screen.fill(DARK_BLUE)

        for i in range(0, WIDTH + 220, 220):
            pygame.draw.polygon(screen, (80, 120, 200), [(i, HEIGHT), (i + 70, 260), (i + 140, HEIGHT)])

        title_x = WIDTH // 2 - title_font.size("Mini Mario Adventure")[0] // 2
        title_y = 48
        shadow_text = title_font.render("Mini Mario Adventure", True, (50, 80, 130))
        screen.blit(shadow_text, (title_x + 4, title_y + 6))
        title_text = title_font.render("Mini Mario Adventure", True, WHITE)
        screen.blit(title_text, (title_x, title_y))

        info_panel = pygame.Surface((560, 90), pygame.SRCALPHA)
        pygame.draw.rect(info_panel, (20, 35, 80, 180), info_panel.get_rect(), border_radius=20)
        screen.blit(info_panel, (WIDTH // 2 - 280, 130))

        sub_text = card_help_font.render("Choose a stage and reach the flag", True, WHITE)
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, 150))

        control_text = small_font.render("Move: A / D or Arrow Keys    Jump: W / Up / Space", True, YELLOW)
        screen.blit(control_text, (WIDTH // 2 - control_text.get_width() // 2, 182))

        self.level_buttons.clear()
        card_x = WIDTH // 2 - 230
        card_width = 460
        start_y = 220
        card_h = 72
        card_gap = 14
        for index, level in enumerate(self.levels):
            rect = pygame.Rect(card_x, start_y + index * (card_h + card_gap), card_width, card_h)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            fill_color = (118, 196, 255) if hovered else (72, 138, 220)
            shadow_rect = rect.move(0, 8)
            pygame.draw.rect(screen, (30, 60, 120), shadow_rect, border_radius=14)
            pygame.draw.rect(screen, fill_color, rect, border_radius=14)
            pygame.draw.rect(screen, YELLOW, rect, 3, border_radius=14)

            name_text = card_title_font.render(level["name"], True, WHITE)
            screen.blit(name_text, (rect.x + 28, rect.y + 10))

            help_text = card_help_font.render(LEVEL_HINTS.get(index, "Reach the flag!"), True, WHITE)
            screen.blit(help_text, (rect.x + 28, rect.y + 48))
            self.level_buttons.append(rect)

        tip_panel = pygame.Surface((220, 42), pygame.SRCALPHA)
        pygame.draw.rect(tip_panel, (0, 0, 0, 120), tip_panel.get_rect(), border_radius=12)
        screen.blit(tip_panel, (WIDTH // 2 - 110, 490))
        tip_label = small_font.render("Click a stage to start", True, WHITE)
        screen.blit(tip_label, (WIDTH // 2 - tip_label.get_width() // 2, 500))

    def draw_transition_overlay(self):
        alpha = min(255, int((self.transition_timer / self.transition_duration) * 255))
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(shade, (0, 0, 0, max(80, 220 - alpha)), shade.get_rect())
        screen.blit(shade, (0, 0))

        title = title_font.render(self.transition_text, True, WHITE)
        subtitle = small_font.render("Ready!", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 30))

    def draw_world(self):
        self.draw_background(screen)
        self.draw_ground_tiles(screen, self.camera_x)
        self.draw_platforms(screen, self.camera_x)
        self.draw_coins(screen, self.camera_x)
        self.draw_enemies(screen, self.camera_x)
        self.draw_flag(screen, self.camera_x)
        self.draw_player(screen, self.camera_x)
        self.draw_hud(screen)

        if self.game_state == "transition":
            self.draw_transition_overlay()
            return

        if self.game_state == "win":
            panel = pygame.Surface((460, 170), pygame.SRCALPHA)
            pygame.draw.rect(panel, (0, 0, 0, 180), panel.get_rect(), border_radius=18)
            screen.blit(panel, (WIDTH // 2 - 230, HEIGHT // 2 - 85))
            end_text = title_font.render("LEVEL CLEAR!", True, YELLOW)
            hint_text = small_font.render("Click to return to the stage menu", True, WHITE)
            screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 45))

        if self.game_state == "dead":
            panel = pygame.Surface((470, 170), pygame.SRCALPHA)
            pygame.draw.rect(panel, (0, 0, 0, 180), panel.get_rect(), border_radius=18)
            screen.blit(panel, (WIDTH // 2 - 235, HEIGHT // 2 - 85))
            over_text = title_font.render("GAME OVER", True, RED)
            hint_text = small_font.render("Click to return to the stage menu", True, WHITE)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 45))

    def update(self):
        if self.game_state == "transition":
            self.transition_timer += 1
            if self.transition_timer >= self.transition_duration:
                self.game_state = "playing"
            return

        if self.game_state == "playing":
            if self.player.state != "dead" and not self.the_end:
                self.update_player()
                self.update_enemies()
            if self.player.state == "dead":
                self.game_state = "dead"
            if self.the_end:
                self.game_state = "win"

    def draw(self):
        if self.game_state == "start":
            self.draw_start_screen()
        else:
            self.draw_world()

    def handle_click(self, pos):
        if self.game_state == "start":
            for idx, rect in enumerate(self.level_buttons):
                if rect.collidepoint(pos):
                    self.start_level(idx)
                    return True
        elif self.game_state in ("dead", "win"):
            self.game_state = "start"
            self.level_buttons.clear()
            return True
        return False


def prepare_level_data():
    level1 = {
        "name": "Stage 1",
        "world_width": 2400,
        "flag_x": 2240,
        "platforms": [
            {"x": 0, "y": GROUND_Y, "w": 700, "h": 90},
            {"x": 760, "y": GROUND_Y, "w": 640, "h": 90},
            {"x": 1500, "y": GROUND_Y, "w": 700, "h": 90},
            {"x": 2000, "y": GROUND_Y, "w": 400, "h": 90},
            {"x": 280, "y": 400, "w": 140, "h": 28},
            {"x": 520, "y": 350, "w": 130, "h": 28},
            {"x": 900, "y": 310, "w": 150, "h": 28},
            {"x": 1180, "y": 260, "w": 140, "h": 28},
            {"x": 1700, "y": 340, "w": 160, "h": 28},
            {"x": 1950, "y": 290, "w": 140, "h": 28},
        ],
        "coins": [
            {"x": 140, "y": 420, "collected": False},
            {"x": 330, "y": 350, "collected": False},
            {"x": 570, "y": 310, "collected": False},
            {"x": 950, "y": 270, "collected": False},
            {"x": 1215, "y": 220, "collected": False},
            {"x": 1750, "y": 300, "collected": False},
            {"x": 2010, "y": 250, "collected": False},
            {"x": 2170, "y": 420, "collected": False},
        ],
        "enemies": [
            {"x": 900, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.4, "dir": 1, "min_x": 820, "max_x": 1210, "kind": "walker", "base_y": GROUND_Y - 30},
            {"x": 1660, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.6, "dir": -1, "min_x": 1550, "max_x": 1890, "kind": "jumper", "base_y": GROUND_Y - 30, "jump_v": 0.0},
            {"x": 2130, "y": GROUND_Y - 80, "w": 30, "h": 30, "speed": 1.7, "dir": 1, "min_x": 2070, "max_x": 2320, "kind": "flyer", "base_y": GROUND_Y - 100, "float_offset": 0.0},
        ],
    }

    level2 = {
        "name": "Stage 2",
        "world_width": 2600,
        "flag_x": 2450,
        "platforms": [
            {"x": 0, "y": GROUND_Y, "w": 650, "h": 90},
            {"x": 760, "y": GROUND_Y, "w": 560, "h": 90},
            {"x": 1450, "y": GROUND_Y, "w": 650, "h": 90},
            {"x": 2200, "y": GROUND_Y, "w": 400, "h": 90},
            {"x": 240, "y": 420, "w": 150, "h": 28},
            {"x": 520, "y": 365, "w": 140, "h": 28},
            {"x": 830, "y": 320, "w": 150, "h": 28},
            {"x": 1150, "y": 270, "w": 140, "h": 28},
            {"x": 1620, "y": 360, "w": 170, "h": 28},
            {"x": 1880, "y": 310, "w": 150, "h": 28},
            {"x": 2100, "y": 250, "w": 120, "h": 28},
        ],
        "coins": [
            {"x": 270, "y": 380, "collected": False},
            {"x": 560, "y": 325, "collected": False},
            {"x": 870, "y": 280, "collected": False},
            {"x": 1190, "y": 230, "collected": False},
            {"x": 1660, "y": 320, "collected": False},
            {"x": 1920, "y": 270, "collected": False},
            {"x": 2130, "y": 210, "collected": False},
            {"x": 2320, "y": 420, "collected": False},
        ],
        "enemies": [
            {"x": 860, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.5, "dir": 1, "min_x": 790, "max_x": 1200, "kind": "walker", "base_y": GROUND_Y - 30},
            {"x": 1600, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.7, "dir": -1, "min_x": 1490, "max_x": 1870, "kind": "jumper", "base_y": GROUND_Y - 30, "jump_v": 0.0},
            {"x": 2220, "y": GROUND_Y - 80, "w": 30, "h": 30, "speed": 1.8, "dir": 1, "min_x": 2170, "max_x": 2420, "kind": "flyer", "base_y": GROUND_Y - 120, "float_offset": 0.0},
        ],
    }

    level3 = {
        "name": "Stage 3",
        "world_width": 2900,
        "flag_x": 2740,
        "platforms": [
            {"x": 0, "y": GROUND_Y, "w": 620, "h": 90},
            {"x": 720, "y": GROUND_Y, "w": 580, "h": 90},
            {"x": 1420, "y": GROUND_Y, "w": 650, "h": 90},
            {"x": 2200, "y": GROUND_Y, "w": 700, "h": 90},
            {"x": 250, "y": 420, "w": 160, "h": 28},
            {"x": 540, "y": 360, "w": 140, "h": 28},
            {"x": 860, "y": 310, "w": 140, "h": 28},
            {"x": 1160, "y": 250, "w": 150, "h": 28},
            {"x": 1540, "y": 360, "w": 180, "h": 28},
            {"x": 1810, "y": 300, "w": 150, "h": 28},
            {"x": 2070, "y": 250, "w": 150, "h": 28},
            {"x": 2440, "y": 335, "w": 170, "h": 28},
        ],
        "coins": [
            {"x": 290, "y": 380, "collected": False},
            {"x": 600, "y": 320, "collected": False},
            {"x": 890, "y": 270, "collected": False},
            {"x": 1210, "y": 210, "collected": False},
            {"x": 1590, "y": 320, "collected": False},
            {"x": 1850, "y": 260, "collected": False},
            {"x": 2115, "y": 210, "collected": False},
            {"x": 2490, "y": 295, "collected": False},
            {"x": 2650, "y": 420, "collected": False},
        ],
        "enemies": [
            {"x": 860, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.5, "dir": 1, "min_x": 760, "max_x": 1200, "kind": "walker", "base_y": GROUND_Y - 30},
            {"x": 1600, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.7, "dir": -1, "min_x": 1480, "max_x": 1880, "kind": "jumper", "base_y": GROUND_Y - 30, "jump_v": 0.0},
            {"x": 2250, "y": GROUND_Y - 80, "w": 30, "h": 30, "speed": 1.9, "dir": 1, "min_x": 2200, "max_x": 2540, "kind": "flyer", "base_y": GROUND_Y - 120, "float_offset": 0.0},
            {"x": 2560, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.8, "dir": -1, "min_x": 2400, "max_x": 2850, "kind": "walker", "base_y": GROUND_Y - 30},
        ],
    }

    return [level1, level2, level3]


LEVEL_HINTS = {
    0: "Reach the flag and avoid the patrols.",
    1: "Use the floating ledges to gain height.",
    2: "The final route needs careful double-jumps.",
}


def main():
    game = Game()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)

        game.update()
        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
