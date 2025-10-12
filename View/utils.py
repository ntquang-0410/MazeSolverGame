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


def load_monkey_path_images():
    """Load all monkey path images for use in floor tiles states 4 and 5"""
    monkey_path_dir = os.path.join(ASSETS, "monkey_path")
    monkey_path_images = {}

    # Define the mapping of image files to their keys
    image_files = {
        'bottom_to_top': 'bottom_to_top.png',
        'left_to_right': 'left_to_right.png',
        'right_to_left': 'right_to_left.png',
        'top_to_bottom': 'top_to_bottom.png',
        'cross_footprints': 'cross_footprints.png',
        'fork_footprints': 'folk_in_the_footprints.png',
        'turn_back': 'turn_back.png'
    }

    for key, filename in image_files.items():
        image_path = os.path.join(monkey_path_dir, filename)
        if os.path.exists(image_path):
            monkey_path_images[key] = load_image(image_path)
        else:
            # Create a placeholder if image doesn't exist
            placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
            placeholder.fill((100, 100, 200, 100))
            monkey_path_images[key] = placeholder

    return monkey_path_images


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


def determine_footprint_direction(solution_path, current_index, maze_cols, maze_rows):
    """
    Determine the appropriate footprint image based on path analysis
    Returns the key for the appropriate monkey path image
    """
    if not solution_path or current_index < 0 or current_index >= len(solution_path):
        return 'left_to_right'  # fallback

    current_pos = solution_path[current_index]
    prev_pos = solution_path[current_index - 1] if current_index > 0 else None
    next_pos = solution_path[current_index + 1] if current_index < len(solution_path) - 1 else None

    # Get surrounding path positions for intersection detection
    x, y = current_pos
    adjacent_path_count = 0
    directions = []

    # Check all 4 directions for path connections
    for dx, dy, direction in [(-1, 0, 'left'), (1, 0, 'right'), (0, -1, 'up'), (0, 1, 'down')]:
        adj_x, adj_y = x + dx, y + dy
        if (adj_x, adj_y) in solution_path:
            adjacent_path_count += 1
            directions.append(direction)

    # Intersection detection (cross or fork)
    if adjacent_path_count >= 3:
        if adjacent_path_count == 4:
            return 'cross_footprints'  # 4-way intersection
        else:
            return 'fork_footprints'    # 3-way fork

    # Determine movement direction for straight paths and turns
    if prev_pos and next_pos:
        # Calculate movement vectors
        prev_x, prev_y = prev_pos
        next_x, next_y = next_pos

        # Vector from previous to current
        dx1, dy1 = x - prev_x, y - prev_y
        # Vector from current to next
        dx2, dy2 = next_x - x, next_y - y

        # Check if it's a turn (direction change)
        if (dx1, dy1) != (dx2, dy2):
            # It's a turn - use turn_back for significant direction changes
            if (dx1 == -dx2 and dy1 == -dy2):  # Complete reversal
                return 'turn_back'
            # For other turns, use the outgoing direction
            if dx2 == 1:    # Moving right
                return 'left_to_right'
            elif dx2 == -1: # Moving left
                return 'right_to_left'
            elif dy2 == 1:  # Moving down
                return 'top_to_bottom'
            elif dy2 == -1: # Moving up
                return 'bottom_to_top'

        # Straight path - use the movement direction
        if dx2 == 1:    # Moving right
            return 'left_to_right'
        elif dx2 == -1: # Moving left
            return 'right_to_left'
        elif dy2 == 1:  # Moving down
            return 'top_to_bottom'
        elif dy2 == -1: # Moving up
            return 'bottom_to_top'

    # Handle start/end points
    if not prev_pos and next_pos:  # Start point
        next_x, next_y = next_pos
        dx, dy = next_x - x, next_y - y
        if dx == 1:    return 'left_to_right'
        elif dx == -1: return 'right_to_left'
        elif dy == 1:  return 'top_to_bottom'
        elif dy == -1: return 'bottom_to_top'

    if prev_pos and not next_pos:  # End point
        prev_x, prev_y = prev_pos
        dx, dy = x - prev_x, y - prev_y
        if dx == 1:    return 'left_to_right'
        elif dx == -1: return 'right_to_left'
        elif dy == 1:  return 'top_to_bottom'
        elif dy == -1: return 'bottom_to_top'

    # Default fallback
    return 'left_to_right'
