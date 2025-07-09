import numpy as np

class GameObject:
    def __init__(self, pos, obj_type):
        self.pos = np.array(pos)
        self.type = obj_type
        self.health = 500
        self.collected = False
        self.added_to_inventory = False
        self.move_timer = 0
        self.move_delay = 10  # Higher = slower ghost movement

    def get_distance(self, obj_pos, player_pos):
        return np.sqrt(np.sum((obj_pos - player_pos) ** 2))

    def interact(self, player_pos, tool=None, dungeon=None, TILE_FLOOR=None, player=None):
        distance = self.get_distance(self.pos, player_pos)

        if self.type == 'ghost':
            self.ghost_behavior(player_pos, dungeon, TILE_FLOOR, player)
            if distance < 5 and tool == 'bow':
                self.health -= 15

        elif self.type == 'tree' and distance < 2:
            if tool == 'axe':
                self.health -= 25
                if self.health <= 0:
                    self.collected = True

        elif self.type == 'loot' and distance < 2:
            self.collected = True

        elif self.type == 'wood' and distance <= 1:
            self.collected = True

    def ghost_behavior(self, player_pos, dungeon, TILE_FLOOR, player):
        distance = self.get_distance(self.pos, player_pos)
        self.move_timer += 1
        if distance < 6 and self.move_timer >= self.move_delay:
            direction = player_pos - self.pos
            step = np.clip(direction, -1, 1)
            new_pos = self.pos + step

            # Prevent ghosts from walking into walls
            if 0 <= new_pos[0] < dungeon.tiles.shape[1] and 0 <= new_pos[1] < dungeon.tiles.shape[0]:
                if dungeon.tiles[int(new_pos[1]), int(new_pos[0])] == TILE_FLOOR:
                    self.pos = new_pos

            # Damage the player if ghost gets too close
            if self.get_distance(self.pos, player_pos) <= 1.5 and player:
                player["health"] = max(0, player["health"] - 5)
                player["screen_shake"] = 5  # trigger screen shake when hit

            self.move_timer = 0

    def is_collectable(self):
        return self.collected and not self.added_to_inventory

    def mark_as_added_to_inventory(self):
        self.added_to_inventory = True

    def get_icon_key(self):
        return self.type if self.type in {"loot", "wood"} else None
