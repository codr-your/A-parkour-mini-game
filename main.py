import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Mario Adventure")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (210, 70, 70)
YELLOW = (255, 220, 80)
BLUE = (90, 150, 220)
SKY_TOP = (140, 210, 255)

font = pygame.font.SysFont("arial", 28, bold=True)
title_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 20, bold=True)
card_title_font = pygame.font.SysFont("arial", 36, bold=True)
card_help_font = pygame.font.SysFont("arial", 18, bold=True)

base_path = "assets"


def load_scaled(path, size):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)


player_idle = load_scaled(f"{base_path}/characters/platformChar_idle.png", (42, 52))
player_jump = load_scaled(f"{base_path}/characters/platformChar_jump.png", (42, 52))
player_walk1 = load_scaled(f"{base_path}/characters/platformChar_walk1.png", (42, 52))
player_walk2 = load_scaled(f"{base_path}/characters/platformChar_walk2.png", (42, 52))
coin_img = load_scaled(f"{base_path}/items/item_coin.png", (26, 26))

ground_tile = load_scaled(f"{base_path}/tiles/tile_ground.png", (64, 64))
grass_tile = load_scaled(f"{base_path}/tiles/tile_grass.png", (64, 64))
grass_mid = load_scaled(f"{base_path}/tiles/tile_grassMid.png", (64, 64))

GROUND_Y = 470


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
            {"x": 900, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.4, "dir": 1, "min_x": 820, "max_x": 1210},
            {"x": 1660, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.6, "dir": -1, "min_x": 1550, "max_x": 1890},
            {"x": 2130, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.7, "dir": 1, "min_x": 2070, "max_x": 2320},
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
            {"x": 860, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.5, "dir": 1, "min_x": 790, "max_x": 1200},
            {"x": 1600, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.7, "dir": -1, "min_x": 1490, "max_x": 1870},
            {"x": 2220, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.8, "dir": 1, "min_x": 2170, "max_x": 2420},
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
            {"x": 860, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.5, "dir": 1, "min_x": 760, "max_x": 1200},
            {"x": 1600, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.7, "dir": -1, "min_x": 1480, "max_x": 1880},
            {"x": 2250, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.9, "dir": 1, "min_x": 2200, "max_x": 2540},
            {"x": 2560, "y": GROUND_Y - 30, "w": 30, "h": 30, "speed": 1.8, "dir": -1, "min_x": 2400, "max_x": 2850},
        ],
    }

    return [level1, level2, level3]


LEVELS = prepare_level_data()
LEVEL_HINTS = {
    0: "Reach the flag and avoid the patrols.",
    1: "Use the floating ledges to gain height.",
    2: "The final route needs careful double-jumps.",
}
WORLD_WIDTH = LEVELS[0]["world_width"]

player = {
    "x": 80,
    "y": GROUND_Y - 52,
    "w": 42,
    "h": 52,
    "vx": 0,
    "vy": 0,
    "speed": 4.0,
    "jump": -13.5,
    "gravity": 0.65,
    "on_ground": True,
    "facing": 1,
    "anim_timer": 0,
    "lives": 3,
    "score": 0,
    "state": "idle",
    "jump_count": 0,
    "jump_lock": False,
}

platforms = []
coins = []
enemies = []
flag_x = 0
the_end = False
camera_x = 0
game_state = "start"
current_level_index = 0
level_buttons = []
start_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 80, 240, 60)


def reset_game():
    global camera_x, the_end
    player.update({
        "x": 80,
        "y": GROUND_Y - 52,
        "vx": 0,
        "vy": 0,
        "speed": 4.0,
        "jump": -13.5,
        "gravity": 0.65,
        "on_ground": True,
        "facing": 1,
        "anim_timer": 0,
        "lives": 3,
        "score": 0,
        "state": "idle",
        "jump_count": 0,
        "jump_lock": False,
    })
    for coin in coins:
        coin["collected"] = False
    for i, enemy in enumerate(enemies):
        enemy["x"] = enemy["min_x"] if i % 2 == 0 else enemy["max_x"]
        enemy["dir"] = 1 if i % 2 == 0 else -1
    camera_x = 0
    the_end = False


