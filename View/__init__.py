import os, sys, math, random, pygame, time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model import GenerationModel, SolvingModel
from View.components import Button, Dropdown, ModalHistory, ModalVictory
from View.sprites import FloatingBanana, MonkeyIdle
from View.utils import load_image, draw_shadow, draw_glass_card, draw_smooth_rect, try_load_font, calculate_button_size
#from Controller import MazeController


GAME_TITLE = "Monkey's Treasure"
FULLSCREEN = False
RIGHT_PANEL_W = 420  # Tăng từ 360 lên 420 để có nhiều không gian hơn
FPS = 60
# Performance optimization settings
PERFORMANCE_MODE = False  # Automatically enabled when window is small
MIN_FPS_THRESHOLD = 30    # Switch to performance mode if FPS drops below this
PERFORMANCE_FPS = 30      # Reduced FPS in performance mode
MIN_CELL_SIZE_FOR_DETAILS = 12  # Don't draw detailed elements if cells are smaller
GENERATOR = "None" # DFS, Kruskal, Binary Tree, Wilson, Recursive Division
MODE = None  # Easy, Medium, Hard
MAZE_COLS, MAZE_ROWS = 25, 19
CELL_GAP = 0  # khít nhau

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
IMG = lambda name: os.path.join(ASSETS, name)

PALETTES = {
    'neutral': ((20,28,20), (28,36,28), (60,80,60)),
    'green'  : ((32,64,44), (48,104,74), (84,140,110)),
    'yellow' : ((88,72,24), (130,110,36), (170,140,50)),
    'orange' : ((120,64,30), (170,96,48), (210,130,70)),
    'blue'   : ((34,54,86),  (48,86,138), (72,118,170)),
    'purple' : ((52,34,86),  (88,58,140), (120,90,168)),
    'red'    : ((92,38,38),  (138,54,54), (170,84,84)),
}

