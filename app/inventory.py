import pygame
import numpy as np
import time

class Inventory:
    def __init__(self, slot_count=9, slot_size=48):
        self.slot_count = slot_count
        self.slot_size = slot_size
        self.items = [None] * slot_count  # Holds surfaces of item icons
        self.surface = pygame.Surface((slot_size * slot_count, slot_size), pygame.SRCALPHA)
        self.animations = []  # list of (start_time, duration, image, start_pos, end_pos)

    def add_item(self, item_image, start_pos=None):
        for i in range(self.slot_count):
            if self.items[i] is None:
                self.items[i] = item_image

                if start_pos is not None:
                    end_x = i * self.slot_size
                    end_y = 0
                    animation = {
                        'start_time': time.time(),
                        'duration': 0.5,
                        'image': item_image,
                        'start_pos': start_pos,
                        'end_pos': (end_x, end_y)
                    }
                    self.animations.append(animation)
                return  # Only add once

    def remove_item(self, index):
        if 0 <= index < self.slot_count:
            self.items[index] = None

    def draw(self):
        self.surface.fill((0, 0, 0, 0))
        now = time.time()

        # Draw inventory slots and static icons
        for i in range(self.slot_count):
            x = i * self.slot_size
            rect = pygame.Rect(x, 0, self.slot_size, self.slot_size)
            pygame.draw.rect(self.surface, (255, 255, 255), rect, 2)
            if self.items[i] is not None:
                icon = pygame.transform.scale(self.items[i], (self.slot_size, self.slot_size))
                self.surface.blit(icon, (x, 0))

        # Draw any flying animated items
        finished = []
        for anim in self.animations:
            elapsed = now - anim['start_time']
            t = min(elapsed / anim['duration'], 1.0)

            start_x, start_y = anim['start_pos']
            end_x, end_y = anim['end_pos']

            # Easing (ease-out cubic)
            ease_t = 1 - (1 - t)**3
            x = start_x + (end_x - start_x) * ease_t
            y = start_y + (end_y - start_y) * ease_t

            icon = pygame.transform.scale(anim['image'], (self.slot_size, self.slot_size))
            self.surface.blit(icon, (x, y))

            if t >= 1.0:
                finished.append(anim)

        # Clean up finished animations
        for anim in finished:
            self.animations.remove(anim)

        return self.surface

    def get_surface(self):
        return self.surface

    def get_numpy_view(self):
        view = pygame.surfarray.array3d(self.surface)
        return np.moveaxis(view, 0, 1)
    
    def handle_pickup(self, obj, camera, screen_size, icon_lookup):
        if not obj.is_collectable():
            return

        screen_pos = camera.to_screen(*obj.pos)
        inv_offset = (
            screen_size[0] // 2 - self.surface.get_width() // 2,
            screen_size[1] - self.surface.get_height() - 8
        )
        inv_relative_pos = (screen_pos[0] - inv_offset[0], screen_pos[1] - inv_offset[1])

        item_type = obj.get_icon_key()
        item_icon = icon_lookup.get(item_type)

        if item_icon:
            self.add_item(item_icon, start_pos=inv_relative_pos)
            obj.mark_as_added_to_inventory()

