"""
Utility functions for View
Contains drawing helpers, image loading, and font management
"""
import os
import pygame


# Paths
ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def get_asset_path(name):
    """Get full path to an asset file"""
    return os.path.join(ASSETS, name)


def load_image(path, alpha=True):
    """Load an image with error handling"""
    try:
        img = pygame.image.load(path)
        return img.convert_alpha() if alpha else img.convert()
    except Exception as e:
        # Return placeholder surface if image fails to load
        surf = pygame.Surface((64, 64), pygame.SRCALPHA if alpha else 0)
        surf.fill((200, 50, 50, 160) if alpha else (200, 50, 50))
        return surf


def draw_shadow(surface, rect, radius=16, offset=(0, 6), alpha=110):
    """Draw a drop shadow"""
    s = pygame.Surface((rect.w + 20, rect.h + 20), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, alpha), pygame.Rect(10, 10, rect.w, rect.h), border_radius=radius)
    surface.blit(s, (rect.x - 10 + offset[0], rect.y - 10 + offset[1]))


def draw_glass_card(surface, rect, radius=18, bg=(16, 20, 16, 180), border=(90, 120, 90), border_alpha=60):
    """Draw a glassmorphism style card"""
    draw_shadow(surface, rect, radius, (0, 10), 120)
    card = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(card, bg, card.get_rect(), border_radius=radius)
    pygame.draw.rect(card, (*border, border_alpha), card.get_rect(), 2, border_radius=radius)
    surface.blit(card, rect.topleft)


def draw_smooth_rect(surface, rect, color, radius=16, border=0, border_color=(0, 0, 0)):
    """Draw a smooth rectangle with anti-aliasing"""
    # Supersampling for smooth edges
    scale = 2
    temp = pygame.Surface((rect.w * scale, rect.h * scale), pygame.SRCALPHA)
    pygame.draw.rect(temp, color, temp.get_rect(), border_radius=radius * scale)
    if border > 0:
        pygame.draw.rect(temp, border_color, temp.get_rect(), border * scale, border_radius=radius * scale)
    temp = pygame.transform.smoothscale(temp, rect.size)
    surface.blit(temp, rect.topleft)


def try_load_font(size):
    """Try to load custom font, fallback to system font"""
    prefer = os.path.join(ASSETS, "fonts", "PressStart2P.ttf")
    try:
        if os.path.exists(prefer):
            return pygame.font.Font(prefer, size)
    except:
        pass
    return pygame.font.SysFont(None, size)


def calculate_button_size(image, target_width=None, target_height=None):
    """Calculate button size while maintaining aspect ratio"""
    if image is None:
        return (100, 40)  # Default size

    orig_w, orig_h = image.get_size()
    aspect_ratio = orig_w / orig_h

    if target_width and not target_height:
        return (target_width, int(target_width / aspect_ratio))
    elif target_height and not target_width:
        return (int(target_height * aspect_ratio), target_height)
    elif target_width and target_height:
        w_from_width = target_width
        h_from_width = int(target_width / aspect_ratio)

        w_from_height = int(target_height * aspect_ratio)
        h_from_height = target_height

        if h_from_width <= target_height:
            return (w_from_width, h_from_width)
        else:
            return (w_from_height, h_from_height)
    else:
        return (orig_w, orig_h)
