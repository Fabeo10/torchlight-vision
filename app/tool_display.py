# tool_display.py
import pygame

class ToolDisplay:
    def __init__(self, box_size=48):
        self.box_size = box_size
        self.surface = pygame.Surface((box_size, box_size), pygame.SRCALPHA)
        self.current_tool = None

    def set_tool(self, tool_image):
        self.current_tool = pygame.transform.scale(tool_image, (self.box_size, self.box_size))

    def draw(self):
        self.surface.fill((0, 0, 0, 0))  # Clear previous frame
        rect = pygame.Rect(0, 0, self.box_size, self.box_size)
        pygame.draw.rect(self.surface, (255, 255, 255), rect, 2)  # Outline
        if self.current_tool:
            self.surface.blit(self.current_tool, (0, 0))
        return self.surface

    def get_surface(self):
        return self.surface
