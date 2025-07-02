import numpy as np
import pygame

class FogOfWar:
    def __init__(self, map_size, tile_size):
        self.map_size = map_size
        self.tile_size = tile_size
        self.explored = np.zeros(map_size, dtype=bool)

    def update(self, player_tile, light_radius):
        for x in range(self.map_size[0]):
            for y in range(self.map_size[1]):
                dx = x - player_tile[0]
                dy = y - player_tile[1]
                if dx * dx + dy * dy <= light_radius * light_radius:
                    self.explored[x, y] = True


    def draw_minimap(self, screen):
        for x in range(self.map_size[0]):
            for y in range(self.map_size[1]):
                rect = pygame.Rect(10 + x * 4, 10 + y * 4, 4, 4)  # small tiles
                if self.explored[x, y]:
                    pygame.draw.rect(screen, (100, 255, 100), rect)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), rect)
