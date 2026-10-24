# ==============================================================================
# 项目：Mini Mario Adventure（迷你马里奥大冒险）
# 类型：Pygame 横版跳跃小游戏
# 功能：选关界面 + 3 个关卡 + 金币收集 + 敌人踩头消灭 + 二段跳
#
# 代码结构（6 大区域）：
#   ① 导入库 & 初始化           —— 窗口、时钟、颜色、字体
#   ② 图片加载工具 & 素材常量   —— load_scaled() + 所有贴图变量
#   ③ Player 类                 —— 玩家角色的属性和方法
#   ④ Game 类                   —— 整个游戏的大脑（状态管理+更新+渲染）
#   ⑤ 关卡数据 prepare_level_data() —— 3 个关卡的地图/金币/敌人配置
#   ⑥ main() 函数 & 程序入口    —— 游戏主循环
# ==============================================================================

import math              # 数学库（敌人飞行用 sin 函数）
import pygame            # 游戏引擎
import sys               # 用于 sys.exit() 安全退出程序

# ==================================================================== #
# ① 导入库 & 初始化
# ==================================================================== #

pygame.init()                        # 初始化 Pygame 所有子系统（必须先调用）

WIDTH, HEIGHT = 960, 540             # 游戏窗口尺寸：宽 960、高 540（像素）
screen = pygame.display.set_mode((WIDTH, HEIGHT))   # 创建窗口，返回一个 Surface 对象（画布）
pygame.display.set_caption("Mini Mario Adventure")  # 设置窗口标题
clock = pygame.time.Clock()          # 创建时钟对象，用于控制游戏帧率
FPS = 60                             # 目标帧率：每秒 60 帧（Python 约定全大写=常量）

# ---------- 颜色常量（RGB 三元组）---------- #
WHITE     = (255, 255, 255)           # 纯白
BLACK     = (0,   0,   0)             # 纯黑
RED       = (210, 70, 70)             # 偏暗的红（敌人/扣血用）
YELLOW    = (255, 220, 80)            # 明黄（金币/提示用）
BLUE      = (90, 150, 220)            # 蓝色
SKY_TOP   = (140, 210, 255)           # 天空顶部渐变颜色
DARK_BLUE = (28, 50, 110)             # 深蓝（选关界面背景）
GOLD      = (255, 192, 72)            # 金色
PURPLE    = (138, 110, 255)           # 紫色（飞行敌人用）
MINT      = (111, 216, 156)           # 薄荷绿
BROWN     = (98, 74, 52)              # 棕色

# ---------- 字体常量 ---------- #
# pygame.font.SysFont(字体名, 字号, 是否粗体)
font            = pygame.font.SysFont("arial", 28, bold=True)     # 默认正文：28 号加粗
title_font      = pygame.font.SysFont("arial", 48, bold=True)    # 大标题：48 号加粗
small_font      = pygame.font.SysFont("arial", 20, bold=True)    # 小字提示：20 号加粗
card_title_font = pygame.font.SysFont("arial", 36, bold=True)    # 卡片标题：36 号加粗
card_help_font  = pygame.font.SysFont("arial", 18, bold=True)    # 卡片帮助文字：18 号加粗

# ---------- 资源目录 ---------- #
base_path = "assets"                 # 所有图片素材都放在 assets 文件夹下

# ==================================================================== #
# ② 图片加载工具函数 & 素材加载
# ==================================================================== #

def load_scaled(path, size):
    """
    加载一张图片并缩放到指定尺寸。
    :param path: 图片文件路径，如 "assets/characters/xxx.png"
    :param size: (宽, 高) 元组，目标尺寸
    :return: 缩放后的 pygame.Surface 对象
    """
    img = pygame.image.load(path).convert_alpha()  # 加载图片，convert_alpha() 保留透明通道
    return pygame.transform.scale(img, size)        # 缩放到目标大小后返回

# ---------- 玩家贴图（4 张，大小 42×52 像素）---------- #
player_idle  = load_scaled(f"{base_path}/characters/platformChar_idle.png",  (42, 52))
player_jump  = load_scaled(f"{base_path}/characters/platformChar_jump.png",  (42, 52))
player_walk1 = load_scaled(f"{base_path}/characters/platformChar_walk1.png", (42, 52))
player_walk2 = load_scaled(f"{base_path}/characters/platformChar_walk2.png", (42, 52))

# ---------- 物品贴图 ---------- #
coin_img = load_scaled(f"{base_path}/items/item_coin.png", (26, 26))      # 金币 26×26

# ---------- 地块贴图（64×64）---------- #
ground_tile = load_scaled(f"{base_path}/tiles/tile_ground.png",  (64, 64))  # 地下的土
grass_tile  = load_scaled(f"{base_path}/tiles/tile_grass.png",   (64, 64))  # 草地块
grass_mid   = load_scaled(f"{base_path}/tiles/tile_grassMid.png", (64, 64))  # 地面中层的草

# ---------- 地面基准线 ---------- #
GROUND_Y = 470  # 主地面的 y 坐标（像素），玩家站立时底部对齐此线

