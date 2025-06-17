import numpy as np
import pygame
from .hand_detection import HandDetector
from .game_objects import GameObject
from .minimap import FogOfWar

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
LIGHT_RADIUS = 100

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Torchlit Dungeon Crawler")
clock = pygame.time.Clock()

player_pos = np.array([WIDTH // 2, HEIGHT // 2])
objects = [
    GameObject((300, 300), 'enemy_projectile'),
    GameObject((500, 400), 'tree'),
    GameObject((600, 200), 'loot')
]

fog = FogOfWar(map_size=(20, 15), tile_size=40)
hand_detector = HandDetector()

# --- Torch Flicker Variables ---
flicker_angle = 0           # Angle for sine wave
flicker_speed = 0.1         # Smaller = slower flicker
flicker_amplitude = 5       # Max +/- pixels added to radius

# --- Main Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill((100, 100, 100))  # Background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player_pos = np.array(pygame.mouse.get_pos())

    # Interactions
    for obj in objects:
        obj.interact(player_pos)
        if obj.type == 'enemy_projectile' and obj.health > 0:
            pygame.draw.circle(screen, (255, 0, 0), obj.pos, 10)
        elif obj.type == 'tree' and not obj.collected:
            pygame.draw.circle(screen, (0, 255, 0), obj.pos, 10)
        elif obj.type == 'loot' and not obj.collected:
            pygame.draw.circle(screen, (255, 255, 0), obj.pos, 5)

    # Player
    pygame.draw.circle(screen, (0, 0, 255), player_pos, 10)

    # Torch logic
    hand_present = hand_detector.is_hand_detected()

    if hand_present:
        # Smooth flicker
        flicker_angle += flicker_speed
        flicker = int(flicker_amplitude * np.sin(flicker_angle))
        torch_radius = LIGHT_RADIUS + flicker

        # Create lighting mask — fully dark everywhere
        light_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        light_mask.fill((0, 0, 0, 150))  # Global darkness

        # Cut a clear circle for torchlight
        pygame.draw.circle(light_mask, (0, 0, 0, 0), player_pos, torch_radius)
        pygame.draw.circle(light_mask, (0, 0, 0, 80), player_pos, torch_radius + 40)

        screen.blit(light_mask, (0, 0))
        fog.update(player_pos, torch_radius)
    else:
        # No torch → just use full dim mask
        dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_mask.fill((0, 0, 0, 150))
        screen.blit(dim_mask, (0, 0))


    # Minimap
    fog.draw_minimap(screen)

    pygame.display.flip()

# Cleanup
hand_detector.stop()
pygame.quit()
