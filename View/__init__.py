import os, sys, math, random, pygame, time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model import GenerationModel, SolvingModel
from View.components import Button, Dropdown, ModalHistory, ModalVictory
from View.sprites import FloatingBanana, MonkeyIdle
from View.utils import load_image, draw_shadow, draw_glass_card, draw_smooth_rect, try_load_font, calculate_button_size
from View.particle import ParticleSystem
#from Controller import MazeController


GAME_TITLE = "Monkey's Treasure"
FULLSCREEN = True  # Game khởi động ở chế độ fullscreen
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

        # box assets - UI boxes cho time, steps, algorithm
        self.box_assets = {
            'time': load_image(IMG("box/time_box.png")),
            'step': load_image(IMG("box/step_box.png")),
            'algorithm': load_image(IMG("box/algorithm_box.png")),
            'algorithm_choice': load_image(IMG("box/algorithm_choice_box.png")),
            'menu': load_image(IMG("box/menu_box.png"))
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
        self.font_chip = try_load_font(28)  # Font lớn hơn cho time/step boxes (jungle theme)

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
        
        # Maze generation animation
        self.generating_maze = False
        self.generation_model = None
        self.generation_timer = 0.0
        self.generation_speed = 0.01  # Seconds per step (tăng từ 0.003 lên 0.015 để chậm hơn, dễ quan sát)
        
        # Particle effects for wall breaking
        self.particle_system = ParticleSystem()
        self.last_broken_cells = []  # Track recently broken cells for particle emission

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
        start_size = calculate_button_size(self.btn_assets['start'], target_width=320)  # Tăng từ 240 lên 320
        self.btn_start = Button((0, 0, start_size[0], start_size[1]), "", self.font_ui, self.goto_game, theme='green', bg_image=self.btn_assets['start'], keep_aspect=False)

        # game UI
        self.compute_layout()

        # Tính toán vị trí sidebar và margin
        sidebar_left = self.window_rect.w - RIGHT_PANEL_W
        margin = 25  # Margin từ mép sidebar
        cur_y = 120  # Vị trí Y bắt đầu (tránh window controls)

        # Tính toán sidebar card thực tế (giống như trong draw_game)
        # sidebar card có margin 10px từ mép và width nhỏ hơn 20px
        sidebar_card_x = sidebar_left + 10  # +10px margin
        sidebar_card_w = RIGHT_PANEL_W - 20  # -20px margin (10px mỗi bên)

        # Chiều rộng các nút - giảm margin để nút lớn hơn
        side_margin = 10  # Margin rất nhỏ để nút tối đa hóa kích thước
        target_btn_w = sidebar_card_w - (side_margin * 2)  # Chiều rộng tối đa
        max_btn_h = 110  # Chiều cao tối đa (tăng từ 90 lên 110)
        row_spacing = 10  # Khoảng cách giữa các dòng

        # Vị trí X bắt đầu (căn giữa trong sidebar)
        spx = sidebar_left + side_margin

        # Helper function để tính kích thước nút với giới hạn chiều cao
        def get_button_size(asset, target_width, max_height=max_btn_h):
            size = calculate_button_size(asset, target_width=target_width)
            if size[1] > max_height:
                # Nếu cao quá, scale lại dựa trên chiều cao tối đa
                size = calculate_button_size(asset, target_height=max_height)
            return size

        # Tính kích thước nút giữ nguyên aspect ratio từ asset
        restart_size = get_button_size(self.btn_assets['restart'], target_btn_w)
        auto_size = get_button_size(self.btn_assets['auto'], target_btn_w)
        half_btn_w = (target_btn_w - 8) // 2
        play_size = get_button_size(self.btn_assets['small'], half_btn_w)
        # Generate button không dùng background image, tính kích thước dựa trên text
        generate_w = target_btn_w
        generate_h = 55  # Chiều cao cố định phù hợp với text
        generate_size = (generate_w, generate_h)
        history_size = get_button_size(self.btn_assets['history'], target_btn_w)
        back_size = get_button_size(self.btn_assets['back'], target_btn_w)

        # Dòng 1: Restart button (căn giữa trong sidebar card)
        restart_x = sidebar_card_x + (sidebar_card_w - restart_size[0]) // 2
        self.btn_restart = Button((restart_x, cur_y, restart_size[0], restart_size[1]), "", self.font_ui, 
                                  self.restart_level, theme='orange', 
                                  bg_image=self.btn_assets['restart'], keep_aspect=True)
        cur_y += restart_size[1] + row_spacing

        # Dòng 2: Auto button (căn giữa trong sidebar card)
        auto_x = sidebar_card_x + (sidebar_card_w - auto_size[0]) // 2
        self.btn_auto = Button((auto_x, cur_y, auto_size[0], auto_size[1]), "", self.font_ui, 
                              self.toggle_auto, theme='blue', 
                              bg_image=self.btn_assets['auto'], keep_aspect=True)
        cur_y += auto_size[1] + row_spacing

        # Dòng 3: Play và Pause (2 nút căn giữa trong sidebar card)
        total_play_width = play_size[0] * 2 + 8  # Tổng chiều rộng 2 nút + khoảng cách
        play_start_x = sidebar_card_x + (sidebar_card_w - total_play_width) // 2
        self.btn_play = Button((play_start_x, cur_y, play_size[0], play_size[1]), "", self.font_ui, 
                              self.toggle_play, theme='green', 
                              bg_image=self.btn_assets['small'], keep_aspect=True)
        self.btn_pause = Button((play_start_x + play_size[0] + 8, cur_y, play_size[0], play_size[1]), "", 
                               self.font_ui, self.toggle_play, theme='yellow', 
                               bg_image=self.btn_assets['small'], keep_aspect=True)
        cur_y += play_size[1] + row_spacing + 5  # Thêm khoảng cách trước dropdown

        # Dòng 4: Dropdown solving algorithm (căn giữa trong sidebar card)
        dropdown_x = sidebar_card_x + (sidebar_card_w - target_btn_w) // 2
        self.dropdown = Dropdown((dropdown_x, cur_y, target_btn_w, 42), self.font_small, 
                                ["BFS","DFS","UCS","A*","Bidirectional"], 
                                default_text="Solving Algorithm", 
                                on_select=self.set_algo)
        cur_y += 42 + row_spacing

        # Dòng 5: Dropdown generation algorithm (căn giữa trong sidebar card)
        self.maze_gen_dropdown = Dropdown((dropdown_x, cur_y, target_btn_w, 42), self.font_small, 
                                         ["DFS", "Kruskal", "Binary Tree", "Wilson", "Recursive Div."], 
                                         default_text="Generation Algorithm", 
                                         on_select=self.set_generation_algo)
        cur_y += 42 + row_spacing

        # Dòng 6: Generate button (căn giữa trong sidebar card)
        generate_x = sidebar_card_x + (sidebar_card_w - generate_size[0]) // 2
        self.btn_generate = Button((generate_x, cur_y, generate_size[0], generate_size[1]), "Generate Maze", 
                                  self.font_ui, self.generate_maze, theme='green', 
                                  keep_aspect=False)  # Không keep aspect vì không có bg_image
        cur_y += generate_size[1] + row_spacing + 5  # Thêm khoảng cách trước history/back

        # Dòng 7: History button (căn giữa trong sidebar card)
        history_x = sidebar_card_x + (sidebar_card_w - history_size[0]) // 2
        self.btn_history = Button((history_x, cur_y, history_size[0], history_size[1]), "", self.font_ui, 
                                 self.open_history, theme='purple', 
                                 bg_image=self.btn_assets['history'], keep_aspect=True)
        cur_y += history_size[1] + row_spacing

        # Dòng 8: Back button (căn giữa trong sidebar card)
        back_x = sidebar_card_x + (sidebar_card_w - back_size[0]) // 2
        self.btn_back = Button((back_x, cur_y, back_size[0], back_size[1]), "", self.font_ui, 
                              self.goto_start, theme='red', 
                              bg_image=self.btn_assets['back'], keep_aspect=True)

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
        
        # Tính toán sidebar card thực tế (giống như trong draw_game)
        sidebar_card_margin = int(10 * scale_factor)  # Margin của sidebar card
        sidebar_card_x = sidebar_left + sidebar_card_margin
        sidebar_card_w = scaled_panel_w - (sidebar_card_margin * 2)
        
        side_margin = int(10 * scale_factor)  # Margin các nút trong sidebar
        side_margin = max(8, side_margin)  # Margin tối thiểu
        cur_y = 120

        # Chiều rộng các nút
        target_btn_w = sidebar_card_w - (side_margin * 2)
        row_spacing = max(6, int(8 * scale_factor))  # Giảm từ 10 xuống 8
        
        # Chiều cao cố định cho tất cả các nút để đồng nhất
        target_btn_h = int(85 * scale_factor)  
        target_btn_h = max(70, target_btn_h)

        # Tính kích thước riêng cho từng nút trước
        restart_size_temp = calculate_button_size(self.btn_assets['restart'], target_height=target_btn_h)
        auto_size_temp = calculate_button_size(self.btn_assets['auto'], target_height=target_btn_h)
        
        # Lấy chiều rộng lớn nhất để tất cả các nút restart và auto có cùng kích thước
        max_width = max(restart_size_temp[0], auto_size_temp[0])
        restart_size = (max_width, target_btn_h)
        auto_size = (max_width, target_btn_h)
        
        # Generate button không dùng background image, tính kích thước dựa trên text
        generate_w = target_btn_w
        generate_h = int(50 * scale_factor)  # Giảm từ 55 xuống 50
        generate_h = max(40, generate_h)  # Giảm từ 45 xuống 40
        generate_size = (generate_w, generate_h)
        history_size = calculate_button_size(self.btn_assets['history'], target_height=target_btn_h)
        back_size = calculate_button_size(self.btn_assets['back'], target_height=target_btn_h)

        # Dòng 1: Restart button (căn giữa trong sidebar card)
        restart_x = sidebar_card_x + (sidebar_card_w - restart_size[0]) // 2
        self.btn_restart.rect = pygame.Rect(restart_x, cur_y, restart_size[0], restart_size[1])
        if self.btn_restart.bg_image:
            self.btn_restart.scaled_bg = pygame.transform.smoothscale(
                self.btn_restart.bg_image, restart_size)
        cur_y += restart_size[1] + row_spacing

        # Dòng 2: Auto button (căn giữa trong sidebar card)
        auto_x = sidebar_card_x + (sidebar_card_w - auto_size[0]) // 2
        self.btn_auto.rect = pygame.Rect(auto_x, cur_y, auto_size[0], auto_size[1])
        if self.btn_auto.bg_image:
            self.btn_auto.scaled_bg = pygame.transform.smoothscale(
                self.btn_auto.bg_image, auto_size)
        cur_y += auto_size[1] + row_spacing

        # Dòng 3: Dropdown solving algorithm (căn giữa trong sidebar card)
        dropdown_h = int(42 * scale_factor)
        dropdown_h = max(35, dropdown_h)
        dropdown_x = sidebar_card_x + (sidebar_card_w - target_btn_w) // 2
        self.dropdown.rect = pygame.Rect(dropdown_x, cur_y, target_btn_w, dropdown_h)
        cur_y += dropdown_h + row_spacing

        # Dòng 4: Dropdown generation algorithm (căn giữa trong sidebar card)
        self.maze_gen_dropdown.rect = pygame.Rect(dropdown_x, cur_y, target_btn_w, dropdown_h)
        cur_y += dropdown_h + row_spacing

        # Dòng 5: Generate button (căn giữa trong sidebar card)
        generate_x = sidebar_card_x + (sidebar_card_w - generate_size[0]) // 2
        self.btn_generate.rect = pygame.Rect(generate_x, cur_y, generate_size[0], generate_size[1])
        cur_y += generate_size[1] + row_spacing

        # Dòng 6: History button (căn giữa trong sidebar card)
        history_x = sidebar_card_x + (sidebar_card_w - history_size[0]) // 2
        self.btn_history.rect = pygame.Rect(history_x, cur_y, history_size[0], history_size[1])
        if self.btn_history.bg_image:
            self.btn_history.scaled_bg = pygame.transform.smoothscale(
                self.btn_history.bg_image, history_size)
        cur_y += history_size[1] + row_spacing

        # Dòng 7: Back button (căn giữa trong sidebar card)
        back_x = sidebar_card_x + (sidebar_card_w - back_size[0]) // 2
        self.btn_back.rect = pygame.Rect(back_x, cur_y, back_size[0], back_size[1])
        if self.btn_back.bg_image:
            self.btn_back.scaled_bg = pygame.transform.smoothscale(
                self.btn_back.bg_image, back_size)

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
        """Sinh mê cung mới với hiệu ứng animation"""
        if not hasattr(self, 'selected_generation_algo') or self.selected_generation_algo is None:
            return

        # Clear old particles
        self.particle_system.clear()
        
        # Tạo model với animation enabled
        self.generation_model = GenerationModel(MAZE_COLS, MAZE_ROWS, self.selected_generation_algo)
        self.generation_model.animated_generation = True
        
        # Generate maze để tạo animation steps
        # Model sẽ tự động khởi tạo maze về trạng thái ban đầu khi animated_generation = True
        self.generation_model.generate_maze()
        
        # Copy maze trạng thái ban đầu từ model
        self.maze = self.generation_model.Maze
        
        # Bắt đầu animation
        self.generating_maze = True
        self.generation_timer = 0.0
        
        # Reset game state
        self.player = [1, 1]
        self.steps = 0
        self.timer = 0.0
        self.start_time = time.time()
        self.paused = True  # Pause trong lúc đang generate
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
        # Update particle system
        self.particle_system.update(dt)
        
        # Update maze generation animation
        if self.generating_maze:
            self.generation_timer += dt
            
            # Apply multiple steps per frame for smoother animation (giảm xuống để chậm hơn)
            steps_per_frame = max(1, int(0.016 / self.generation_speed)) if self.generation_speed > 0 else 1
            
            for _ in range(steps_per_frame):
                if self.generation_model and self.generation_model.current_step < len(self.generation_model.generation_steps):
                    # Get current step info BEFORE applying
                    current_step_idx = self.generation_model.current_step
                    if current_step_idx < len(self.generation_model.generation_steps):
                        x, y, action = self.generation_model.generation_steps[current_step_idx]
                        
                        # Apply next step
                        has_more = self.generation_model.apply_next_step()
                        
                        # Emit particles based on action
                        if self.maze_rect and self.cell_size:
                            # Calculate screen position
                            screen_x = self.maze_rect.x + x * self.cell_size + self.cell_size // 2
                            screen_y = self.maze_rect.y + y * self.cell_size + self.cell_size // 2
                            
                            if action == 'break_wall':
                                # Wall breaking - dramatic effect
                                self.particle_system.emit_wall_break(screen_x, screen_y, self.cell_size)
                            elif action == 'path':
                                # Path creation - subtle effect
                                self.particle_system.emit_path_creation(screen_x, screen_y, self.cell_size)
                            elif action == 'build_wall':
                                # Building wall - different color particles
                                self.particle_system.emit_path_creation(
                                    screen_x, screen_y, self.cell_size, 
                                    path_color=(150, 100, 100)
                                )
                    
                    # Copy updated maze state
                    self.maze = self.generation_model.Maze
                    
                    if not has_more:
                        # Animation complete - set start and end positions
                        self.generating_maze = False
                        self.paused = False
                        
                        # Find and set start position (first path cell)
                        start_found = False
                        for y in range(MAZE_ROWS):
                            for x in range(MAZE_COLS):
                                if self.maze[y][x].status == 1:
                                    self.maze[y][x].status = 2  # Start
                                    self.player = [x, y]
                                    start_found = True
                                    break
                            if start_found:
                                break
                        
                        # Find and set end position (last path cell)
                        end_found = False
                        for y in range(MAZE_ROWS - 1, -1, -1):
                            for x in range(MAZE_COLS - 1, -1, -1):
                                if self.maze[y][x].status == 1:
                                    self.maze[y][x].status = 3  # End
                                    end_found = True
                                    break
                            if end_found:
                                break
                        
                        self.MazeGenerated = self.maze
                        self.start_time = time.time()
                        
                        # Clear particles when done
                        self.particle_system.clear()
                        break
                else:
                    self.generating_maze = False
                    break
        
        # Update game state
        if self.state=="game" and not self.paused:
            self.timer += dt; self.monkey_idle.update(dt); self.banana.update(dt)

    def draw_start(self):
        # background full, no blur
        bg = pygame.transform.smoothscale(self.bg_start, (self.window_rect.w, self.window_rect.h))
        self.screen.blit(bg, (0, 0))

        # Cập nhật kích thước nút START theo tỷ lệ cửa sổ
        base_width = 320  # Kích thước cơ bản (tăng từ 240 lên 320)
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

        # Vẽ sidebar bán trong suốt (cả performance mode và normal mode)
        if self.skip_expensive_effects:
            # Simple sidebar với alpha cho performance mode
            sidebar_surface = pygame.Surface(sidebar.size, pygame.SRCALPHA)
            sidebar_surface.fill((18,24,18,80))  # Bán trong suốt trong performance mode
            self.screen.blit(sidebar_surface, sidebar.topleft)
            pygame.draw.rect(self.screen, (110,150,110), sidebar, 2, border_radius=12)
        else:
            # Full quality sidebar - Nền rất trong suốt để thấy rõ background phía sau
            draw_glass_card(self.screen, sidebar, radius=22, bg=(18,24,18,100), border=(110,150,110), border_alpha=90)

        # chips - căn giữa trong sidebar
        # Hiển thị trạng thái generating nếu đang generate maze
        if self.generating_maze and self.generation_model:
            status_text = f"Generating... {self.generation_model.current_step}/{len(self.generation_model.generation_steps)}"
            status_color = (255, 255, 100)  # Màu vàng
            status_label = self.font_small.render(status_text, True, status_color)
            status_x = sidebar.x + (sidebar.width - status_label.get_width()) // 2
            status_y = sidebar.y + int(20*scale_factor)
            self.screen.blit(status_label, (status_x, status_y))
        
        t = f"{int(self.timer//60):02d}:{int(self.timer%60):02d}"
        y0 = sidebar.y+int(35*scale_factor)  # Giảm từ 50 xuống 35 để nhích lên
        chip_spacing = int(10*scale_factor)
        
        # Tính kích thước time box dựa trên aspect ratio của asset - TO HƠN
        time_box_img = self.box_assets['time']
        time_box_aspect = time_box_img.get_width() / time_box_img.get_height()
        target_time_h = max(70, int(50 * scale_factor))  
        chip1_w = int(target_time_h * time_box_aspect)  # Chiều rộng giữ tỷ lệ
        chip1_h = target_time_h
        
        # Tính kích thước step box dựa trên aspect ratio của asset - TO HƠN
        step_box_img = self.box_assets['step']
        step_box_aspect = step_box_img.get_width() / step_box_img.get_height()
        target_step_h = target_time_h  # Cùng chiều cao với time box
        chip2_w = int(target_step_h * step_box_aspect)  # Chiều rộng giữ tỷ lệ
        chip2_h = target_step_h
        
        total_chip_w = chip1_w + chip_spacing + chip2_w
        
        # Căn giữa cả 2 chips trong sidebar
        chips_start_x = sidebar.x + (sidebar.width - total_chip_w) // 2
        chip1 = pygame.Rect(chips_start_x, y0, chip1_w, chip1_h)

        # Vẽ time box với background image (giữ tỷ lệ gốc)
        time_box_scaled = pygame.transform.smoothscale(self.box_assets['time'], (chip1_w, chip1_h))
        self.screen.blit(time_box_scaled, chip1.topleft)

        # Font lớn hơn và in đậm cho time (jungle theme)
        time_label = self.font_chip.render(t, True, (255, 250, 220))  # Màu vàng kem
        time_x = chip1.x + (chip1.width - time_label.get_width()) // 2  # Căn giữa
        time_y = chip1.y + (chip1.height - time_label.get_height()) // 2  # Căn giữa
        self.screen.blit(time_label, (time_x, time_y))

        chip2 = pygame.Rect(chip1.right + chip_spacing, y0, chip2_w, chip2_h)

        # Vẽ step box với background image (giữ tỷ lệ gốc)
        step_box_scaled = pygame.transform.smoothscale(self.box_assets['step'], (chip2_w, chip2_h))
        self.screen.blit(step_box_scaled, chip2.topleft)

        # Font lớn hơn và in đậm cho steps (jungle theme)
        steps_label = self.font_chip.render(str(self.steps), True, (255, 250, 220))  # Màu vàng kem
        steps_x = chip2.x + (chip2.width - steps_label.get_width()) // 2  # Căn giữa
        steps_y = chip2.y + (chip2.height - steps_label.get_height()) // 2  # Căn giữa
        self.screen.blit(steps_label, (steps_x, steps_y))

        # buttons - layout mới: mỗi nút chính một hàng riêng, căn giữa, giữ aspect ratio
        cur_y = y0 + chip1_h + int(16*scale_factor)  # Giảm từ 24 xuống 16
        side_margin = int(10*scale_factor)  # Margin rất nhỏ để nút lớn nhất
        side_margin = max(8, side_margin)
        full_btn_w = scaled_panel_w - (side_margin * 2)  # Chiều rộng tối đa
        spacing = max(6, int(8*scale_factor))  # Giảm từ 10 xuống 8
        
        # Chiều cao cố định cho tất cả các nút để đồng nhất
        target_btn_h = int(85 * scale_factor)  
        target_btn_h = max(70, target_btn_h)

        # Tính kích thước riêng cho từng nút trước
        restart_size_temp = calculate_button_size(self.btn_assets['restart'], target_height=target_btn_h)
        auto_size_temp = calculate_button_size(self.btn_assets['auto'], target_height=target_btn_h)
        
        # Lấy chiều rộng lớn nhất để tất cả các nút restart và auto có cùng kích thước
        max_width = max(restart_size_temp[0], auto_size_temp[0])
        restart_size = (max_width, target_btn_h)
        auto_size = (max_width, target_btn_h)
        
        # Generate button không dùng background image, tính kích thước dựa trên text
        generate_w = full_btn_w
        generate_h = int(50 * scale_factor)  # Giảm từ 55 xuống 50
        generate_h = max(40, generate_h)  # Giảm từ 45 xuống 40
        generate_size = (generate_w, generate_h)
        history_size = calculate_button_size(self.btn_assets['history'], target_height=target_btn_h)
        back_size = calculate_button_size(self.btn_assets['back'], target_height=target_btn_h)

        # Dòng 1: Restart button (căn giữa)
        restart_x = sidebar.x + (scaled_panel_w - restart_size[0]) // 2
        self.btn_restart.rect = pygame.Rect(restart_x, cur_y, restart_size[0], restart_size[1])
        self.btn_restart.draw(self.screen)
        cur_y += restart_size[1] + spacing

        # Dòng 2: Auto button (căn giữa)
        auto_x = sidebar.x + (scaled_panel_w - auto_size[0]) // 2
        self.btn_auto.rect = pygame.Rect(auto_x, cur_y, auto_size[0], auto_size[1])
        self.btn_auto.draw(self.screen)
        cur_y += auto_size[1] + spacing

        # Dòng 3: Dropdown solving algorithm (căn giữa)
        dropdown_x = sidebar.x + (scaled_panel_w - full_btn_w) // 2
        self.dropdown.rect.topleft = (dropdown_x, cur_y)
        self.dropdown.rect.width = full_btn_w
        cur_y += self.dropdown.rect.height + spacing

        # Dòng 4: Dropdown generation algorithm (căn giữa)
        self.maze_gen_dropdown.rect.topleft = (dropdown_x, cur_y)
        self.maze_gen_dropdown.rect.width = full_btn_w
        cur_y += self.maze_gen_dropdown.rect.height + spacing

        # Dòng 5: Generate button (căn giữa)
        generate_x = sidebar.x + (scaled_panel_w - generate_size[0]) // 2
        self.btn_generate.rect = pygame.Rect(generate_x, cur_y, generate_size[0], generate_size[1])
        self.btn_generate.draw(self.screen)
        cur_y += generate_size[1] + spacing

        # Dòng 6: History button (căn giữa)
        history_x = sidebar.x + (scaled_panel_w - history_size[0]) // 2
        self.btn_history.rect = pygame.Rect(history_x, cur_y, history_size[0], history_size[1])
        self.btn_history.draw(self.screen)
        cur_y += history_size[1] + spacing

        # Dòng 7: Back button (căn giữa)
        back_x = sidebar.x + (scaled_panel_w - back_size[0]) // 2
        self.btn_back.rect = pygame.Rect(back_x, cur_y, back_size[0], back_size[1])
        self.btn_back.draw(self.screen)

        # Vẽ dropdown cuối cùng để chúng hiển thị trên các element khác
        # Vẽ dropdown đóng trước, dropdown đang mở sau để hiển thị trên cùng
        if self.dropdown.open:
            self.maze_gen_dropdown.draw(self.screen)
            self.dropdown.draw(self.screen)
        else:
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

            # draw player (monkey) - VẼ TRƯỚC walls để đứng sau tường
            px = self.maze_rect.x + self.player[0] * cell + (cell - self.monkey_idle.current().get_width())//2
            py = self.maze_rect.y + self.player[1] * cell + (cell - self.monkey_idle.current().get_height())//2
            self.screen.blit(self.monkey_idle.current(), (px, py))

            # draw banana goal - VẼ TRƯỚC walls để đứng sau tường
            gx = self.maze_rect.x + (MAZE_COLS - 2)*cell + (cell - self.banana.base_image.get_width())//2
            gy = self.maze_rect.y + (MAZE_ROWS - 2)*cell + (cell - self.banana.base_image.get_height())//2

            if self.skip_expensive_effects:
                # Static banana without animation
                self.screen.blit(self.banana.base_image, (gx, gy))
            else:
                # Animated floating banana
                self.banana.draw(self.screen, (gx, gy))

            # draw walls using cached scaled tile - VẼ SAU player và banana để che chúng
            for r in range(MAZE_ROWS):
                for c in range(MAZE_COLS):
                    if self.maze[r][c].status == 0:
                        x = self.maze_rect.x + c*cell; y = self.maze_rect.y + r*cell
                        # Use pre-scaled cached wall tile
                        self.screen.blit(self.scaled_wall_tile, (x, y))
            
            # Hiệu ứng cho đường đi đang được tạo
            if self.generating_maze and self.generation_model:
                current_step = self.generation_model.current_step - 1
                if current_step >= 0:
                    # Tạo hiệu ứng sáng cho các ô vừa phá tường
                    highlight_range = 8  # Số ô được highlight
                    for i in range(max(0, current_step - highlight_range), current_step + 1):
                        if i < len(self.generation_model.generation_steps):
                            step_x, step_y, action = self.generation_model.generation_steps[i]
                            
                            if action in ['break_wall', 'path']:
                                # Vẽ hiệu ứng cho path và break_wall
                                x = self.maze_rect.x + step_x * cell
                                y = self.maze_rect.y + step_y * cell
                                
                                # Tính độ sáng giảm dần theo thời gian
                                age = current_step - i
                                intensity = 1 - (age / highlight_range)
                                
                                # Màu vàng sáng cho ô vừa phá
                                if age == 0:
                                    # Ô hiện tại - sáng nhất với viền sáng
                                    overlay = pygame.Surface((cell, cell), pygame.SRCALPHA)
                                    overlay.fill((255, 255, 150, 220))
                                    self.screen.blit(overlay, (x, y))
                                    # Viền sáng
                                    pygame.draw.rect(self.screen, (255, 255, 200), (x, y, cell, cell), 2)
                                else:
                                    # Ô cũ hơn - gradient màu từ vàng sang xanh nhạt
                                    alpha = int(180 * intensity)
                                    r = int(255 * intensity + 100 * (1 - intensity))
                                    g = int(255 * intensity + 200 * (1 - intensity))
                                    b = int(150 * intensity + 150 * (1 - intensity))
                                    overlay = pygame.Surface((cell, cell), pygame.SRCALPHA)
                                    overlay.fill((r, g, b, alpha))
                                    self.screen.blit(overlay, (x, y))
                            
                            elif action == 'build_wall':
                                # Hiệu ứng xây tường (cho Recursive Division)
                                x = self.maze_rect.x + step_x * cell
                                y = self.maze_rect.y + step_y * cell
                                age = current_step - i
                                if age < 5:
                                    alpha = int(150 * (1 - age / 5))
                                    overlay = pygame.Surface((cell, cell), pygame.SRCALPHA)
                                    overlay.fill((200, 100, 100, alpha))
                                    self.screen.blit(overlay, (x, y))

        # Draw particles (vẽ SAU maze và player để particles nằm trên cùng)
        if self.generating_maze:
            self.particle_system.draw(self.screen)

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
