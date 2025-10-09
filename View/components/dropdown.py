"""
Dropdown Component
Dropdown menu for selecting options
"""
import time
import pygame
from View.utils import draw_shadow, draw_smooth_rect


class Dropdown:
    """Dropdown menu component for algorithm selection"""
    
    def __init__(self, rect, font, options, default_text="None", on_select=None):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.options = options[:]
        self.open = False
        self.selected = None
        self.default_text = default_text
        self.on_select = on_select
        
        # Click debounce for better responsiveness
        self.last_click_time = 0
        self.click_debounce = 0.05  # 50ms

    def draw(self, surface):
        """Draw dropdown on surface"""
        bg = (20, 28, 20)
        border = (36, 60, 36)

        # Performance mode check
        performance_mode = hasattr(surface, '_performance_mode') and getattr(surface, '_performance_mode', False)

        if performance_mode:
            # Simple drawing for performance
            pygame.draw.rect(surface, bg, self.rect, border_radius=8)
            pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)
        else:
            # Full quality drawing
            draw_shadow(surface, self.rect, radius=14, offset=(0, 6), alpha=100)
            draw_smooth_rect(surface, self.rect, bg, radius=14, border=2, border_color=border)

        # Display text
        text = self.selected if self.selected else self.default_text
        label = self.font.render(text, True, (240, 240, 240))
        surface.blit(label, (self.rect.x + 12, self.rect.y + (self.rect.h - label.get_height()) // 2))

        # Draw caret (down arrow)
        pygame.draw.polygon(surface, (200, 200, 200),
                          [(self.rect.right - 22, self.rect.y + self.rect.h // 2 - 4),
                           (self.rect.right - 12, self.rect.y + self.rect.h // 2 - 4),
                           (self.rect.right - 17, self.rect.y + self.rect.h // 2 + 4)])

        # Draw dropdown panel if open
        if self.open:
            opt_h = self.rect.h
            panel = pygame.Rect(self.rect.x, self.rect.bottom + 6, self.rect.w, opt_h * len(self.options))

            if performance_mode:
                pygame.draw.rect(surface, (240, 240, 240), panel, border_radius=8)
            else:
                draw_shadow(surface, panel, radius=12, offset=(0, 6), alpha=110)
                pygame.draw.rect(surface, (240, 240, 240), panel, border_radius=12)

            # Draw options
            for i, opt in enumerate(self.options):
                r = pygame.Rect(panel.x, panel.y + i * opt_h, panel.w, opt_h)
                pygame.draw.rect(surface, (255, 255, 255), r, border_radius=0)
                lab = self.font.render(opt, True, (40, 40, 40))
                surface.blit(lab, (r.x + 12, r.y + (r.h - lab.get_height()) // 2))
                pygame.draw.line(surface, (230, 230, 230), (r.x, r.bottom - 1), (r.right, r.bottom - 1))

    def handle_event(self, event):
        """Handle mouse events"""
        current_time = time.time()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check debounce
            if current_time - self.last_click_time < self.click_debounce:
                return

            if self.open:
                opt_h = self.rect.h
                panel = pygame.Rect(self.rect.x, self.rect.bottom + 6, self.rect.w, opt_h * len(self.options))

                if panel.collidepoint(event.pos):
                    # Option selected
                    index = (event.pos[1] - panel.y) // opt_h
                    if 0 <= index < len(self.options):
                        self.selected = self.options[index]
                        if self.on_select:
                            self.on_select(self.selected)
                    self.open = False
                    self.last_click_time = current_time
                else:
                    # Click outside - close
                    self.open = False
                    self.last_click_time = current_time
            else:
                # Open dropdown
                if self.rect.collidepoint(event.pos):
                    self.open = True
                    self.last_click_time = current_time
