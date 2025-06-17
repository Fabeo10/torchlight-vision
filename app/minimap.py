import numpy as np
import pygame

class FogOfWar:
    def __init__(self, map_size, tile_size):
        self.map_size = map_size
        self.tile_size = tile_size
        self.explored = np.zeros(map_size, dtype=bool)

    def update(self, player_pos, light_radius):
        for x in range(self.map_size[0]):
            for y in range(self.map_size[1]):
                tile_pos = np.array([x * self.tile_size, y * self.tile_size])
                if np.linalg.norm(player_pos - tile_pos) <= light_radius:
                    self.explored[x, y] = True

    def draw_minimap(self, screen):
        for x in range(self.map_size[0]):
            for y in range(self.map_size[1]):
                rect = pygame.Rect(10 + x * 4, 10 + y * 4, 4, 4)  # small tiles
                if self.explored[x, y]:
                    pygame.draw.rect(screen, (100, 255, 100), rect)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), rect)
