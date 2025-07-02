import numpy as np

class GameObject:
    def __init__(self, pos, obj_type):
        self.pos = np.array(pos)
        self.type = obj_type
        self.health = 100
        self.collected = False

    def get_distance(self, obj_pos, player_pos):
       return np.sqrt(np.sum((obj_pos-player_pos)**2))

    def interact(self, player_pos):
        distance = self.get_distance(self.pos, player_pos)
        if self.type == 'enemy_projectile' and distance < 5:
            self.health -= 10
        elif self.type == 'enemy_sword' and distance < 1.5:
            self.health -= 20
        elif self.type == 'tree' and distance < 2:
            self.collected = True
        elif self.type == 'loot' and distance < 2:
            self.collected = True

