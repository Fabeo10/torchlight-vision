# camera.py
class Camera:
    def __init__(self, map_width, map_height, screen_width, screen_height, tile_size):
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size

        self.tiles_wide = screen_width // tile_size
        self.tiles_high = screen_height // tile_size

        self.x = 0
        self.y = 0

    def center_on(self, player_x, player_y):
        self.x = max(0, min(player_x - self.tiles_wide // 2, self.map_width - self.tiles_wide))
        self.y = max(0, min(player_y - self.tiles_high // 2, self.map_height - self.tiles_high))

    def to_screen(self, world_x, world_y):
        return (world_x - self.x) * self.tile_size, (world_y - self.y) * self.tile_size