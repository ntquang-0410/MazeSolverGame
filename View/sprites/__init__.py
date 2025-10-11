"""
Sprite Components
Animated sprites for game objects (Monkey, Banana)
"""
import pygame
import math


class FloatingBanana(pygame.sprite.Sprite):
    """Animated floating banana sprite with shadow"""
    
    def __init__(self, image, cell_size):
        super().__init__()
        self.base_image = image
        self.cell_size = cell_size
        self.image = image
        self.rect = self.image.get_rect()
        self.t = 0.0
        self.offset = (0, 0)

    def update(self, dt):
        """Update floating animation"""
        self.t += dt
        dy = math.sin(self.t * 2.2) * (self.cell_size * 0.10)
        self.offset = (0, int(dy))

    def draw(self, surface, pos_px):
        """Draw banana with shadow"""
        # Draw shadow
        shadow = pygame.Surface((self.rect.w, self.rect.h // 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), shadow.get_rect())
        surface.blit(shadow, (pos_px[0], pos_px[1] + self.rect.h - 6))
        
        # Draw banana with floating offset
        surface.blit(self.base_image, (pos_px[0], pos_px[1] + self.offset[1]))


class MonkeyIdle(pygame.sprite.Sprite):
    """Animated monkey sprite with frame animation"""
    
    def __init__(self, frames, fallback, cell_size):
        super().__init__()
        self.frames = frames if frames else [fallback]
        self.cell_size = cell_size
        self.index = 0
        self.timer = 0.0
        self.fps = 6 if len(self.frames) > 1 else 0

    def update(self, dt):
        """Update animation frame"""
        if self.fps > 0 and len(self.frames) > 1:
            self.timer += dt
            if self.timer >= 1.0 / self.fps:
                self.timer = 0.0
                self.index = (self.index + 1) % len(self.frames)

    def current(self):
        """Get current animation frame"""
        return self.frames[self.index]


__all__ = ['FloatingBanana', 'MonkeyIdle']