def player_rect(p):
    return pygame.Rect(p["x"], p["y"], p["w"], p["h"])


def draw_background(surface):
    surface.fill(SKY_TOP)
    for i in range(0, WIDTH + 200, 180):
        pygame.draw.rect(surface, (160, 210, 255), (i - 40, 110, 90, 50))
        pygame.draw.circle(surface, WHITE, (i, 100), 20)
        pygame.draw.circle(surface, WHITE, (i + 25, 100), 20)
        pygame.draw.circle(surface, WHITE, (i + 12, 80), 20)
    for i in range(0, WIDTH + 500, 220):
        pygame.draw.polygon(surface, (110, 140, 90), [(i, HEIGHT), (i + 70, 250), (i + 140, HEIGHT)])


def draw_ground_tiles(surface, world_x):
    for p in platforms:
        sx = p["x"] - world_x
        tile_w = ground_tile.get_width()
        if p["y"] >= GROUND_Y - 10:
            for i in range(0, p["w"], tile_w):
                surface.blit(ground_tile, (sx + i, p["y"]))
                surface.blit(grass_mid, (sx + i, p["y"] - 64))
        else:
            pygame.draw.rect(surface, (145, 130, 100), (sx, p["y"], p["w"], p["h"]))


def draw_platforms(surface, world_x):
    for p in platforms:
        sx = p["x"] - world_x
        if p["y"] >= GROUND_Y - 10:
            continue
        pygame.draw.rect(surface, (190, 160, 120), (sx, p["y"], p["w"], p["h"]))
        for tile_index in range(0, p["w"], 64):
            surface.blit(grass_tile, (sx + tile_index, p["y"]))


def draw_coins(surface, world_x):
    for coin in coins:
        if not coin["collected"]:
            surface.blit(coin_img, (coin["x"] - world_x, coin["y"]))


def draw_flag(surface, world_x):
    flag_x_screen = flag_x - world_x
    pygame.draw.rect(surface, WHITE, (flag_x_screen, 240, 6, 200))
    pygame.draw.polygon(surface, RED, [(flag_x_screen + 6, 240), (flag_x_screen + 6 + 60, 270), (flag_x_screen + 6, 300)])


def draw_enemies(surface, world_x):
    for enemy in enemies:
        if enemy["x"] < -100:
            continue
        pygame.draw.rect(surface, RED, (enemy["x"] - world_x, enemy["y"], enemy["w"], enemy["h"]))
        pygame.draw.circle(surface, BLACK, (int(enemy["x"] - world_x + 8), int(enemy["y"] + 8)), 4)
        pygame.draw.circle(surface, BLACK, (int(enemy["x"] - world_x + 22), int(enemy["y"] + 8)), 4)


def get_player_image():
    return player_idle


def draw_player(surface, world_x):
    px = player["x"] - world_x
    py = player["y"]
    if player["state"] == "dead":
        return
    img = get_player_image()
    img = pygame.transform.flip(img, player["facing"] == -1, False)
    surface.blit(img, (px, py))