# ==================================================================== #
# ③ Player 类 —— 玩家角色的数据结构和操作
# ==================================================================== #
class Player:
    """玩家角色：存储位置、速度、生命、分数、动画状态等所有属性"""

    def __init__(self):
        """初始化玩家，设置默认位置和属性"""
        # ---------- 位置和尺寸 ---------- #
        self.x = 80                       # 玩家左上角 x（出生点在地图最左边靠右一点）
        self.y = GROUND_Y - 52            # 玩家左上角 y（站立时底部对齐 GROUND_Y）
        self.w = 42                       # 玩家宽度（像素）
        self.h = 52                       # 玩家高度（像素）

        # ---------- 物理参数 ---------- #
        self.vx = 0.0                     # x 方向速度（向右为正）
        self.vy = 0.0                     # y 方向速度（向下为正，因为屏幕坐标系 y 轴朝下）
        self.speed   = 4.0                # 水平移动速度上限
        self.jump    = -13.5              # 跳跃初速度（负值 = 向上）
        self.gravity = 0.65               # 重力加速度（每帧 vy 增加 0.65）

        # ---------- 状态标记 ---------- #
        self.on_ground   = True           # 是否站在地面上
        self.facing      = 1              # 朝向：1=向右，-1=向左（用于翻转贴图）
        self.anim_timer  = 0.0            # 动画计时器（用来切换走路帧）
        self.lives       = 3              # 初始生命值
        self.score       = 0              # 当前分数
        self.state       = "idle"         # 动画状态：idle / moving / jumping / dead
        self.jump_count  = 0              # 当前空中已跳跃次数（支持二段跳，上限 2）
        self.jump_lock   = False          # 跳跃防抖锁：按住跳跃键时只触发一次

    def rect(self):
        """返回玩家当前的碰撞矩形（pygame.Rect 对象）"""
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def reset_position(self):
        """
        把玩家位置、速度、跳跃状态全部重置为初始值。
        用于被敌人撞到但还没 GAME OVER 时，把人传送回起点。
        注意：lives 和 score 在此方法中不重置。
        """
        self.x = 80
        self.y = GROUND_Y - 52
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True
        self.facing = 1
        self.state = "idle"
        self.jump_count = 0
        self.jump_lock = False

    def reset_stats(self):
        """
        完全重置玩家：血量、分数、位置全部回到初始值。
        开始新游戏或新关卡时调用。
        """
        self.speed   = 4.0
        self.jump    = -13.5
        self.gravity = 0.65
        self.anim_timer = 0.0
        self.lives = 3
        self.score = 0
        self.reset_position()     # 复用 reset_position 重置位置部分