# ---------- App ----------
class App:
    def __init__(self):
        self.cell_size = None
        self.maze_rect = None
        pygame.init()
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode((0, 0) if FULLSCREEN else (1024, 768), flags)
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.window_rect = self.screen.get_rect()
        self.running = True

        # Performance optimization - Cache system
        self._image_cache = {}
        self._surface_cache = {}
        self._last_cell_size = None
        self._bg_cache = {}

        # Performance monitoring and optimization
        self.fps_samples = []
        self.current_fps = FPS
        self.performance_mode = PERFORMANCE_MODE
        self.frame_skip_counter = 0
        self.dirty_regions = []
        self.last_draw_time = 0
        self.skip_expensive_effects = False

        # Precomputed maze surface for small sizes
        self._maze_surface = None
        self._maze_surface_dirty = True
        self._ui_surface = None
        self._ui_surface_dirty = True

        # assets
        self.bg_jungle = load_image(IMG("bg_jungle.png"))
        self.bg_start = load_image(IMG("bg_start.png"))
        self.tile_wall = load_image(IMG("tile_wall.png"))
        self.monkey_img = load_image(IMG("monkey.png"))
        self.banana_img = load_image(IMG("banana_rainbow.png"))

        # button assets
        self.btn_assets = {
            'start': load_image(IMG("button/start_btn.png")),
            'restart': load_image(IMG("button/restart_btn.png")),
            'close': load_image(IMG("button/close_btn.png")),
            'exit': load_image(IMG("button/exit_btn.png")),
            'minimize': load_image(IMG("button/minimize_btn.png")),
            'back': load_image(IMG("button/back_btn.png")),
            'history': load_image(IMG("button/history_btn.png")),
            'auto': load_image(IMG("button/auto_btn.png")),
            'small': load_image(IMG("button/small_btn.png")),
            'win_restart': load_image(IMG("button/win_restart_btn.png"))
        }

        # floor tiles
        self.floor_tiles = []
        tiles_dir = os.path.join(ASSETS, "tiles")
        for name in sorted(os.listdir(tiles_dir)):
            if name.lower().endswith(".png"):
                self.floor_tiles.append(load_image(os.path.join(tiles_dir, name)))

        # fonts
        self.font_title = try_load_font(64)
        self.font_ui = try_load_font(26)
        self.font_small = try_load_font(20)

        # state
        self.state = "start"
        self.paused = False
        self.auto_on = False
        self.selected_algo = None
        self.steps = 0
        self.timer = 0.0
        self.start_time = None
        self.history = []
        self.game_won = False
        self.modal_history = ModalHistory(lambda: self.history)
        self.modal_victory = ModalVictory(self.restart_level)
        self.modal_victory.win_restart_img = self.btn_assets['win_restart']

        # Lưu kích thước windowed và trạng thái fullscreen
        self.windowed_size = (1024, 768)  # Kích thước khi không full màn hình
        self.is_fullscreen = FULLSCREEN  # Ban đầu là full màn hình
        self.is_minimized = False  # Trạng thái thu nhỏ

        # Window dragging state
        self.dragging = False
        self.drag_offset = (0, 0)

        # Window controls - 3 nút ở góc trên phải
        btn_size = 48  # Kích thước nút - tăng lên
        btn_y = 10     # Vị trí Y - dời lên cao hơn
        btn_gap = 8    # Khoảng cách giữa các nút

        # Tính vị trí từ phải sang trái (Exit -> Maximize -> Minimize)
        x_exit = self.window_rect.w - 10 - btn_size
        x_maximize = x_exit - btn_gap - btn_size
        x_minimize = x_maximize - btn_gap - btn_size

        # Tạo 3 nút mới với assets đúng
        # Nút trái: Hide (ẩn cửa sổ)
        self.btn_min = Button(
            (x_minimize, btn_y, btn_size, btn_size),
            "", self.font_small, self.hide_window,
            theme='yellow',
            bg_image=self.btn_assets['minimize'],
            keep_aspect=False
        )

        # Nút giữa: Minimize (thu nhỏ cửa sổ)
        self.btn_max = Button(
            (x_maximize, btn_y, btn_size, btn_size),
            "", self.font_small, self.shrink_window,
            theme='blue',
            bg_image=self.btn_assets['small'],
            keep_aspect=False
        )

        self.btn_close = Button(
            (x_exit, btn_y, btn_size, btn_size),
            "", self.font_small, self.quit,
            theme='red',
            bg_image=self.btn_assets['close'],  # Dùng close_btn thay vì exit_btn
            keep_aspect=False
        )

        # start screen - tăng kích thước nút start
        start_size = calculate_button_size(self.btn_assets['start'], target_width=240)  # Tăng từ 180 lên 240
        self.btn_start = Button((0, 0, start_size[0], start_size[1]), "", self.font_ui, self.goto_game, theme='green', bg_image=self.btn_assets['start'], keep_aspect=False)

        # game UI
        self.compute_layout()

        # Tính toán vị trí sidebar và margin
        sidebar_left = self.window_rect.w - RIGHT_PANEL_W
        margin = 25  # Margin từ mép sidebar
        cur_y = 120  # Vị trí Y bắt đầu (tránh window controls)

        # Chiều rộng các nút
        target_btn_w = RIGHT_PANEL_W - (margin * 2)  # Chiều rộng toàn bộ
        btn_h = 45  # Chiều cao cố định cho tất cả các nút
        row_spacing = 10  # Khoảng cách giữa các dòng

        # Vị trí X bắt đầu (căn giữa trong sidebar)
        spx = sidebar_left + margin

        # Dòng 1: Restart button (toàn bộ chiều rộng)
        self.btn_restart = Button((spx, cur_y, target_btn_w, btn_h), "", self.font_ui, 
                                  self.restart_level, theme='orange', 
                                  bg_image=self.btn_assets['restart'], keep_aspect=False)
        cur_y += btn_h + row_spacing

        # Dòng 2: Auto button (toàn bộ chiều rộng)
        self.btn_auto = Button((spx, cur_y, target_btn_w, btn_h), "", self.font_ui, 
                              self.toggle_auto, theme='blue', 
                              bg_image=self.btn_assets['auto'], keep_aspect=False)
        cur_y += btn_h + row_spacing

        # Dòng 3: Play và Pause (2 nút cạnh nhau)
        half_btn_w = (target_btn_w - 8) // 2  # Chiều rộng mỗi nút (2 nút/dòng)
        self.btn_play = Button((spx, cur_y, half_btn_w, btn_h), "", self.font_ui, 
                              self.toggle_play, theme='green', 
                              bg_image=self.btn_assets['small'], keep_aspect=False)
        self.btn_pause = Button((spx + half_btn_w + 8, cur_y, half_btn_w, btn_h), "", 
                               self.font_ui, self.toggle_play, theme='yellow', 
                               bg_image=self.btn_assets['small'], keep_aspect=False)
        cur_y += btn_h + row_spacing + 5  # Thêm khoảng cách trước dropdown

        # Dòng 4: Dropdown solving algorithm (chiều rộng đầy đủ)
        self.dropdown = Dropdown((spx, cur_y, target_btn_w, 42), self.font_small, 
                                ["BFS","DFS","UCS","A*","Bidirectional"], 
                                default_text="Solving Algorithm", 
                                on_select=self.set_algo)
        cur_y += 42 + row_spacing

        # Dòng 5: Dropdown generation algorithm (chiều rộng đầy đủ)
        self.maze_gen_dropdown = Dropdown((spx, cur_y, target_btn_w, 42), self.font_small, 
                                         ["DFS", "Kruskal", "Binary Tree", "Wilson", "Recursive Div."], 
                                         default_text="Generation Algorithm", 
                                         on_select=self.set_generation_algo)
        cur_y += 42 + row_spacing

        # Dòng 6: Generate button (toàn bộ chiều rộng)
        self.btn_generate = Button((spx, cur_y, target_btn_w, btn_h), "Generate Maze", 
                                  self.font_ui, self.generate_maze, theme='green', 
                                  keep_aspect=False)
        cur_y += btn_h + row_spacing + 5  # Thêm khoảng cách trước history/back

        # Dòng 7: History button (toàn bộ chiều rộng)
        self.btn_history = Button((spx, cur_y, target_btn_w, btn_h), "", self.font_ui, 
                                 self.open_history, theme='purple', 
                                 bg_image=self.btn_assets['history'], keep_aspect=False)
        cur_y += btn_h + row_spacing

        # Dòng 8: Back button (toàn bộ chiều rộng)
        self.btn_back = Button((spx, cur_y, target_btn_w, btn_h), "", self.font_ui, 
                              self.goto_start, theme='red', 
                              bg_image=self.btn_assets['back'], keep_aspect=False)

        # maze
        self.MazeGenerated = GenerationModel(MAZE_COLS, MAZE_ROWS, GENERATOR).generate_maze()
        self.maze = self.MazeGenerated
        self.player = [1,1]  # Khởi tạo từ (1,1) thay vì (0,0)
        self.prepare_sprites()

        # prebuild random floor map for repeatability
        random.seed(42)
        self.floor_map = [[random.randrange(len(self.floor_tiles)) for _ in range(MAZE_COLS)] for _ in range(MAZE_ROWS)]

        # Cập nhật scale các nút game ngay sau khi khởi tạo
        self.update_game_buttons()

    def prepare_sprites(self):
        cell = self.cell_size
        # Clear cache if cell size changed
        if self._last_cell_size != cell:
            self.clear_size_dependent_cache()
            self._last_cell_size = cell

        def scale_to_cell(img, ratio=0.9):
            w = h = int(cell*ratio)
            return self.get_scaled_image(img, (w,h))

        # Pre-scale and cache all floor tiles for current cell size
        self.scaled_floor_tiles = []
        for tile in self.floor_tiles:
            self.scaled_floor_tiles.append(self.get_scaled_image(tile, (cell, cell)))

        # Pre-scale wall tile
        self.scaled_wall_tile = self.get_scaled_image(self.tile_wall, (cell, cell))

        # idle frames
        stand_dir = os.path.join(ASSETS, "monkey_stand")
        frames = []
        if os.path.exists(stand_dir):
            for name in sorted(os.listdir(stand_dir)):
                if name.lower().endswith((".png",".jpg",".jpeg")):
                    frames.append(scale_to_cell(load_image(os.path.join(stand_dir, name))))
        self.monkey_idle = MonkeyIdle(frames, scale_to_cell(self.monkey_img), self.cell_size)
        self.banana = FloatingBanana(scale_to_cell(self.banana_img, 0.85), self.cell_size)

    # ---- Window controls
    def update_window_controls(self):
        """Cập nhật vị trí window controls khi cửa sổ thay đổi kích thước"""
        btn_size = 48  # Tăng kích thước nút
        btn_y = 10  # Vị trí Y - cao hơn
        btn_gap = 8

        x_exit = self.window_rect.w - 10 - btn_size
        x_maximize = x_exit - btn_gap - btn_size
        x_minimize = x_maximize - btn_gap - btn_size

        self.btn_min.rect = pygame.Rect(x_minimize, btn_y, btn_size, btn_size)
        self.btn_max.rect = pygame.Rect(x_maximize, btn_y, btn_size, btn_size)
        self.btn_close.rect = pygame.Rect(x_exit, btn_y, btn_size, btn_size)

        # Re-scale background images
        if self.btn_min.bg_image:
            self.btn_min.scaled_bg = pygame.transform.smoothscale(self.btn_min.bg_image, (btn_size, btn_size))
        if self.btn_max.bg_image:
            self.btn_max.scaled_bg = pygame.transform.smoothscale(self.btn_max.bg_image, (btn_size, btn_size))
        if self.btn_close.bg_image:
            self.btn_close.scaled_bg = pygame.transform.smoothscale(self.btn_close.bg_image, (btn_size, btn_size))

    def update_game_buttons(self):
        """Cập nhật kích thước và vị trí các nút game khi cửa sổ thay đổi"""
        # Scale sidebar width theo tỷ lệ cửa sổ
        scale_factor = min(self.window_rect.w / 1920, self.window_rect.h / 1080)
        scale_factor = max(0.5, min(1.0, scale_factor))

        scaled_panel_w = int(RIGHT_PANEL_W * scale_factor)
        scaled_panel_w = max(240, scaled_panel_w)  # Tăng tối thiểu lên 240px

        # Tính toán vị trí sidebar và margin
        sidebar_left = self.window_rect.w - scaled_panel_w
        margin = int(25 * scale_factor)
        margin = max(15, margin)  # Margin tối thiểu
        cur_y = 120

        # Chiều rộng các nút
        target_btn_w = scaled_panel_w - (margin * 2)
        btn_h = int(45 * scale_factor)  # Chiều cao nút scale theo cửa sổ
        btn_h = max(35, btn_h)  # Chiều cao tối thiểu
        row_spacing = max(8, int(10 * scale_factor))

        # Vị trí X bắt đầu
        spx = sidebar_left + margin

        # Dòng 1: Restart button (toàn bộ chiều rộng)
        self.btn_restart.rect = pygame.Rect(spx, cur_y, target_btn_w, btn_h)
        if self.btn_restart.bg_image:
            self.btn_restart.scaled_bg = pygame.transform.smoothscale(
                self.btn_restart.bg_image, (target_btn_w, btn_h))
        cur_y += btn_h + row_spacing

        # Dòng 2: Auto button (toàn bộ chiều rộng)
        self.btn_auto.rect = pygame.Rect(spx, cur_y, target_btn_w, btn_h)
        if self.btn_auto.bg_image:
            self.btn_auto.scaled_bg = pygame.transform.smoothscale(
                self.btn_auto.bg_image, (target_btn_w, btn_h))
        cur_y += btn_h + row_spacing

        # Dòng 3: Play và Pause (2 nút cạnh nhau)
        half_btn_w = (target_btn_w - 8) // 2
        self.btn_play.rect = pygame.Rect(spx, cur_y, half_btn_w, btn_h)
        if self.btn_play.bg_image:
            self.btn_play.scaled_bg = pygame.transform.smoothscale(
                self.btn_play.bg_image, (half_btn_w, btn_h))
        self.btn_pause.rect = pygame.Rect(spx + half_btn_w + 8, cur_y, half_btn_w, btn_h)
        if self.btn_pause.bg_image:
            self.btn_pause.scaled_bg = pygame.transform.smoothscale(
                self.btn_pause.bg_image, (half_btn_w, btn_h))
        cur_y += btn_h + row_spacing + 5

        # Dòng 4: Dropdown solving algorithm
        dropdown_h = int(42 * scale_factor)
        dropdown_h = max(35, dropdown_h)
        self.dropdown.rect = pygame.Rect(spx, cur_y, target_btn_w, dropdown_h)
        cur_y += dropdown_h + row_spacing

        # Dòng 5: Dropdown generation algorithm
        self.maze_gen_dropdown.rect = pygame.Rect(spx, cur_y, target_btn_w, dropdown_h)
        cur_y += dropdown_h + row_spacing

        # Dòng 6: Generate button (toàn bộ chiều rộng)
        self.btn_generate.rect = pygame.Rect(spx, cur_y, target_btn_w, btn_h)
        cur_y += btn_h + row_spacing + 5

        # Dòng 7: History button (toàn bộ chiều rộng)
        self.btn_history.rect = pygame.Rect(spx, cur_y, target_btn_w, btn_h)
        if self.btn_history.bg_image:
            self.btn_history.scaled_bg = pygame.transform.smoothscale(
                self.btn_history.bg_image, (target_btn_w, btn_h))
        cur_y += btn_h + row_spacing

        # Dòng 8: Back button (toàn bộ chiều rộng)
        self.btn_back.rect = pygame.Rect(spx, cur_y, target_btn_w, btn_h)
        if self.btn_back.bg_image:
            self.btn_back.scaled_bg = pygame.transform.smoothscale(
                self.btn_back.bg_image, (target_btn_w, btn_h))

    def hide_window(self):
        """Ẩn cửa sổ xuống taskbar (iconify)"""
        try:
            pygame.display.iconify()
        except:
            pass

    def shrink_window(self):
        """Thu nhỏ cửa sổ về 70% màn hình (giữ tỷ lệ) hoặc phóng to lại fullscreen"""
        global FULLSCREEN

        if self.is_minimized:
            # Đang ở trạng thái thu nhỏ -> phóng to về fullscreen
            FULLSCREEN = True
            self.is_fullscreen = True
            self.is_minimized = False
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Đang fullscreen -> thu nhỏ về 70% màn hình (giữ tỷ lệ)
            FULLSCREEN = False
            self.is_fullscreen = False
            self.is_minimized = True

            # Lấy kích thước màn hình sử dụng pygame (cross-platform)
            display_info = pygame.display.Info()
            screen_width = display_info.current_w
            screen_height = display_info.current_h

            # Tính 70% kích thước màn hình nhưng giữ tỷ lệ khung hình
            target_width = int(screen_width * 0.7)
            target_height = int(screen_height * 0.7)

            # Giữ tỷ lệ khung hình của màn hình gốc
            screen_ratio = screen_width / screen_height

            # Tính kích thước cửa sổ giữ nguyên tỷ lệ
            if target_width / target_height > screen_ratio:
                # Giới hạn bởi chiều cao
                window_height = target_height
                window_width = int(window_height * screen_ratio)
            else:
                # Giới hạn bởi chiều rộng
                window_width = target_width
                window_height = int(window_width / screen_ratio)

            # Đảm bảo kích thước tối thiểu
            window_width = max(640, window_width)
            window_height = max(480, window_height)

            # Căn giữa cửa sổ trước khi tạo
            self.center_window(window_width, window_height)

            # Tạo cửa sổ mới với kích thước đã tính
            pygame.display.set_mode((window_width, window_height))

        # Cập nhật sau khi thay đổi kích thước
        self.screen = pygame.display.get_surface()
        self.window_rect = self.screen.get_rect()
        self.compute_layout()
        self.update_window_controls()
        self.prepare_sprites()

    def center_window(self, width, height):
        """Đặt cửa sổ ở giữa màn hình - cross-platform version"""
        try:
            # Lấy kích thước màn hình sử dụng pygame
            display_info = pygame.display.Info()
            screen_width = display_info.current_w
            screen_height = display_info.current_h

            # Tính vị trí căn giữa
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2

            # Đặt vị trí cửa sổ sử dụng environment variable (cross-platform)
            import os
            os.environ['SDL_WINDOW_POS'] = f'{x},{y}'

        except Exception as e:
            # Nếu không thể căn giữa, để pygame tự xử lý
            pass

    def toggle_fullscreen(self):
        global FULLSCREEN
        FULLSCREEN = not FULLSCREEN
        if FULLSCREEN:
            pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((1024,768))
        self.screen = pygame.display.get_surface()
        self.window_rect = self.screen.get_rect()
        self.compute_layout()
        self.update_window_controls()  # Cập nhật vị trí window controls
        self.prepare_sprites()  # Cập nhật sprites với cell size mới

    def quit(self):
        self.running = False

    # ---- Layout
    def compute_layout(self):
        screen = self.window_rect

        # Scale sidebar width theo tỷ lệ cửa sổ
        scale_factor = min(screen.w / 1920, screen.h / 1080)
        scale_factor = max(0.5, min(1.0, scale_factor))
        scaled_panel_w = int(RIGHT_PANEL_W * scale_factor)
        scaled_panel_w = max(200, scaled_panel_w)

        left_space = screen.w - scaled_panel_w
        margin = max(12, int(24 * scale_factor))
        avail_w = left_space - margin*2
        avail_h = screen.h - margin*2
        cell_w = avail_w // MAZE_COLS
        cell_h = avail_h // MAZE_ROWS
        self.cell_size = min(cell_w, cell_h)
        maze_w = self.cell_size * MAZE_COLS
        maze_h = self.cell_size * MAZE_ROWS
        self.maze_rect = pygame.Rect((left_space - maze_w)//2 + margin, (screen.h-maze_h)//2, maze_w, maze_h)

        # Cập nhật lại kích thước và vị trí các nút game (chỉ khi đã khởi tạo)
        if hasattr(self, 'btn_restart'):
            self.update_game_buttons()

    # ---- State transitions
    def goto_start(self):
        self.save_run(label="Manual" if not self.auto_on else f"Auto ({self.selected_algo or 'None'})")
        self.state = "start"; self.modal_history.visible=False

    def goto_game(self):
        self.state = "game"; self.reset_run()

    def reset_run(self):
        self.steps = 0; self.timer = 0.0; self.start_time = time.time()
        self.paused = False; self.auto_on=False
        self.player= [1,1]  # Bắt đầu từ (1,1) thay vì (0,0) vì viền ngoài là tường
        self.maze = self.MazeGenerated
        self.prepare_sprites()
        self.modal_victory.hide()

    def restart_level(self): self.reset_run()
    def toggle_play(self): self.paused = not self.paused
    def toggle_auto(self): self.auto_on = not self.auto_on
    def set_algo(self, name): self.selected_algo = name
    def set_generation_algo(self, name):
        """Thiết lập thuật toán sinh mê cung được chọn"""
        self.selected_generation_algo = name

    def generate_maze(self):
        """Sinh mê cung mới dựa trên thuật toán được chọn"""
        if not hasattr(self, 'selected_generation_algo') or self.selected_generation_algo is None:
            return

        # Tạo model mới và set thuật toán
        generation_model = GenerationModel(MAZE_COLS, MAZE_ROWS, self.selected_generation_algo)

        # Sinh mê cung
        self.MazeGenerated = generation_model.generate_maze()
        self.maze = self.MazeGenerated

        # Reset lại vị trí người chơi về start position
        self.player = [1, 1]

        # Reset game state nhưng không gọi reset_run() để tránh lặp
        self.steps = 0
        self.timer = 0.0
        self.start_time = time.time()
        self.paused = False
        self.game_won = False

        # Cập nhật sprites và invalidate cache
        self.prepare_sprites()
        self.invalidate_maze_surface()  # Important for performance optimization
        self.modal_victory.hide()

    def open_history(self): self.modal_history.visible = True

    def save_run(self, label="Manual"):
        if self.start_time is None: return
        duration = self.timer; steps=self.steps
        if duration<=0 and steps<=0: return
        rank = "S" if duration<30 and steps<50 else ("A" if duration<60 else ("B" if duration<120 else "C"))
        mode = label if "Auto" in label else ("Manual" if not self.auto_on else f"Auto ({self.selected_algo or 'None'})")
        self.history.append({"time_str": f"{int(duration//60):02d}:{int(duration%60):02d}", "steps": steps, "rank": rank, "mode": mode})

    # ---- Input
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.quit()

            # Window dragging - chỉ hoạt động khi không fullscreen
            if not self.is_fullscreen:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Kiểm tra xem có click vào vùng title bar không (vùng trên cùng, tránh các nút)
                    if event.pos[1] < 60:  # Vùng title bar
                        # Kiểm tra xem có click vào các nút window control không
                        clicked_button = False
                        for btn in (self.btn_close, self.btn_max, self.btn_min):
                            if btn.rect.collidepoint(event.pos):
                                clicked_button = True
                                break

                        if not clicked_button:
                            self.dragging = True
                            self.drag_offset = event.pos

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        # Di chuyển cửa sổ - simplified cross-platform version
                        try:
                            # Lấy vị trí chuột hiện tại
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            # Tính toán vị trí mới
                            new_x = mouse_x - self.drag_offset[0]
                            new_y = mouse_y - self.drag_offset[1]
                            # Đặt lại vị trí cửa sổ cho lần tạo tiếp theo
                            os.environ['SDL_WINDOW_POS'] = f'{new_x},{new_y}'
                        except:
                            pass

            if self.state == "start": self.btn_start.handle_event(event)
            for b in (self.btn_close, self.btn_max, self.btn_min): b.handle_event(event)
            if self.state == "game":
                # Xử lý modal victory trước
                if self.modal_victory.visible:
                    self.modal_victory.handle_event(event)
                else:
                    for b in (self.btn_restart, self.btn_play, self.btn_pause, self.btn_auto, self.btn_history, self.btn_back, self.btn_generate): b.handle_event(event)
                    self.dropdown.handle_event(event)
                    self.maze_gen_dropdown.handle_event(event)
                    if event.type == pygame.KEYDOWN and not self.paused:
                        if event.key in (pygame.K_LEFT, pygame.K_a): self.move(-1,0)
                        if event.key in (pygame.K_RIGHT, pygame.K_d): self.move(1,0)
                        if event.key in (pygame.K_UP, pygame.K_w): self.move(0,-1)
                        if event.key in (pygame.K_DOWN, pygame.K_s): self.move(0,1)
            if self.modal_history.visible and (event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN)):
                self.modal_history.visible=False

    def move(self, dx, dy):
        if self.game_won: return  # Không cho di chuyển khi đã thắng

        c, r = self.player; nc, nr = c+dx, r+dy
        if 0 <= nc < MAZE_COLS and 0 <= nr < MAZE_ROWS:
            # Cho phép di chuyển trên Path (1), Start (2), và End (3)
            if self.maze[nr][nc].status in [1, 2, 3]:
                self.player=[nc,nr]; self.steps += 1

                # Kiểm tra chiến thắng (chạm chuối ở vị trí thực tế)
                if nc == MAZE_COLS-2 and nr == MAZE_ROWS-2:
                    self.game_won = True
                    self.paused = True
                    time_str = f"{int(self.timer//60):02d}:{int(self.timer%60):02d}"
                    self.modal_victory.show(time_str, self.steps)

    # ---- Update / Draw
    def update(self, dt):
        if self.state=="game" and not self.paused:
            self.timer += dt; self.monkey_idle.update(dt); self.banana.update(dt)

    def draw_start(self):
        # background full, no blur
        bg = pygame.transform.smoothscale(self.bg_start, (self.window_rect.w, self.window_rect.h))
        self.screen.blit(bg, (0, 0))

        # Cập nhật kích thước nút START theo tỷ lệ cửa sổ
        base_width = 240  # Kích thước cơ bản
        scale_factor = min(self.window_rect.w / 1920, self.window_rect.h / 1080)  # Tỷ lệ so với fullscreen chuẩn
        scale_factor = max(0.5, min(1.0, scale_factor))  # Giới hạn từ 50% đến 100%

        new_width = int(base_width * scale_factor)
        start_size = calculate_button_size(self.btn_assets['start'], target_width=new_width)

        self.btn_start.rect = pygame.Rect(0, 0, start_size[0], start_size[1])
        self.btn_start.scaled_bg = pygame.transform.smoothscale(self.btn_start.bg_image, start_size)

        # place START slightly left and lower (~82% h)
        self.btn_start.rect.center = (int(self.window_rect.centerx * 0.85), int(self.window_rect.h * 0.82))
        self.btn_start.draw(self.screen)

        # Window controls - vẽ cuối cùng để đảm bảo không bị đè
        for b in (self.btn_min, self.btn_max, self.btn_close):
            b.draw(self.screen)

    def draw_game(self):
        # Update performance monitoring
        self.update_performance_mode()

        # Skip frame if in performance mode
        if self.should_skip_frame():
            return

        # jungle background full - use cached version
        bg_scaled = self.get_scaled_background(self.bg_jungle, (self.window_rect.w, self.window_rect.h))
        self.screen.blit(bg_scaled, (0,0))

        # Scale sidebar width theo tỷ lệ cửa sổ
        scale_factor = min(self.window_rect.w / 1920, self.window_rect.h / 1080)
        scale_factor = max(0.5, min(1.0, scale_factor))
        scaled_panel_w = int(RIGHT_PANEL_W * scale_factor)
        scaled_panel_w = max(200, scaled_panel_w)

        # sidebar card - use optimized drawing for small windows
        sidebar = pygame.Rect(self.window_rect.w-scaled_panel_w+int(10*scale_factor), 60, scaled_panel_w-int(20*scale_factor), self.window_rect.h-70)

        if self.skip_expensive_effects:
            # Simple sidebar background for performance
            pygame.draw.rect(self.screen, (18,24,18), sidebar, border_radius=12)
        else:
            # Full quality sidebar
            draw_glass_card(self.screen, sidebar, radius=22, bg=(18,24,18,190), border=(110,150,110), border_alpha=70)

        # chips - căn giữa text
        t = f"{int(self.timer//60):02d}:{int(self.timer%60):02d}"
        chip_h = max(28, int(36 * scale_factor)); x0 = sidebar.x+int(18*scale_factor); y0 = sidebar.y+int(50*scale_factor)
        chip1 = pygame.Rect(x0, y0, int(140*scale_factor), chip_h)

        if self.skip_expensive_effects:
            # Simple chip backgrounds
            pygame.draw.rect(self.screen, (26,34,26), chip1, border_radius=8)
        else:
            draw_smooth_rect(self.screen, chip1, (26,34,26,220), radius=18, border=2, border_color=(86,116,86))

        time_label = self.font_small.render("⏱  "+t, True, (235,235,235))
        time_x = chip1.x + (chip1.width - time_label.get_width()) // 2  # Căn giữa
        time_y = chip1.y + (chip1.height - time_label.get_height()) // 2  # Căn giữa
        self.screen.blit(time_label, (time_x, time_y))

        chip2 = pygame.Rect(chip1.right+int(10*scale_factor), y0, int(120*scale_factor), chip_h)

        if self.skip_expensive_effects:
            pygame.draw.rect(self.screen, (26,34,26), chip2, border_radius=8)
        else:
            draw_smooth_rect(self.screen, chip2, (26,34,26,220), radius=18, border=2, border_color=(86,116,86))

        steps_label = self.font_small.render("🚶  "+str(self.steps), True, (235,235,235))
        steps_x = chip2.x + (chip2.width - steps_label.get_width()) // 2  # Căn giữa
        steps_y = chip2.y + (chip2.height - steps_label.get_height()) // 2  # Căn giữa
        self.screen.blit(steps_label, (steps_x, steps_y))

        # buttons - layout mới: mỗi nút chính một hàng riêng
        spx = sidebar.x+int(20*scale_factor); cur_y = y0 + chip_h + int(24*scale_factor)
        full_btn_w = scaled_panel_w - int(40*scale_factor)  # Chiều rộng đầy đủ cho nút
        half_btn_w = (full_btn_w - int(8*scale_factor)) // 2  # Chiều rộng cho 2 nút (Play/Pause)
        spacing = max(8, int(10*scale_factor))

        # Dòng 1: Restart button (full width)
        self.btn_restart.rect.topleft = (spx, cur_y)
        self.btn_restart.rect.width = full_btn_w
        self.btn_restart.draw(self.screen)
        cur_y += self.btn_restart.rect.height + spacing

        # Dòng 2: Auto button (full width)
        self.btn_auto.rect.topleft = (spx, cur_y)
        self.btn_auto.rect.width = full_btn_w
        self.btn_auto.draw(self.screen)
        cur_y += self.btn_auto.rect.height + spacing

        # Dòng 3: Play và Pause (2 nút cạnh nhau)
        self.btn_play.rect.topleft = (spx, cur_y)
        self.btn_play.rect.width = half_btn_w
        self.btn_play.draw(self.screen)
        
        self.btn_pause.rect.topleft = (spx + half_btn_w + 8, cur_y)
        self.btn_pause.rect.width = half_btn_w
        self.btn_pause.draw(self.screen)
        cur_y += max(self.btn_play.rect.height, self.btn_pause.rect.height) + spacing + 5

        # Dòng 4: Dropdown solving algorithm (full width)
        self.dropdown.rect.topleft = (spx, cur_y)
        self.dropdown.rect.width = full_btn_w
        cur_y += self.dropdown.rect.height + spacing

        # Dòng 5: Dropdown generation algorithm (full width)
        self.maze_gen_dropdown.rect.topleft = (spx, cur_y)
        self.maze_gen_dropdown.rect.width = full_btn_w
        cur_y += self.maze_gen_dropdown.rect.height + spacing

        # Dòng 6: Generate button (full width)
        self.btn_generate.rect.topleft = (spx, cur_y)
        self.btn_generate.rect.width = full_btn_w
        self.btn_generate.draw(self.screen)
        cur_y += self.btn_generate.rect.height + spacing + 5

        # Dòng 7: History button (full width)
        self.btn_history.rect.topleft = (spx, cur_y)
        self.btn_history.rect.width = full_btn_w
        self.btn_history.draw(self.screen)
        cur_y += self.btn_history.rect.height + spacing

        # Dòng 8: Back button (full width)
        self.btn_back.rect.topleft = (spx, cur_y)
        self.btn_back.rect.width = full_btn_w
        self.btn_back.draw(self.screen)

        # Vẽ dropdown cuối cùng để chúng hiển thị trên các element khác
        self.dropdown.draw(self.screen)
        self.maze_gen_dropdown.draw(self.screen)

        # maze frame card - simplified for performance mode
        if self.skip_expensive_effects:
            pygame.draw.rect(self.screen, (12,22,12), self.maze_rect, border_radius=8)
        else:
            draw_glass_card(self.screen, self.maze_rect, radius=16, bg=(12,22,12,140), border=(90,120,90), border_alpha=55)

        # Use optimized maze rendering for small cells
        if self.cell_size < MIN_CELL_SIZE_FOR_DETAILS:
            # Use pre-rendered maze surface for better performance
            maze_surface = self.get_optimized_maze_surface()
            self.screen.blit(maze_surface, self.maze_rect.topleft)
        else:
            # Standard maze rendering for larger cells
            cell = self.cell_size
            for r in range(MAZE_ROWS):
                for c in range(MAZE_COLS):
                    x = self.maze_rect.x + c * cell
                    y = self.maze_rect.y + r * cell
                    idx = self.floor_map[r][c]
                    # Use pre-scaled cached tiles instead of scaling every frame
                    self.screen.blit(self.scaled_floor_tiles[idx], (x,y))

            # draw walls using cached scaled tile
            for r in range(MAZE_ROWS):
                for c in range(MAZE_COLS):
                    if self.maze[r][c].status == 0:
                        x = self.maze_rect.x + c*cell; y = self.maze_rect.y + r*cell
                        # Use pre-scaled cached wall tile
                        self.screen.blit(self.scaled_wall_tile, (x, y))

        # draw player
        px = self.maze_rect.x + self.player[0] * cell + (cell - self.monkey_idle.current().get_width())//2
        py = self.maze_rect.y + self.player[1] * cell + (cell - self.monkey_idle.current().get_height())//2
        self.screen.blit(self.monkey_idle.current(), (px, py))

        # draw banana goal - skip floating animation in performance mode
        gx = self.maze_rect.x + (MAZE_COLS - 2)*cell + (cell - self.banana.base_image.get_width())//2
        gy = self.maze_rect.y + (MAZE_ROWS - 2)*cell + (cell - self.banana.base_image.get_height())//2

        if self.skip_expensive_effects:
            # Static banana without animation
            self.screen.blit(self.banana.base_image, (gx, gy))
        else:
            # Animated floating banana
            self.banana.draw(self.screen, (gx, gy))

        # window buttons - vẽ cuối cùng để đảm bảo không bị đè
        for b in (self.btn_min, self.btn_max, self.btn_close):
            b.draw(self.screen)

        # history modal
        self.modal_history.draw(self.screen, self.window_rect, self.font_ui, self.font_small)

        # victory modal
        self.modal_victory.draw(self.screen, self.window_rect, self.font_title, self.font_ui)

    def get_cached_surface(self, key, creator_func):
        """Cache system for expensive surface operations"""
        if key not in self._surface_cache:
            self._surface_cache[key] = creator_func()
        return self._surface_cache[key]

    def clear_size_dependent_cache(self):
        """Clear cache when window size changes"""
        self._image_cache.clear()
        self._surface_cache.clear()
        self._bg_cache.clear()

    def get_scaled_image(self, image, size):
        """Cache scaled images to avoid repeated scaling"""
        cache_key = (id(image), size)
        if cache_key not in self._image_cache:
            self._image_cache[cache_key] = pygame.transform.smoothscale(image, size)
        return self._image_cache[cache_key]

    def get_scaled_background(self, image, size):
        """Cache scaled backgrounds"""
        cache_key = (id(image), size)
        if cache_key not in self._bg_cache:
            self._bg_cache[cache_key] = pygame.transform.smoothscale(image, size)
        return self._bg_cache[cache_key]

    # ---- Performance optimization methods
    def update_performance_mode(self):
        """Monitor FPS and automatically enable performance optimizations when needed"""
        current_time = time.time()

        # Calculate current FPS
        if hasattr(self, 'last_frame_time'):
            frame_time = current_time - self.last_frame_time
            if frame_time > 0:
                fps = 1.0 / frame_time
                self.fps_samples.append(fps)

                # Keep only last 30 samples for rolling average
                if len(self.fps_samples) > 30:
                    self.fps_samples.pop(0)

                avg_fps = sum(self.fps_samples) / len(self.fps_samples)

                # Enable performance mode if FPS drops below threshold
                if avg_fps < MIN_FPS_THRESHOLD and not self.performance_mode:
                    self.performance_mode = True
                    self.current_fps = PERFORMANCE_FPS

                # Disable performance mode if FPS is stable above threshold
                elif avg_fps > MIN_FPS_THRESHOLD + 10 and self.performance_mode:
                    self.performance_mode = False
                    self.current_fps = FPS

        self.last_frame_time = current_time

        # Enable additional optimizations for very small windows
        window_area = self.window_rect.w * self.window_rect.h
        small_window_threshold = 800 * 600  # Small window threshold

        self.skip_expensive_effects = (
            self.performance_mode or
            window_area < small_window_threshold or
            self.cell_size < MIN_CELL_SIZE_FOR_DETAILS
        )

    def should_skip_frame(self):
        """Determine if we should skip this frame for performance"""
        if not self.performance_mode:
            return False

        self.frame_skip_counter += 1
        # Skip every 2nd frame in performance mode
        if self.frame_skip_counter >= 2:
            self.frame_skip_counter = 0
            return False
        return True

    def get_optimized_maze_surface(self):
        """Create a pre-rendered maze surface for better performance"""
        if self._maze_surface is None or self._maze_surface_dirty:
            # Create surface for the entire maze
            maze_surface = pygame.Surface(self.maze_rect.size)

            cell = self.cell_size

            # Draw floor tiles
            for r in range(MAZE_ROWS):
                for c in range(MAZE_COLS):
                    x = c * cell
                    y = r * cell
                    idx = self.floor_map[r][c]
                    maze_surface.blit(self.scaled_floor_tiles[idx], (x, y))

            # Draw walls
            for r in range(MAZE_ROWS):
                for c in range(MAZE_COLS):
                    if self.maze[r][c].status == 0:
                        x = c * cell
                        y = r * cell
                        maze_surface.blit(self.scaled_wall_tile, (x, y))

            self._maze_surface = maze_surface
            self._maze_surface_dirty = False

        return self._maze_surface

    def invalidate_maze_surface(self):
        """Mark maze surface as dirty when maze changes"""
        self._maze_surface_dirty = True
        self._ui_surface_dirty = True

    def draw_optimized_ui(self, sidebar):
        """Draw UI elements with performance optimizations"""
        if self._ui_surface is None or self._ui_surface_dirty:
            # Pre-render UI elements that don't change often
            scale_factor = min(self.window_rect.w / 1920, self.window_rect.h / 1080)
            scale_factor = max(0.5, min(1.0, scale_factor))

            ui_surface = pygame.Surface(sidebar.size, pygame.SRCALPHA)

            # Draw sidebar background
            draw_glass_card(ui_surface, pygame.Rect(0, 0, sidebar.w, sidebar.h),
                          radius=22, bg=(18,24,18,190), border=(110,150,110), border_alpha=70)

            self._ui_surface = ui_surface
            self._ui_surface_dirty = False

        return self._ui_surface

    def draw_simplified_effects(self):
        """Draw simplified visual effects for performance mode"""
        if self.skip_expensive_effects:
            # Use simple rectangles instead of complex shadows and effects
            return True
        return False

    def run(self):
        while self.running:
            # Use adaptive FPS based on performance mode
            target_fps = self.current_fps if hasattr(self, 'current_fps') else FPS
            dt = self.clock.tick(target_fps)/1000.0

            self.handle_events()
            self.update(dt)

            if self.state=="start":
                self.draw_start()
            else:
                self.draw_game()

            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    App().run()