def update_player():
    global camera_x, the_end
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player["vx"] = -player["speed"]
        player["facing"] = -1
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player["vx"] = player["speed"]
        player["facing"] = 1
    else:
        player["vx"] *= 0.8
        if abs(player["vx"]) < 0.1:
            player["vx"] = 0

    jump_pressed = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]
    if jump_pressed and not player["jump_lock"]:
        if player["on_ground"]:
            player["vy"] = player["jump"]
            player["on_ground"] = False
            player["jump_count"] = 1
        elif player["jump_count"] < 2:
            player["vy"] = player["jump"] * 0.9
            player["jump_count"] += 1
        player["jump_lock"] = True
    elif not jump_pressed:
        player["jump_lock"] = False

    if player["on_ground"]:
        player["vy"] = 0
    else:
        player["vy"] += player["gravity"]

    prev_x = player["x"]
    prev_y = player["y"]

    player["x"] += player["vx"]
    rect = player_rect(player)
    for p in platforms:
        pr = pygame.Rect(p["x"], p["y"], p["w"], p["h"])
        if rect.colliderect(pr):
            if prev_x + player["w"] <= pr.left + 10 and player["vx"] > 0:
                player["x"] = pr.left - player["w"]
            elif prev_x >= pr.right - 10 and player["vx"] < 0:
                player["x"] = pr.right
            player["vx"] = 0

    player["y"] += player["vy"]
    rect = player_rect(player)
    player["on_ground"] = False
    for p in platforms:
        pr = pygame.Rect(p["x"], p["y"], p["w"], p["h"])
        if rect.colliderect(pr):
            if prev_y + player["h"] <= pr.top + 18 and player["vy"] >= 0:
                player["y"] = pr.top - player["h"]
                player["vy"] = 0
                player["on_ground"] = True
                player["jump_count"] = 0
            elif prev_y >= pr.bottom - 18 and player["vy"] < 0:
                player["y"] = pr.bottom
                player["vy"] = 0

    if player["on_ground"]:
        player["vy"] = 0
        player["jump_count"] = 0

    player["state"] = "idle"

    if player["y"] > HEIGHT + 80:
        player["lives"] -= 1
        player["x"] = 80
        player["y"] = GROUND_Y - 52
        player["vx"] = 0
        player["vy"] = 0
        player["state"] = "idle"
        player["jump_count"] = 0
        camera_x = 0
        if player["lives"] <= 0:
            player["state"] = "dead"

    for coin in coins:
        if not coin["collected"]:
            c_rect = pygame.Rect(coin["x"], coin["y"], 26, 26)
            if rect.colliderect(c_rect):
                coin["collected"] = True
                player["score"] += 10

    for enemy in enemies:
        e_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["w"], enemy["h"])
        if rect.colliderect(e_rect):
            if player["vy"] > 0 and prev_y + player["h"] <= enemy["y"] + 10:
                player["vy"] = -10
                enemy["x"] = -999
            else:
                player["lives"] -= 1
                player["x"] = 80
                player["y"] = GROUND_Y - 52
                player["vx"] = 0
                player["vy"] = 0
                player["state"] = "idle"
                player["jump_count"] = 0
                camera_x = 0
                if player["lives"] <= 0:
                    player["state"] = "dead"
                break

    if player["x"] > flag_x:
        the_end = True

    camera_x = max(0, min(player["x"] - WIDTH * 0.35, WORLD_WIDTH - WIDTH))


def update_enemies():
    for enemy in enemies:
        enemy["x"] += enemy["speed"] * enemy["dir"]
        if enemy["x"] <= enemy["min_x"] or enemy["x"] >= enemy["max_x"]:
            enemy["dir"] *= -1