# ==================================================================== #
# ④ Game 类 —— 整个游戏的大脑
#    负责：状态机切换、玩家/敌人/金币更新、所有画面渲染、关卡加载
# ==================================================================== #
class Game:

    # ==================================================================== #
    # 构造 & 关卡加载
    # ==================================================================== #

    def __init__(self):
        """游戏初始化：加载关卡数据、创建玩家、加载第一关"""
        self.levels = prepare_level_data()   # 加载 3 个关卡的地图数据
        self.player = Player()               # 创建玩家对象

        # ---------- 关卡内的对象列表 ---------- #
        self.platforms = []   # 平台列表，每个元素是 {"x","y","w","h"} 字典
        self.coins     = []   # 金币列表，每个元素是 {"x","y","collected"} 字典
        self.enemies   = []   # 敌人列表，每个元素是含位置/速度/范围的字典

        # ---------- 关卡配置 ---------- #
        self.flag_x      = 0              # 终点旗帜的 x 坐标
        self.world_width = self.levels[0]["world_width"]  # 当前关卡地图总宽度

        # ---------- 游戏状态机 ---------- #
        self.the_end            = False   # 是否已到达终点
        self.camera_x           = 0       # 摄像机 x 偏移（用于画面滚动）
        self.game_state         = "start" # 当前状态：start/transition/playing/win/dead
        self.current_level_index = 0      # 当前关卡索引（0=第一关）

        # ---------- 过渡动画 ---------- #
        self.level_buttons        = []    # 选关界面上按钮的 Rect 列表（用于鼠标点击判定）
        self.transition_timer     = 0     # 关卡开场动画的计时器
        self.transition_duration  = 70    # 过渡动画持续帧数（约 1.17 秒）
        self.transition_text      = "STAGE 1"

        self.load_level(0)                # 预加载第一关的数据（但游戏状态仍为 start）

    def reset_game(self):
        """
        重置当前关卡的可玩状态：
        - 玩家血量/分数/位置重置
        - 所有金币恢复未收集
        - 所有敌人回到初始位置和方向
        - 摄像机回到原点
        """
        self.player.reset_stats()          # 玩家血量、分数、位置全部重置

        for coin in self.coins:            # 金币全部恢复未收集
            coin["collected"] = False

        for i, enemy in enumerate(self.enemies):
            # 根据敌人索引的奇偶性决定初始位置（min_x 或 max_x）
            enemy["x"]  = enemy["min_x"] if i % 2 == 0 else enemy["max_x"]
            enemy["dir"] = 1 if i % 2 == 0 else -1

            # 不同类型敌人的状态也重置
            if enemy.get("kind") == "flyer":
                enemy["float_offset"] = 0.0
                enemy["y"] = enemy.get("base_y", GROUND_Y - 30)
            elif enemy.get("kind") == "jumper":
                enemy["jump_v"] = -1.2
                enemy["y"] = enemy.get("base_y", GROUND_Y - 30)

        self.camera_x = 0
        self.the_end  = False
        self.transition_timer = 0

    def load_level(self, index):
        """
        加载指定关卡的全部数据（平台、金币、敌人等）。
        注意：用 .copy() 复制每个字典，避免修改 prepare_level_data() 里的原始数据。
        """
        self.current_level_index = index
        level = self.levels[index]

        self.platforms = [p.copy() for p in level["platforms"]]
        self.coins     = [c.copy() for c in level["coins"]]
        self.enemies   = [e.copy() for e in level["enemies"]]

        # 为敌人补全默认字段（如果关卡数据里没写的话）
        for enemy in self.enemies:
            enemy.setdefault("kind",         "walker")          # 默认是地面巡逻型
            enemy.setdefault("base_y",       enemy["y"])        # 基准 y（flyer 浮动用）
            enemy.setdefault("float_offset", 0.0)
            enemy.setdefault("jump_v",       0.0)

        self.flag_x      = level["flag_x"]
        self.world_width = level["world_width"]
        self.camera_x    = 0
        self.the_end     = False
        self.reset_game()

    def start_level(self, index):
        """
        正式开始一个关卡：加载数据 + 设置过渡动画 + 切到 transition 状态。
        transition 状态会显示 "STAGE 1 Ready!" 约 1 秒，之后自动变成 playing。
        """
        self.load_level(index)
        self.transition_text = f"STAGE {index + 1}"
        self.transition_timer = 0
        self.game_state = "transition"

    def handle_player_damage(self):
        """
        玩家扣血 + 传送回起点。
        如果血量归零 → 玩家状态设为 dead + 游戏状态切到 dead（GAME OVER）。
        """
        self.player.lives -= 1
        self.player.reset_position()
        self.camera_x = 0
        if self.player.lives <= 0:
            self.player.state = "dead"
            self.game_state = "dead"

    def get_enemy_color(self, enemy):
        """根据敌人 kind 返回对应的颜色元组"""
        kind = enemy.get("kind", "walker")
        if kind == "jumper": return (255, 170, 70)   # 橙色
        if kind == "flyer":  return (170, 130, 255)   # 紫色
        return RED                                    # walker 默认红色

    # ==================================================================== #
    # 玩家更新（物理、碰撞、金币、敌人、摄像机）
    # ==================================================================== #

    def update_player(self):
        # ---------------------------------------------------------------- #
        # ① 读取键盘输入 → 设置水平速度 vx（左右移动 + 摩擦减速）
        # ---------------------------------------------------------------- #
        keys = pygame.key.get_pressed()

        # A / ← 向左走，速度为 -speed，朝向设为 -1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.vx = -self.player.speed
            self.player.facing = -1
        # D / → 向右走，速度为 +speed，朝向设为 1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.vx = self.player.speed
            self.player.facing = 1
        # 没按方向键 → 摩擦减速（每帧乘 0.8），几乎为 0 就归零
        else:
            self.player.vx *= 0.8
            if abs(self.player.vx) < 0.1:
                self.player.vx = 0

        # ---------------------------------------------------------------- #
        # ② 跳跃处理（支持二段跳 + jump_lock 防止连触）
        # ---------------------------------------------------------------- #
        jump_pressed = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]

        if jump_pressed and not self.player.jump_lock:
            if self.player.on_ground:
                # 地面起跳：vy 赋一个负值（向上），跳跃次数记为 1
                self.player.vy = self.player.jump
                self.player.on_ground = False
                self.player.jump_count = 1
            elif self.player.jump_count < 2:
                # 空中二段跳：力度稍微衰减（× 0.9），跳跃次数 +1
                self.player.vy = self.player.jump * 0.9
                self.player.jump_count += 1
            # 触发跳跃后立刻上锁，必须松手才能再次触发
            self.player.jump_lock = True
        elif not jump_pressed:
            # 松开跳跃键 → 解锁，允许下次再跳
            self.player.jump_lock = False

        # ---------------------------------------------------------------- #
        # ③ 重力应用：地面则 vy=0，空中则 vy += gravity
        # ---------------------------------------------------------------- #
        if self.player.on_ground:
            self.player.vy = 0
        else:
            self.player.vy += self.player.gravity

        # ---------------------------------------------------------------- #
        # ④ 碰撞检测准备：记录移动前的位置（用于判断"从哪个方向撞到的"）
        # ---------------------------------------------------------------- #
        prev_x = self.player.x
        prev_y = self.player.y

        # ---- ④-a 先移动 x，再做水平方向碰撞修正 ---- #
        self.player.x += self.player.vx
        rect = self.player.rect()
        for p in self.platforms:
            pr = pygame.Rect(p["x"], p["y"], p["w"], p["h"])
            if rect.colliderect(pr):
                # 玩家从右侧走向平台：贴到平台左侧
                if prev_x + self.player.w <= pr.left + 10 and self.player.vx > 0:
                    self.player.x = pr.left - self.player.w
                # 玩家从左侧走向平台：贴到平台右侧
                elif prev_x >= pr.right - 10 and self.player.vx < 0:
                    self.player.x = pr.right
                # 撞墙了 → 水平速度清零
                self.player.vx = 0

        # ---- ④-b 再移动 y，做垂直方向碰撞修正 + 判定是否踩地 ---- #
        self.player.y += self.player.vy
        rect = self.player.rect()
        # 先假设不在地面上，下方循环里如果确实踩了平台再设回 True
        self.player.on_ground = False
        for p in self.platforms:
            pr = pygame.Rect(p["x"], p["y"], p["w"], p["h"])
            if rect.colliderect(pr):
                # 从上方落到平台顶：粘到顶部 + vy 清零 + 标记在地面
                if prev_y + self.player.h <= pr.top + 18 and self.player.vy >= 0:
                    self.player.y = pr.top - self.player.h
                    self.player.vy = 0
                    self.player.on_ground = True
                    self.player.jump_count = 0      # 落地后跳跃次数清零
                # 从下方顶到平台底：粘到底部 + vy 清零
                elif prev_y >= pr.bottom - 18 and self.player.vy < 0:
                    self.player.y = pr.bottom
                    self.player.vy = 0

        # ---------------------------------------------------------------- #
        # ⑤ 地面状态二次确认：强制把 vy 和 jump_count 归零
        # ---------------------------------------------------------------- #
        if self.player.on_ground:
            self.player.vy = 0
            self.player.jump_count = 0

        # ---------------------------------------------------------------- #
        # ⑥ 掉出屏幕底部 → 扣血
        # ---------------------------------------------------------------- #
        if self.player.y > HEIGHT + 80:
            self.handle_player_damage()
            return

        # ---------------------------------------------------------------- #
        # ⑦ 根据当前速度和位置设定玩家动画状态
        # ---------------------------------------------------------------- #
        if abs(self.player.vx) > 0.2 and self.player.on_ground:
            self.player.state = "moving"     # 地面且在移动
        elif not self.player.on_ground:
            self.player.state = "jumping"    # 在空中
        else:
            self.player.state = "idle"       # 地面静止

        # 动画计时器：速度越快计时越快，走路动画就切换得越勤
        self.player.anim_timer += abs(self.player.vx) * 0.7 + 1

        # ---------------------------------------------------------------- #
        # ⑧ 金币收集检测
        # ---------------------------------------------------------------- #
        for coin in self.coins:
            if not coin["collected"]:
                c_rect = pygame.Rect(coin["x"], coin["y"], 26, 26)
                if rect.colliderect(c_rect):
                    coin["collected"] = True    # 标记已收集
                    self.player.score += 10     # 每次收集 +10 分

        # ---------------------------------------------------------------- #
        # ⑨ 敌人碰撞检测：踩头顶消灭 / 侧面相撞扣血
        # ---------------------------------------------------------------- #
        for enemy in self.enemies:
            e_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["w"], enemy["h"])
            if rect.colliderect(e_rect):
                # 踩敌人头顶：玩家在下落 + 上一帧在敌人上方 → 反弹 + 消灭敌人
                if self.player.vy > 0 and prev_y + self.player.h <= enemy["y"] + 10:
                    self.player.vy = -10              # 向上反弹一下
                    enemy["x"] = -999                 # 移出屏幕 = 消灭
                # 侧面相撞：直接扣血
                else:
                    self.handle_player_damage()
                    return

        # ---------------------------------------------------------------- #
        # ⑩ 终点检测 & 摄像机跟随
        # ---------------------------------------------------------------- #
        if self.player.x > self.flag_x:
            self.the_end = True                  # 到达终点 → 标记通关

        # 摄像机跟随：让玩家保持在屏幕偏左 35% 处，不超出地图边界
        self.camera_x = max(0, min(self.player.x - WIDTH * 0.35, self.world_width - WIDTH))

    # ==================================================================== #
    # 敌人更新
    # ==================================================================== #

    def update_enemies(self):
        """更新所有敌人的位置：巡逻、飞行浮动、跳跃等不同行为"""
        for enemy in self.enemies:
            kind = enemy.get("kind", "walker")

            # ---------- 所有敌人通用：水平移动 ---------- #
            enemy["x"] += enemy["speed"] * enemy["dir"]

            # ---------- 不同 kind 的特殊行为 ---------- #
            if kind == "flyer":
                # 飞行敌人：y 方向上下浮动（用 sin 函数做周期性摆动）
                enemy["float_offset"] += 0.12
                enemy["y"] = enemy["base_y"] + math.sin(enemy["float_offset"]) * 18

            elif kind == "jumper":
                # 跳跃敌人：每隔一段时间自动向上跳一下
                enemy["jump_v"] += 0.14      # 重力
                enemy["y"] += enemy["jump_v"]
                if enemy["y"] >= enemy["base_y"]:
                    enemy["y"] = enemy["base_y"]    # 落地
                    enemy["jump_v"] = -3.8          # 蓄力下一次跳跃

            # ---------- 通用：巡逻范围边界反弹 ---------- #
            if enemy["x"] <= enemy["min_x"] or enemy["x"] >= enemy["max_x"]:
                enemy["dir"] *= -1               # 到边界 → 掉头

    # ==================================================================== #
    # 渲染方法（全部是 draw_xxx）
    # ==================================================================== #

    def draw_background(self, surface):
        """绘制背景：天空渐变 + 云 + 远山"""
        surface.fill(SKY_TOP)                # 先刷一层天空颜色

        # 画云：每隔 180 像素画一朵（一个矩形 + 三个圆组成云朵形状）
        for i in range(0, WIDTH + 200, 180):
            pygame.draw.rect(surface, (160, 210, 255), (i - 40, 110, 90, 50))
            pygame.draw.circle(surface, WHITE, (i, 100), 20)
            pygame.draw.circle(surface, WHITE, (i + 25, 100), 20)
            pygame.draw.circle(surface, WHITE, (i + 12, 80), 20)

        # 画远山：每隔 220 像素画一个三角形
        for i in range(0, WIDTH + 500, 220):
            pygame.draw.polygon(surface, (110, 140, 90), [(i, HEIGHT), (i + 70, 250), (i + 140, HEIGHT)])

    def draw_ground_tiles(self, surface, world_x):
        """绘制地面的瓦片贴图：地面 y >= GROUND_Y - 10 的平台用此方法"""
        for p in self.platforms:
            sx = p["x"] - world_x             # 世界坐标 → 屏幕坐标（减去摄像机偏移）
            tile_w = ground_tile.get_width()

            if p["y"] >= GROUND_Y - 10:
                # 主地面：用 ground_tile 铺满底层，上面叠一层 grass_mid
                for i in range(0, p["w"], tile_w):
                    surface.blit(ground_tile, (sx + i, p["y"]))
                    surface.blit(grass_mid, (sx + i, p["y"] - 64))
            else:
                # 地面层如果被削掉，画个矩形兜底
                pygame.draw.rect(surface, (145, 130, 100), (sx, p["y"], p["w"], p["h"]))

    def draw_platforms(self, surface, world_x):
        """绘制空中悬浮平台：地面以上的小平台用此方法"""
        for p in self.platforms:
            sx = p["x"] - world_x

            if p["y"] >= GROUND_Y - 10:
                continue                    # 地面平台已经由 draw_ground_tiles 画过了

            pygame.draw.rect(surface, (190, 160, 120), (sx, p["y"], p["w"], p["h"]))  # 土色主体
            for tile_index in range(0, p["w"], 64):
                surface.blit(grass_tile, (sx + tile_index, p["y"]))                  # 顶部草皮

    def draw_coins(self, surface, world_x):
        """绘制所有未收集的金币"""
        for coin in self.coins:
            if not coin["collected"]:
                surface.blit(coin_img, (coin["x"] - world_x, coin["y"]))

    def draw_flag(self, surface, world_x):
        """绘制终点旗帜（白色旗杆 + 红色三角旗面）"""
        flag_x_screen = self.flag_x - world_x
        pygame.draw.rect(surface, WHITE, (flag_x_screen, 240, 6, 200))                         # 旗杆
        pygame.draw.polygon(surface, RED, [
            (flag_x_screen + 6, 240),
            (flag_x_screen + 6 + 60, 270),
            (flag_x_screen + 6, 300)
        ])                                                                                       # 旗面

    def get_enemy_rect(self, enemy, world_x):
        """获取敌人在屏幕坐标系下的碰撞矩形"""
        px = enemy["x"] - world_x
        return pygame.Rect(px, enemy["y"], enemy["w"], enemy["h"])

    def draw_enemies(self, surface, world_x):
        """绘制所有敌人：不同 kind 颜色不同，眼睛画法也不同"""
        for enemy in self.enemies:
            if enemy["x"] < -100:
                continue                    # 已经被消灭（x=-999）→ 跳过

            px = enemy["x"] - world_x
            color = self.get_enemy_color(enemy)
            pygame.draw.rect(surface, color, (px, enemy["y"], enemy["w"], enemy["h"]))  # 身体方块

            if enemy.get("kind") == "flyer":
                # 飞行敌人：白色大眼睛
                pygame.draw.circle(surface, WHITE, (int(px + 8),  int(enemy["y"] + 8)), 3)
                pygame.draw.circle(surface, WHITE, (int(px + 22), int(enemy["y"] + 8)), 3)
            else:
                # 普通敌人：黑色眼珠
                pygame.draw.circle(surface, BLACK, (int(px + 8),  int(enemy["y"] + 8)), 4)
                pygame.draw.circle(surface, BLACK, (int(px + 22), int(enemy["y"] + 8)), 4)

    def get_player_image(self):
        """
        根据玩家当前动画状态返回对应的贴图。
        目前先统一返回 walk1，后续可以扩展状态切换。
        """
        return player_walk1

    def draw_life_icons(self, surface, x, y):
        """在 HUD 上绘制 3 颗心（当前血量 = 实心，其余 = 灰色空心）"""
        heart_size = 12
        spacing = 18
        for i in range(3):
            heart_x = x + i * spacing
            active = i < self.player.lives
            fill   = RED if active else (100, 100, 110)
            border = (255, 255, 255) if active else (70, 70, 80)
            heart = pygame.Rect(heart_x, y, heart_size, heart_size)
            inner = pygame.Rect(heart_x + 3, y + 3, heart_size - 6, heart_size - 6)
            pygame.draw.rect(surface, border, heart, 2)   # 边框
            pygame.draw.rect(surface, fill, inner)        # 填充

    def draw_player(self, surface, world_x):
        """绘制玩家：根据 facing 方向翻转贴图"""
        px = self.player.x - world_x
        py = self.player.y
        if self.player.state == "dead":
            return                        # 死亡状态不画玩家
        img = self.get_player_image()
        img = pygame.transform.flip(img, self.player.facing == -1, False)  # facing=-1 就水平翻转
        surface.blit(img, (px, py))

    def draw_hud(self, surface):
        """绘制游戏抬头显示：分数、血量、关卡名、通关/失败提示"""
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

    # ---------- 选关界面 ---------- #

    def draw_start_screen(self):
        """绘制选关界面：深蓝背景 + 大标题 + 关卡卡片 + 鼠标悬停效果"""
        screen.fill(DARK_BLUE)

        # 背景远山
        for i in range(0, WIDTH + 220, 220):
            pygame.draw.polygon(screen, (80, 120, 200), [(i, HEIGHT), (i + 70, 260), (i + 140, HEIGHT)])

        # 带阴影的大标题
        title_x = WIDTH // 2 - title_font.size("Mini Mario Adventure")[0] // 2
        title_y = 48
        shadow_text = title_font.render("Mini Mario Adventure", True, (50, 80, 130))
        screen.blit(shadow_text, (title_x + 4, title_y + 6))        # 阴影层
        title_text = title_font.render("Mini Mario Adventure", True, WHITE)
        screen.blit(title_text, (title_x, title_y))                 # 主标题

        # 信息面板（半透明圆角矩形）
        info_panel = pygame.Surface((560, 90), pygame.SRCALPHA)
        pygame.draw.rect(info_panel, (20, 35, 80, 180), info_panel.get_rect(), border_radius=20)
        screen.blit(info_panel, (WIDTH // 2 - 280, 130))

        # 副标题 & 操作说明
        sub_text = card_help_font.render("Choose a stage and reach the flag", True, WHITE)
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, 150))
        control_text = small_font.render("Move: A / D or Arrow Keys    Jump: W / Up / Space", True, YELLOW)
        screen.blit(control_text, (WIDTH // 2 - control_text.get_width() // 2, 182))

        # 关卡卡片（3 张，支持鼠标悬停变色）
        self.level_buttons.clear()       # 清空旧的按钮区域（防止重复添加）
        card_x = WIDTH // 2 - 230
        card_width = 460
        start_y = 220
        card_h = 72
        card_gap = 14
        for index, level in enumerate(self.levels):
            rect = pygame.Rect(card_x, start_y + index * (card_h + card_gap), card_width, card_h)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            fill_color = (118, 196, 255) if hovered else (72, 138, 220)   # 悬停变亮

            # 卡片阴影 + 卡片主体 + 黄色边框
            shadow_rect = rect.move(0, 8)
            pygame.draw.rect(screen, (30, 60, 120), shadow_rect, border_radius=14)
            pygame.draw.rect(screen, fill_color, rect, border_radius=14)
            pygame.draw.rect(screen, YELLOW, rect, 3, border_radius=14)

            # 关卡名 & 提示文字
            name_text = card_title_font.render(level["name"], True, WHITE)
            screen.blit(name_text, (rect.x + 28, rect.y + 10))
            help_text = card_help_font.render(LEVEL_HINTS.get(index, "Reach the flag!"), True, WHITE)
            screen.blit(help_text, (rect.x + 28, rect.y + 48))

            self.level_buttons.append(rect)   # 记录按钮区域，点击检测要用

        # 底部提示条
        tip_panel = pygame.Surface((220, 42), pygame.SRCALPHA)
        pygame.draw.rect(tip_panel, (0, 0, 0, 120), tip_panel.get_rect(), border_radius=12)
        screen.blit(tip_panel, (WIDTH // 2 - 110, 490))
        tip_label = small_font.render("Click a stage to start", True, WHITE)
        screen.blit(tip_label, (WIDTH // 2 - tip_label.get_width() // 2, 500))

    def draw_transition_overlay(self):
        """关卡开场过渡动画：渐暗的黑幕 + STAGE 1 Ready! 文字"""
        alpha = min(255, int((self.transition_timer / self.transition_duration) * 255))
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(shade, (0, 0, 0, max(80, 220 - alpha)), shade.get_rect())
        screen.blit(shade, (0, 0))

        title = title_font.render(self.transition_text, True, WHITE)
        subtitle = small_font.render("Ready!", True, YELLOW)
        screen.blit(title,   (WIDTH // 2 - title.get_width() // 2,   HEIGHT // 2 - 40))
        screen.blit(subtitle,(WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 30))

    def draw_world(self):
        """渲染整个游戏世界：背景 → 平台 → 金币 → 敌人 → 旗帜 → 玩家 → HUD"""
        self.draw_background(screen)
        self.draw_ground_tiles(screen, self.camera_x)
        self.draw_platforms(screen, self.camera_x)
        self.draw_coins(screen, self.camera_x)
        self.draw_enemies(screen, self.camera_x)
        self.draw_flag(screen, self.camera_x)
        self.draw_player(screen, self.camera_x)
        self.draw_hud(screen)

        # 覆盖层（优先级最高，画在最上面）
        if self.game_state == "transition":
            self.draw_transition_overlay()
            return

        if self.game_state == "win":
            panel = pygame.Surface((460, 170), pygame.SRCALPHA)
            pygame.draw.rect(panel, (0, 0, 0, 180), panel.get_rect(), border_radius=18)
            screen.blit(panel, (WIDTH // 2 - 230, HEIGHT // 2 - 85))
            end_text  = title_font.render("LEVEL CLEAR!", True, YELLOW)
            hint_text = small_font.render("Click to return to the stage menu", True, WHITE)
            screen.blit(end_text,  (WIDTH // 2 - end_text.get_width() // 2,  HEIGHT // 2 - 20))
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 45))

        if self.game_state == "dead":
            panel = pygame.Surface((470, 170), pygame.SRCALPHA)
            pygame.draw.rect(panel, (0, 0, 0, 180), panel.get_rect(), border_radius=18)
            screen.blit(panel, (WIDTH // 2 - 235, HEIGHT // 2 - 85))
            over_text = title_font.render("GAME OVER", True, RED)
            hint_text = small_font.render("Click to return to the stage menu", True, WHITE)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 45))

    # ==================================================================== #
    # 主循环的 update / draw / 事件处理
    # ==================================================================== #

    def update(self):
        """每帧调用：根据当前 game_state 执行不同的更新逻辑"""
        # ---- 过渡动画阶段：只跑计时器 ---- #
        if self.game_state == "transition":
            self.transition_timer += 1
            if self.transition_timer >= self.transition_duration:
                self.game_state = "playing"   # 过渡结束 → 正式开始游戏
            return

        # ---- 正常游玩阶段 ---- #
        if self.game_state == "playing":
            if self.player.state != "dead" and not self.the_end:
                self.update_player()
                self.update_enemies()
            # 玩家死了 / 到达终点 → 自动切换游戏状态
            if self.player.state == "dead":
                self.game_state = "dead"
            if self.the_end:
                self.game_state = "win"

    def draw(self):
        """每帧调用：根据 game_state 画不同的画面"""
        if self.game_state == "start":
            self.draw_start_screen()       # 选关界面
        else:
            self.draw_world()              # 正常游戏画面（含 win/dead 遮罩）

    def handle_click(self, pos):
        """
        鼠标左键点击处理：
        - 选关界面 → 判断点中了哪个关卡按钮
        - win / dead → 回到选关界面
        返回 True 表示本次点击被处理了。
        """
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

# ==================================================================== #
# ⑤ 关卡数据 —— 3 个关卡的全部地图配置
#    每个关卡是一个字典，包含：
#      name         —— 关卡名（显示在选关卡片上）
#      world_width  —— 地图总宽度
#      flag_x       —— 终点旗帜的 x 坐标
#      platforms    —— 平台列表 [{"x","y","w","h"}, ...]
#      coins        —— 金币列表 [{"x","y","collected":False}, ...]
#      enemies      —— 敌人列表 [{"x","y","w","h","speed","dir","min_x","max_x","kind",...}, ...]
# ==================================================================== #

def prepare_level_data():

    # ---------- Stage 1 ---------- #
    level1 = {
        "name":         "Stage 1",
        "world_width":  2400,
        "flag_x":       2240,
        "platforms": [
            {"x": 0,    "y": GROUND_Y, "w": 700, "h": 90},   # 主地面分段（中间有断裂，制造坑）
            {"x": 760,  "y": GROUND_Y, "w": 640, "h": 90},
            {"x": 1500, "y": GROUND_Y, "w": 700, "h": 90},
            {"x": 2000, "y": GROUND_Y, "w": 400, "h": 90},
            # 空中平台（需要跳跃才能到达）
            {"x": 280,  "y": 400, "w": 140, "h": 28},
            {"x": 520,  "y": 350, "w": 130, "h": 28},
            {"x": 900,  "y": 310, "w": 150, "h": 28},
            {"x": 1180, "y": 260, "w": 140, "h": 28},
            {"x": 1700, "y": 340, "w": 160, "h": 28},
            {"x": 1950, "y": 290, "w": 140, "h": 28},
        ],
        "coins": [
            {"x": 140,  "y": 420, "collected": False},
            {"x": 330,  "y": 350, "collected": False},
            {"x": 570,  "y": 310, "collected": False},
            {"x": 950,  "y": 270, "collected": False},
            {"x": 1215, "y": 220, "collected": False},
            {"x": 1750, "y": 300, "collected": False},
            {"x": 2010, "y": 250, "collected": False},
            {"x": 2170, "y": 420, "collected": False},
        ],
        "enemies": [
            # 地面巡逻型 walker
            {"x": 900,  "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.4, "dir": 1,
             "min_x": 820, "max_x": 1210, "kind": "walker", "base_y": GROUND_Y - 30},
            # 跳跃型 jumper（每隔一会自动跳）
            {"x": 1660, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.6, "dir": -1,
             "min_x": 1550, "max_x": 1890, "kind": "jumper", "base_y": GROUND_Y - 30, "jump_v": 0.0},
            # 飞行型 flyer（空中上下浮动）
            {"x": 2130, "y": GROUND_Y - 80, "w": 30, "h": 30, "speed": 1.7, "dir": 1,
             "min_x": 2070, "max_x": 2320, "kind": "flyer",  "base_y": GROUND_Y - 100, "float_offset": 0.0},
        ],
    }

    # ---------- Stage 2 ---------- #
    level2 = {
        "name":         "Stage 2",
        "world_width":  2600,
        "flag_x":       2450,
        "platforms": [
            {"x": 0,    "y": GROUND_Y, "w": 650, "h": 90},
            {"x": 760,  "y": GROUND_Y, "w": 560, "h": 90},
            {"x": 1450, "y": GROUND_Y, "w": 650, "h": 90},
            {"x": 2200, "y": GROUND_Y, "w": 400, "h": 90},
            # 空中平台（数量更多、间距更疏）
            {"x": 240,  "y": 420, "w": 150, "h": 28},
            {"x": 520,  "y": 365, "w": 140, "h": 28},
            {"x": 830,  "y": 320, "w": 150, "h": 28},
            {"x": 1150, "y": 270, "w": 140, "h": 28},
            {"x": 1620, "y": 360, "w": 170, "h": 28},
            {"x": 1880, "y": 310, "w": 150, "h": 28},
            {"x": 2100, "y": 250, "w": 120, "h": 28},
        ],
        "coins": [
            {"x": 270,  "y": 380, "collected": False},
            {"x": 560,  "y": 325, "collected": False},
            {"x": 870,  "y": 280, "collected": False},
            {"x": 1190, "y": 230, "collected": False},
            {"x": 1660, "y": 320, "collected": False},
            {"x": 1920, "y": 270, "collected": False},
            {"x": 2130, "y": 210, "collected": False},
            {"x": 2320, "y": 420, "collected": False},
        ],
        "enemies": [
            {"x": 860,  "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.5, "dir": 1,
             "min_x": 790, "max_x": 1200, "kind": "walker", "base_y": GROUND_Y - 30},
            {"x": 1600, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.7, "dir": -1,
             "min_x": 1490, "max_x": 1870, "kind": "jumper", "base_y": GROUND_Y - 30, "jump_v": 0.0},
            {"x": 2220, "y": GROUND_Y - 80, "w": 30, "h": 30, "speed": 1.8, "dir": 1,
             "min_x": 2170, "max_x": 2420, "kind": "flyer",  "base_y": GROUND_Y - 120, "float_offset": 0.0},
        ],
    }

    # ---------- Stage 3（最终关） ---------- #
    level3 = {
        "name":         "Stage 3",
        "world_width":  2900,
        "flag_x":       2740,
        "platforms": [
            {"x": 0,    "y": GROUND_Y, "w": 620, "h": 90},
            {"x": 720,  "y": GROUND_Y, "w": 580, "h": 90},
            {"x": 1420, "y": GROUND_Y, "w": 650, "h": 90},
            {"x": 2200, "y": GROUND_Y, "w": 700, "h": 90},
            # 空中平台（间距更大，更考验二段跳）
            {"x": 250,  "y": 420, "w": 160, "h": 28},
            {"x": 540,  "y": 360, "w": 140, "h": 28},
            {"x": 860,  "y": 310, "w": 140, "h": 28},
            {"x": 1160, "y": 250, "w": 150, "h": 28},
            {"x": 1540, "y": 360, "w": 180, "h": 28},
            {"x": 1810, "y": 300, "w": 150, "h": 28},
            {"x": 2070, "y": 250, "w": 150, "h": 28},
            {"x": 2440, "y": 335, "w": 170, "h": 28},
        ],
        "coins": [
            {"x": 290,  "y": 380, "collected": False},
            {"x": 600,  "y": 320, "collected": False},
            {"x": 890,  "y": 270, "collected": False},
            {"x": 1210, "y": 210, "collected": False},
            {"x": 1590, "y": 320, "collected": False},
            {"x": 1850, "y": 260, "collected": False},
            {"x": 2115, "y": 210, "collected": False},
            {"x": 2490, "y": 295, "collected": False},
            {"x": 2650, "y": 420, "collected": False},
        ],
        "enemies": [
            {"x": 860,  "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.5, "dir": 1,
             "min_x": 760, "max_x": 1200, "kind": "walker", "base_y": GROUND_Y - 30},
            {"x": 1600, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.7, "dir": -1,
             "min_x": 1480, "max_x": 1880, "kind": "jumper", "base_y": GROUND_Y - 30, "jump_v": 0.0},
            {"x": 2250, "y": GROUND_Y - 80, "w": 30, "h": 30, "speed": 1.9, "dir": 1,
             "min_x": 2200, "max_x": 2540, "kind": "flyer",  "base_y": GROUND_Y - 120, "float_offset": 0.0},
            {"x": 2560, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.8, "dir": -1,
             "min_x": 2400, "max_x": 2850, "kind": "walker", "base_y": GROUND_Y - 30},
        ],
    }

    return [level1, level2, level3]

# ---------- 选关卡片上的提示文字 ---------- #
LEVEL_HINTS = {
    0: "Reach the flag and avoid the patrols.",
    1: "Use the floating ledges to gain height.",
    2: "The final route needs careful double-jumps.",
}

# ==================================================================== #
# ⑥ main 函数 & 程序入口
# ==================================================================== #

def main():
    """
    游戏主函数：
    - 创建 Game 实例
    - 进入主循环（每秒 60 帧）
    - 处理事件 → 更新逻辑 → 渲染画面
    - 关闭窗口时安全退出
    """
    game = Game()
    running = True

    while running:
        clock.tick(FPS)                             # 控制帧率，保证大约 60 FPS

        # ---------- 事件处理 ---------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # 点击窗口右上角关闭按钮
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)         # 鼠标左键点击 → 交给 Game 处理

        # ---------- 更新 & 渲染 ---------- #
        game.update()
        game.draw()
        pygame.display.flip()                       # 把画好的 Surface 显示到屏幕上（双缓冲）

    # ---------- 退出清理 ---------- #
    pygame.quit()
    sys.exit()

# 只有直接运行此文件时才启动游戏；被其他文件 import 时不启动
if __name__ == "__main__":
    main()