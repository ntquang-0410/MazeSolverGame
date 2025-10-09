"""
Button Component
Customizable button with image background support and themes
"""
import pygame
from config import PALETTES
from View.utils import draw_shadow, draw_smooth_rect


class Button:
    """Interactive button component with hover effects"""
    
    def __init__(self, rect, text, font, on_click=None, tooltip=None, theme='neutral', bg_image=None, keep_aspect=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.tooltip = tooltip
        self.enabled = True
        self.hovered = False
        self.theme = theme
        self.bg_image = bg_image
        self.scaled_bg = None
        self.keep_aspect = keep_aspect

        # Scale background image if provided
        if self.bg_image:
            if keep_aspect:
                orig_w, orig_h = self.bg_image.get_size()
                aspect_ratio = orig_w / orig_h

                target_w = self.rect.width
                target_h = self.rect.height

                new_h = int(target_w / aspect_ratio)
                if new_h <= target_h:
                    self.rect.height = new_h
                else:
                    new_w = int(target_h * aspect_ratio)
                    self.rect.width = new_w

            self.scaled_bg = pygame.transform.smoothscale(self.bg_image, self.rect.size)

    def draw(self, surface):
        """Draw button on surface"""
        # Rescale background if size changed
        if self.bg_image and (not self.scaled_bg or self.scaled_bg.get_size() != self.rect.size):
            self.scaled_bg = pygame.transform.smoothscale(self.bg_image, self.rect.size)
        
        if self.bg_image and self.scaled_bg:
            # Draw image background
            if self.hovered and self.enabled:
                hover_surface = self.scaled_bg.copy()
                hover_overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                hover_overlay.fill((255, 255, 255, 30))
                hover_surface.blit(hover_overlay, (0, 0))
                surface.blit(hover_surface, self.rect.topleft)
            else:
                surface.blit(self.scaled_bg, self.rect.topleft)

            # Draw text with shadow
            color = (255, 255, 255) if self.enabled else (170, 170, 170)
            label = self.font.render(self.text, True, color)

            shadow = self.font.render(self.text, True, (0, 0, 0))
            shadow_pos = label.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
            text_pos = label.get_rect(center=self.rect.center)

            surface.blit(shadow, shadow_pos)
            surface.blit(label, text_pos)
        else:
            # Fallback to themed style
            color = (235, 235, 235) if self.enabled else (170, 170, 170)
            base, hover, border_col = PALETTES.get(self.theme, PALETTES['neutral'])
            bg = hover if self.hovered and self.enabled else base
            draw_shadow(surface, self.rect, radius=14, offset=(0, 6), alpha=100)
            draw_smooth_rect(surface, self.rect, bg, radius=14, border=2, border_color=border_col)
            label = self.font.render(self.text, True, color)
            surface.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()