def draw_hud(surface):
    score_text = font.render(f"Score: {player['score']}", True, WHITE)
    life_text = font.render(f"Lives: {player['lives']}", True, WHITE)
    stage_text = font.render(f"Stage {current_level_index + 1}", True, WHITE)
    surface.blit(score_text, (20, 18))
    surface.blit(life_text, (20, 48))
    surface.blit(stage_text, (WIDTH - 180, 18))
    if the_end:
        win_text = font.render("LEVEL CLEAR!", True, YELLOW)
        surface.blit(win_text, (WIDTH // 2 - 90, 20))
    elif player["state"] == "dead":
        over_text = font.render("GAME OVER", True, RED)
        surface.blit(over_text, (WIDTH // 2 - 90, 20))


def draw_start_screen():
    screen.fill(BLUE)

    title_x = WIDTH // 2 - title_font.size("Mini Mario Adventure")[0] // 2
    title_y = 48
    shadow_text = title_font.render("Mini Mario Adventure", True, (60, 100, 150))
    screen.blit(shadow_text, (title_x + 4, title_y + 5))
    title_text = title_font.render("Mini Mario Adventure", True, WHITE)
    screen.blit(title_text, (title_x, title_y))

    subtitle_text = small_font.render("Choose a stage", True, WHITE)
    subtitle_x = WIDTH // 2 - subtitle_text.get_width() // 2
    subtitle_y = 142
    screen.blit(subtitle_text, (subtitle_x, subtitle_y))

    hint_text = small_font.render("Reach the flag and survive the patrols", True, WHITE)
    hint_x = WIDTH // 2 - hint_text.get_width() // 2
    hint_y = 180
    screen.blit(hint_text, (hint_x, hint_y))

    level_buttons.clear()
    card_x = WIDTH // 2 - 230
    card_width = 460
    start_y = 220
    card_h = 72
    card_gap = 14
    for index, level in enumerate(LEVELS):
        rect = pygame.Rect(card_x, start_y + index * (card_h + card_gap), card_width, card_h)
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        fill_color = (108, 178, 255) if hovered else (70, 130, 220)
        shadow_rect = rect.move(0, 7)
        pygame.draw.rect(screen, (50, 90, 150), shadow_rect, border_radius=14)
        pygame.draw.rect(screen, fill_color, rect, border_radius=14)
        pygame.draw.rect(screen, YELLOW, rect, 3, border_radius=14)

        name_text = card_title_font.render(level["name"], True, WHITE)
        screen.blit(name_text, (rect.x + 28, rect.y + 10))

        help_text = card_help_font.render(LEVEL_HINTS.get(index, "Reach the flag!"), True, WHITE)
        screen.blit(help_text, (rect.x + 28, rect.y + 48))
        level_buttons.append(rect)

    small_panel = pygame.Surface((200, 40), pygame.SRCALPHA)
    pygame.draw.rect(small_panel, (0, 0, 0, 80), small_panel.get_rect(), border_radius=12)
    screen.blit(small_panel, (WIDTH // 2 - 100, 490))


def main():
    global game_state, the_end
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "start":
                    for idx, rect in enumerate(level_buttons):
                        if rect.collidepoint(event.pos):
                            load_level(idx)
                            game_state = "playing"
                            break
                elif game_state in ("dead", "win"):
                    game_state = "start"
                    level_buttons.clear()

        if game_state == "playing":
            if player["state"] != "dead" and not the_end:
                update_player()
                update_enemies()
            if player["state"] == "dead":
                game_state = "dead"
            if the_end:
                game_state = "win"

        if game_state == "start":
            draw_start_screen()
        else:
            draw_background(screen)
            draw_ground_tiles(screen, camera_x)
            draw_platforms(screen, camera_x)
            draw_coins(screen, camera_x)
            draw_enemies(screen, camera_x)
            draw_flag(screen, camera_x)
            draw_player(screen, camera_x)
            draw_hud(screen)

            if game_state == "win":
                win_panel = pygame.Surface((420, 150), pygame.SRCALPHA)
                pygame.draw.rect(win_panel, (0, 0, 0, 180), win_panel.get_rect())
                screen.blit(win_panel, (WIDTH // 2 - 210, HEIGHT // 2 - 75))
                end_text = title_font.render("LEVEL CLEAR!", True, YELLOW)
                hint_text = small_font.render("Click to return to the stage menu", True, WHITE)
                screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 30))
                screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 30))

            if game_state == "dead":
                over_panel = pygame.Surface((440, 150), pygame.SRCALPHA)
                pygame.draw.rect(over_panel, (0, 0, 0, 180), over_panel.get_rect())
                screen.blit(over_panel, (WIDTH // 2 - 220, HEIGHT // 2 - 75))
                over_text = title_font.render("GAME OVER", True, RED)
                hint_text = small_font.render("Click to return to the stage menu", True, WHITE)
                screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
                screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def load_level(index):
    global platforms, coins, enemies, flag_x, WORLD_WIDTH, camera_x, the_end, current_level_index
    current_level_index = index
    level = LEVELS[index]
    platforms = [platform.copy() for platform in level["platforms"]]
    coins = [coin.copy() for coin in level["coins"]]
    enemies = [enemy.copy() for enemy in level["enemies"]]
    flag_x = level["flag_x"]
    WORLD_WIDTH = level["world_width"]
    camera_x = 0
    the_end = False
    reset_game()


if __name__ == "__main__":
    load_level(0)
    main()
