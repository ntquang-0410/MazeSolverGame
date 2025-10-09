"""
Configuration file for Monkey's Treasure Game
Contains all constants and settings
"""
import os

# Game Settings
GAME_TITLE = "Monkey's Treasure"
FULLSCREEN = False
FPS = 60

# UI Layout
RIGHT_PANEL_W = 360
CELL_GAP = 0  # khít nhau

# Performance optimization settings
PERFORMANCE_MODE = False  # Automatically enabled when window is small
MIN_FPS_THRESHOLD = 30    # Switch to performance mode if FPS drops below this
PERFORMANCE_FPS = 30      # Reduced FPS in performance mode
MIN_CELL_SIZE_FOR_DETAILS = 12  # Don't draw detailed elements if cells are smaller

# Maze Settings
GENERATOR = "None"  # DFS, Kruskal, Binary Tree, Wilson, Recursive Division
MODE = None  # Easy, Medium, Hard
MAZE_COLS, MAZE_ROWS = 25, 19

# Cell Status Constants
CELL_STATUS = {
    'WALL': 0,
    'PATH': 1,
    'START': 2,
    'END': 3,
    'PATH_FOUND': 4,
    'MOVED_PATH': 5
}

# Color Palettes
PALETTES = {
    'neutral': ((20, 28, 20), (28, 36, 28), (60, 80, 60)),
    'green': ((32, 64, 44), (48, 104, 74), (84, 140, 110)),
    'yellow': ((88, 72, 24), (130, 110, 36), (170, 140, 50)),
    'orange': ((120, 64, 30), (170, 96, 48), (210, 130, 70)),
    'blue': ((34, 54, 86), (48, 86, 138), (72, 118, 170)),
    'purple': ((52, 34, 86), (88, 58, 140), (120, 90, 168)),
    'red': ((92, 38, 38), (138, 54, 54), (170, 84, 84)),
}

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "View", "assets")

def get_asset_path(name):
    """Get full path to an asset file"""
    return os.path.join(ASSETS_DIR, name)
