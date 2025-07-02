# effects.py
import pygame

COLOR_TREE = (0, 255, 0)
COLOR_LOOT = (255, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_FLASH = (255, 100, 100)
COLOR_FADE = (100, 0, 0)

flash_duration = 10
sparkle_duration = 10
death_fade_duration = 20

flash_counters = {}
sparkle_counters = {}
death_counters = {}

def draw_object_effect(screen, obj, camera, tile_size):
    pos_key = tuple(obj.pos)
    sx, sy = camera.to_screen(*obj.pos)
    center = (sx + tile_size // 2, sy + tile_size // 2)

    # Enemy flash + death dissolve
    if obj.type == 'enemy_projectile':
        if obj.health > 0:
            if pos_key not in flash_counters:
                flash_counters[pos_key] = flash_duration
            else:
                flash_counters[pos_key] = max(0, flash_counters[pos_key] - 1)

            if flash_counters[pos_key] > 0:
                pygame.draw.circle(screen, COLOR_FLASH, center, tile_size // 3)
            else:
                pygame.draw.circle(screen, COLOR_ENEMY, center, tile_size // 3)
        else:
            if pos_key not in death_counters:
                death_counters[pos_key] = death_fade_duration
            else:
                death_counters[pos_key] -= 1

            fade = max(0, death_counters[pos_key]) / death_fade_duration
            faded_color = tuple(int(c * fade) for c in COLOR_FADE)
            pygame.draw.circle(screen, faded_color, center, int((tile_size // 3) * fade))

            if death_counters[pos_key] <= 0:
                death_counters.pop(pos_key, None)
                flash_counters.pop(pos_key, None)

    # Tree chop animation (shrink)
    elif obj.type == 'tree':
        if not obj.collected:
            pygame.draw.circle(screen, COLOR_TREE, center, tile_size // 3)
        else:
            if pos_key not in death_counters:
                death_counters[pos_key] = death_fade_duration
            else:
                death_counters[pos_key] -= 1

            fade = max(0, death_counters[pos_key]) / death_fade_duration
            pygame.draw.circle(screen, COLOR_TREE, center, int((tile_size // 3) * fade))

            if death_counters[pos_key] <= 0:
                death_counters.pop(pos_key, None)

    # Loot sparkle + pickup burst
    elif obj.type == 'loot':
        if not obj.collected:
            frame = pygame.time.get_ticks() // 200 % 2
            radius = tile_size // 4 + (1 if frame == 0 else 0)
            pygame.draw.circle(screen, COLOR_LOOT, center, radius)
        else:
            if pos_key not in sparkle_counters:
                sparkle_counters[pos_key] = sparkle_duration

            if sparkle_counters[pos_key] > 0:
                sparkle_counters[pos_key] -= 1
                burst_radius = int((tile_size // 4) + 2 * (sparkle_duration - sparkle_counters[pos_key]))
                pygame.draw.circle(screen, COLOR_LOOT, center, burst_radius, 2)
            else:
                sparkle_counters.pop(pos_key, None)

    # Clean flash state for removed objects
    if obj.health <= 0 or obj.collected:
        flash_counters.pop(pos_key, None)
