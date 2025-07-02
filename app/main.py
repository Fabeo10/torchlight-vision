# main.py
import numpy as np
import pygame
from .dungeon import Dungeon
from .camera import Camera
from .dungeon import TILE_WALL, TILE_FLOOR
from .hand_detection import HandDetector
from .game_objects import GameObject
from .minimap import FogOfWar
from .effects import draw_object_effect, death_counters, sparkle_counters

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 24
MAP_WIDTH, MAP_HEIGHT = 60, 45
FPS = 30
LIGHT_RADIUS = 7  # in tiles

# --- Colors ---
COLOR_WALL = (40, 40, 40)
COLOR_FLOOR = (150, 150, 150)
COLOR_PLAYER = (0, 0, 255)

import cv2

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Torchlit Dungeon Crawler")
clock = pygame.time.Clock()

# Initialize dungeon
dungeon = Dungeon(MAP_WIDTH, MAP_HEIGHT)
start_x, start_y = dungeon.center(dungeon.rooms[0])
player_tile = np.array([start_x, start_y])
target_tile = player_tile.copy()
camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)

# Initialize objects
room_cx, room_cy = dungeon.center(dungeon.rooms[1])
objects = [
    GameObject((room_cx - 2, room_cy), 'enemy_projectile'),
    GameObject((room_cx + 2, room_cy), 'enemy_projectile'),
    GameObject((room_cx, room_cy - 2), 'tree'),
    GameObject((room_cx, room_cy + 2), 'tree'),
    GameObject((room_cx - 2, room_cy - 2), 'loot'),
    GameObject((room_cx + 2, room_cy + 2), 'loot')
]

fog = FogOfWar(map_size=(MAP_WIDTH, MAP_HEIGHT), tile_size=TILE_SIZE)
hand_detector = HandDetector()

# Torch flicker setup
flicker_angle = 0
flicker_speed = 0.1
flicker_amplitude = 1.0  # tile units
show_minimap = True
recording = False

# Setup OpenCV video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('game_capture.avi', fourcc, FPS, (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Main Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill((0, 0, 0))

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
    player_tile = target_tile.copy()

    # Center camera on player
    camera.center_on(*player_tile)

    # Determine torch status before drawing
    hand_present = hand_detector.is_hand_detected()
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
                pygame.draw.rect(screen, color, (sx, sy, TILE_SIZE, TILE_SIZE))

    # Draw fog of war before objects
    if hasattr(fog, 'draw'):
        fog.draw(screen, camera)

    # Object interaction and rendering
    updated_objects = []
    for obj in objects:
        obj.interact(player_tile)
        draw_object_effect(screen, obj, camera, TILE_SIZE)

        # Draw CV-style bounding box and label for visible objects
        sx, sy = camera.to_screen(*obj.pos)
        rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

        if obj.type == 'enemy_projectile':
            label_color = (255, 0, 0)
        elif obj.type == 'tree':
            label_color = (0, 255, 0)
        elif obj.type == 'loot':
            label_color = (255, 255, 0)
        else:
            label_color = (255, 255, 255)

        if 0 <= sx < SCREEN_WIDTH and 0 <= sy < SCREEN_HEIGHT:
            pygame.draw.rect(screen, label_color, rect, 1)
            font = pygame.font.SysFont(None, 16)
            label = font.render(obj.type, True, label_color)
            screen.blit(label, (sx, sy - 10))
        pos_key = tuple(obj.pos)

        if (obj.type == 'enemy_projectile' and obj.health <= 0 and pos_key not in death_counters) or \
           (obj.type == 'tree' and obj.collected and pos_key not in death_counters) or \
           (obj.type == 'loot' and obj.collected and pos_key not in sparkle_counters):
            continue  # skip fully expired object

        updated_objects.append(obj)

    objects = updated_objects

    # Draw player
    px, py = camera.to_screen(*player_tile)
    pygame.draw.rect(screen, COLOR_PLAYER, (px, py, TILE_SIZE, TILE_SIZE))

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
        fog.draw_minimap(screen)

    pygame.display.flip()

    # Capture frame to OpenCV video
    if recording:
        frame_str = pygame.image.tostring(screen, 'RGB')
        frame_np = np.frombuffer(frame_str, dtype=np.uint8).reshape((SCREEN_HEIGHT, SCREEN_WIDTH, 3))
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)

hand_detector.stop()
out.release()
pygame.quit()
