import numpy as np
import pygame

class FogOfWar:
    def __init__(self, map_size, tile_size):
        self.map_size = map_size
        self.tile_size = tile_size
        self.explored = np.zeros((map_size[1], map_size[0]), dtype=bool)  # shape = (height, width)

    def update(self, player_tile, light_radius):
        # correct index order: [y, x] for height/width alignment
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                dx = x - player_tile[0]
                dy = y - player_tile[1]
                if dx * dx + dy * dy <= light_radius * light_radius:
                    self.explored[y, x] = True 

    def draw_minimap(self, screen, dungeon, TILE_WALL, TILE_FLOOR, pos=(10, 10), scale=4):
        h, w = self.map_size[1], self.map_size[0]
        tile_colors = np.zeros((h, w, 3), dtype=np.uint8)

        # Transpose dungeon tiles to match minimap shape (h, w)
        tiles = dungeon.tiles  # (h, w)
        tile_colors[tiles == TILE_WALL] = (40, 40, 40)
        tile_colors[tiles == TILE_FLOOR] = (150, 150, 150)

        # Apply explored mask (broadcasted to 3 channels)
        mask = np.expand_dims(self.explored, axis=-1)
        tile_colors = tile_colors * mask

        # Upscale by repeating pixels 
        scaled = np.repeat(np.repeat(tile_colors, scale, axis=0), scale, axis=1)

        # Draw to pygame
        surf = pygame.Surface((w * scale, h * scale))
        pygame.surfarray.blit_array(surf, scaled.swapaxes(0, 1))
        screen.blit(surf, pos)
