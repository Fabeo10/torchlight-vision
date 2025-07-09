# main.py
import numpy as np
import pygame
import time
import cv2 as cv
from .dungeon import Dungeon
from .camera import Camera
from .dungeon import TILE_WALL, TILE_FLOOR
from .hand_detection import HandDetector
from .game_objects import GameObject
from .minimap import FogOfWar
from .effects import draw_object_effect, death_counters, sparkle_counters
from .sprite_loader import SpriteSheet
from .inventory import Inventory
from .tool_display import ToolDisplay


# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 24
MAP_WIDTH, MAP_HEIGHT = 60, 45
FPS = 15
LIGHT_RADIUS = 7  # in tiles

# --- Colors ---
COLOR_WALL = (40, 40, 40)
COLOR_FLOOR = (150, 150, 150)
COLOR_PLAYER = (0, 0, 255)

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Torchlit Dungeon Crawler")
clock = pygame.time.Clock()

# Load sprite sheets
player_sprite_sheet = SpriteSheet("assets/player_ready.png", frame_width=24, frame_height=24)
tree_sprite_sheet = SpriteSheet("assets/tree_idle_ready.png", frame_width=24, frame_height=24)
coin_icon = pygame.image.load("assets/coin_ready.png").convert_alpha()
wood_icon = pygame.image.load("assets/wood_ready.png").convert_alpha()
axe_icon = pygame.image.load("assets/axe_24.png").convert_alpha()
bow_icon = pygame.image.load("assets/bow_ready.png").convert_alpha()
lantern_icon = pygame.transform.scale(pygame.image.load("assets/lantern_ready.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
ghost_icon = pygame.image.load("assets/ghost_ready.png").convert_alpha()

# Initialize player 
player_status = {"health": 100, "screen_shake": 0}


# Initialize dungeon
dungeon = Dungeon(MAP_WIDTH, MAP_HEIGHT)
start_x, start_y = dungeon.center(dungeon.rooms[0])
player_tile = np.array([start_x, start_y])
target_tile = player_tile.copy()
camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)

objects = []

# initialize objects
# Exclude the starting room (index 0)
for i, room in enumerate(dungeon.rooms[1:], start=1):
    rx, ry = dungeon.center(room)
    placed = set()

    for _ in range(np.random.randint(2, 4)):  # Place 2–4 objects per room
        obj_type = np.random.choice(['ghost', 'tree', 'loot'])
        dx, dy = np.random.randint(-2, 2), np.random.randint(-2, 2)
        pos = (rx + dx, ry + dy)

        # Avoid placing multiple objects on same tile
        if pos not in placed and 0 <= pos[0] < MAP_WIDTH and 0 <= pos[1] < MAP_HEIGHT:
            if dungeon.tiles[pos[1], pos[0]] == TILE_FLOOR:
                objects.append(GameObject(pos, obj_type))
                placed.add(pos)


fog = FogOfWar(map_size=(MAP_WIDTH, MAP_HEIGHT), tile_size=TILE_SIZE)
hand_detector = HandDetector()
inventory = Inventory()

last_toggle_time = 0.0
tool_selected = 'axe'  # Default tool
tool_toggle_state = False
prev_hand_piece = False

# --- NEW: Setup tool display ---
tool_display = ToolDisplay()
tool_display.set_tool(axe_icon)

# Torch flicker setup
flicker_angle = 0
flicker_speed = 0.1
flicker_amplitude = 1.0  # tile units
show_minimap = True
recording = False
frame_index = 0

# Setup OpenCV video writer
fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter('game_capture.mp4', fourcc, FPS, (SCREEN_WIDTH, SCREEN_HEIGHT))
hand_out = None
hand_frame = None

# --- Main Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill((0, 0, 0))
    frame_index = (frame_index + 1) % player_sprite_sheet.num_frames

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_w:
                target_tile[1] -= 1
            elif event.key == pygame.K_s:
                target_tile[1] += 1
            elif event.key == pygame.K_a:
                target_tile[0] -= 1
            elif event.key == pygame.K_d:
                target_tile[0] += 1
            elif event.key == pygame.K_m:
                show_minimap = not show_minimap
            elif event.key == pygame.K_r:
                recording = not recording
                print(f"Recording {'started' if recording else 'stopped'}.")

    target_tile[0] = np.clip(target_tile[0], 0, MAP_WIDTH - 1)
    target_tile[1] = np.clip(target_tile[1], 0, MAP_HEIGHT - 1)

    # Prevent walking through walls
    if dungeon.tiles[target_tile[1], target_tile[0]] == TILE_FLOOR:
        player_tile = target_tile.copy()


    hand_present = hand_detector.is_hand_detected()  # for torchlight
    hand_piece = hand_detector.is_hand_piece()
    hand_frame = hand_detector.get_latest_frame()

    # New toggle logic
    if hand_present:
        if hand_piece and not prev_hand_piece:
            if time.time() - last_toggle_time > 0.5:
                tool_toggle_state = not tool_toggle_state
                tool_selected = 'bow' if tool_toggle_state else 'axe'  
                tool_display.set_tool(bow_icon if tool_toggle_state else axe_icon)
                last_toggle_time = time.time()
        prev_hand_piece = hand_piece
    else:
        prev_hand_piece = False

    # Apply screen shake offset if player gets
    shake_offset = np.random.randint(-4, 5, size=2) if player_status.get("screen_shake", 0) > 0 else np.array([0, 0])
    player_status["screen_shake"] = max(0, player_status["screen_shake"] - 1)


    # Center camera on player
    camera.center_on(*player_tile)

    # Determine torch status before drawing
    if hand_present:
        flicker_angle += flicker_speed
        flicker = flicker_amplitude * np.sin(flicker_angle)
        torch_radius = LIGHT_RADIUS + flicker
        fog.update(player_tile, int(torch_radius))
    else:
        torch_radius = 0

    # Draw dungeon
    for y in range(camera.y, camera.y + camera.tiles_high):
        for x in range(camera.x, camera.x + camera.tiles_wide):
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                tile = dungeon.tiles[y, x]
                color = COLOR_WALL if tile == TILE_WALL else COLOR_FLOOR
                sx, sy = camera.to_screen(x, y)
                sx += shake_offset[0]
                sy += shake_offset[1]
                pygame.draw.rect(screen, color, (sx, sy, TILE_SIZE, TILE_SIZE))

    # Object interaction and rendering
    updated_objects = []
    new_objects = []
    for obj in objects:
        prev_health = obj.health
        obj.interact(player_tile, tool_selected, dungeon, TILE_FLOOR, player_status)
        draw_object_effect(screen, obj, camera, TILE_SIZE)

        if obj.type == 'tree' and obj.collected and not hasattr(obj, 'dropped'):
            drop_count = np.random.randint(1, 4)
            possible_offsets = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3)
                                if np.abs(dx) + np.abs(dy) <= 2 and not (dx == 0 and dy == 0)]
            np.random.shuffle(possible_offsets)
            for dx, dy in possible_offsets[:drop_count]:
                wood_pos = obj.pos + np.array([dx, dy])
                new_objects.append(GameObject(wood_pos, 'wood'))
            obj.dropped = True

        # apply offsets to player or enemies if that specific object was hit
        shake_offset = np.random.randint(-2, 3, size=2) if obj.health < prev_health else np.array([0, 0])
        sx, sy = camera.to_screen(*obj.pos)
        sx += shake_offset[0]
        sy += shake_offset[1]
        draw_x, draw_y = sx, sy
        rect = pygame.Rect(draw_x, draw_y, TILE_SIZE, TILE_SIZE)

        if obj.type == 'tree':
            frame = tree_sprite_sheet.get_frame(frame_index)
            screen.blit(frame, (draw_x, draw_y))
            if obj.health > 0:
                pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y - 6, TILE_SIZE * (obj.health / 500), 4))
        elif obj.type == 'ghost':
            frame = ghost_icon
            screen.blit(frame, (draw_x, draw_y))
            if obj.health > 0:
                pygame.draw.rect(screen, (255, 0, 0), (draw_x, draw_y - 6, TILE_SIZE * (obj.health / 500), 4))
        elif obj.type in ("loot", "wood"):
            if obj.type == "wood":
                screen.blit(wood_icon, (draw_x, draw_y))
            inventory.handle_pickup(obj, camera, (SCREEN_WIDTH, SCREEN_HEIGHT), {
                "loot": coin_icon,
                "wood": wood_icon
            })

        font = pygame.font.SysFont(None, 16)
        label_color = (255, 255, 255)
        label = font.render(f"{obj.type}", True, label_color)
        screen.blit(label, (draw_x, draw_y - 18))
        pos_key = tuple(obj.pos)

        if (obj.type == 'ghost' and obj.health <= 0 and pos_key not in death_counters) or \
           (obj.type == 'tree' and obj.collected and pos_key not in death_counters) or \
           (obj.type in ('loot', 'wood') and obj.collected and pos_key not in sparkle_counters):
            continue

        updated_objects.append(obj)

    objects = updated_objects + new_objects

    # Draw player
    px, py = camera.to_screen(*player_tile)
    px += shake_offset[0]
    py += shake_offset[1]
    player_frame = player_sprite_sheet.get_frame(frame_index)
    screen.blit(player_frame, (px, py))

    # Lighting Mask
    light_mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    if hand_present:
        light_mask.fill((0, 0, 0, 200))
        pygame.draw.circle(light_mask, (0, 0, 0, 0), (px + TILE_SIZE//2, py + TILE_SIZE//2), int(torch_radius * TILE_SIZE))
    else:
        light_mask.fill((0, 0, 0, 200))
    screen.blit(light_mask, (0, 0))

    # Minimap toggleable
    if show_minimap:
        fog.draw_minimap(screen, dungeon, TILE_WALL, TILE_FLOOR)

    # Draw inventory at the bottom of the screen
    inv_surface = inventory.draw()
    screen.blit(inv_surface, (SCREEN_WIDTH//2 - inv_surface.get_width()//2, SCREEN_HEIGHT - inv_surface.get_height() - 8))

    # Draw current tool icon on the bottom-left corner
    tool_surface = tool_display.draw()
    tool_x = 8
    tool_y = SCREEN_HEIGHT - tool_surface.get_height() - 8
    screen.blit(tool_surface, (tool_x, tool_y))

    # Draw lantern icon above the tool if hand is detected
    if hand_present:
        lantern_surface = pygame.transform.scale(lantern_icon, (tool_surface.get_width(), tool_surface.get_height()))
        lantern_y = tool_y - lantern_surface.get_height() - 4
        screen.blit(lantern_surface, (tool_x, lantern_y))

    # Draw player health status
    bar_width = 200
    bar_height = 20
    bar_x = SCREEN_WIDTH - bar_width - 70
    bar_y = 20
    health_ratio = player_status["health"] / 100

    # Background bar (gray)
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    # Health fill (green)
    pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))

    # Health text (red)
    font = pygame.font.SysFont(None, 20)
    health_text = font.render(f"{player_status['health']} HP", True, (255, 0, 0))
    screen.blit(health_text, (bar_x + bar_width + 8, bar_y))

    pygame.display.flip()

    # Save video frame if recording
    if recording:
        frame_str = pygame.image.tostring(screen, 'RGB')
        frame_np = np.frombuffer(frame_str, dtype=np.uint8).reshape((SCREEN_HEIGHT, SCREEN_WIDTH, 3))
        frame_bgr = cv.cvtColor(frame_np, cv.COLOR_RGB2BGR)
        out.write(frame_bgr)

        if hand_frame is not None:
            if hand_out is None:
                h, w = hand_frame.shape[:2]
                hand_out = cv.VideoWriter('hand_capture.mp4', fourcc, FPS, (w, h))
            hand_out.write(hand_frame)

hand_detector.stop()
out.release()
if hand_out:
    hand_out.release()
pygame.quit()
