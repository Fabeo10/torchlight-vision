import numpy as np

class GameObject:
    def __init__(self, pos, obj_type):
        self.pos = np.array(pos)
        self.type = obj_type
        self.health = 100
        self.collected = False

    def interact(self, player_pos):
        distance = np.linalg.norm(self.pos - player_pos)
        if self.type == 'enemy_projectile' and distance < 150:
            self.health -= 10
        elif self.type == 'enemy_sword' and distance < 50:
            self.health -= 20
        elif self.type == 'tree' and distance < 20:
            self.collected = True
        elif self.type == 'loot' and distance < 5:
            self.collected = True
