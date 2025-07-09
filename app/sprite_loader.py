import pygame

class SpriteSheet:
    def __init__(self, image_path, frame_width, frame_height):
        self.sheet = pygame.image.load(image_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = self.load_frames()
        self.num_frames = len(self.frames)  # <-- ADD THIS LINE

    def load_frames(self):
        sheet_width, sheet_height = self.sheet.get_size()
        frames = []
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
                if rect.right <= sheet_width and rect.bottom <= sheet_height:
                    frames.append(self.sheet.subsurface(rect))
        return frames

    def get_frame(self, index):
        return self.frames[index % len(self.frames)]
