# dungeon.py
import numpy as np

TILE_WALL = 0
TILE_FLOOR = 1

class Dungeon:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = np.full((height, width), TILE_WALL, dtype=np.uint8)
        self.rooms = []
        self.generate()

    def generate(self, room_attempts=20, min_size=6, max_size=12):
        for _ in range(room_attempts):
            w = np.random.randint(min_size, max_size + 1)
            h = np.random.randint(min_size, max_size + 1)
            x = np.random.randint(1, self.width - w - 1)
            y = np.random.randint(1, self.height - h - 1)
            new_room = (x, y, w, h)

            if any(self.intersect(new_room, r) for r in self.rooms):
                continue
            self.create_room(new_room)
            if self.rooms:
                prev_x, prev_y = self.center(self.rooms[-1])
                new_x, new_y = self.center(new_room)
                self.connect_rooms(prev_x, prev_y, new_x, new_y)

            self.rooms.append(new_room)

    def create_room(self, room):
        x, y, w, h = room
        self.tiles[y:y+h, x:x+w] = TILE_FLOOR

    def center(self, room):
        x, y, w, h = room
        return x + w // 2, y + h // 2

    def intersect(self, r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return (x1 <= x2 + w2 and x1 + w1 >= x2 and
                y1 <= y2 + h2 and y1 + h1 >= y2)

    def connect_rooms(self, x1, y1, x2, y2):
        if np.random.random() < 0.5:
            self.create_h_tunnel(x1, x2, y1)
            self.create_v_tunnel(y1, y2, x2)
        else:
            self.create_v_tunnel(y1, y2, x1)
            self.create_h_tunnel(x1, x2, y2)

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[y, x] = TILE_FLOOR

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[y, x] = TILE_FLOOR