import os, sys, math, random, pygame, time

GAME_TITLE = "Monkey's Treasure"
FULLSCREEN = False
RIGHT_PANEL_W = 360
FPS = 60
MAZE_COLS, MAZE_ROWS = 21, 13
CELL_GAP = 0  # khít nhau

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
IMG = lambda name: os.path.join(ASSETS, name)

# ---------- Utility & Theme ----------
def load_image(path, alpha=True):
    try:
        img = pygame.image.load(path)
        return img.convert_alpha() if alpha else img.convert()
    except Exception as e:
        surf = pygame.Surface((64,64), pygame.SRCALPHA if alpha else 0)
        surf.fill((200,50,50,160) if alpha else (200,50,50))
        return surf

PALETTES = {
    'neutral': ((20,28,20), (28,36,28), (60,80,60)),
    'green'  : ((32,64,44), (48,104,74), (84,140,110)),
    'yellow' : ((88,72,24), (130,110,36), (170,140,50)),
    'orange' : ((120,64,30), (170,96,48), (210,130,70)),
    'blue'   : ((34,54,86),  (48,86,138), (72,118,170)),
    'purple' : ((52,34,86),  (88,58,140), (120,90,168)),
    'red'    : ((92,38,38),  (138,54,54), (170,84,84)),
}

def draw_shadow(surface, rect, radius=16, offset=(0,6), alpha=110):
    s = pygame.Surface((rect.w+20, rect.h+20), pygame.SRCALPHA)
    pygame.draw.rect(s, (0,0,0,alpha), pygame.Rect(10,10,rect.w,rect.h), border_radius=radius)
    surface.blit(s, (rect.x-10+offset[0], rect.y-10+offset[1]))

def draw_glass_card(surface, rect, radius=18, bg=(16,20,16,180), border=(90,120,90), border_alpha=60):
    draw_shadow(surface, rect, radius, (0,10), 120)
    card = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(card, bg, card.get_rect(), border_radius=radius)
    pygame.draw.rect(card, (*border, border_alpha), card.get_rect(), 2, border_radius=radius)
    surface.blit(card, rect.topleft)

def draw_smooth_rect(surface, rect, color, radius=16, border=0, border_color=(0,0,0)):
    # Supersampling to smooth edges
    scale = 2
    temp = pygame.Surface((rect.w*scale, rect.h*scale), pygame.SRCALPHA)
    pygame.draw.rect(temp, color, temp.get_rect(), border_radius=radius*scale)
    if border>0:
        pygame.draw.rect(temp, border_color, temp.get_rect(), border*scale, border_radius=radius*scale)
    temp = pygame.transform.smoothscale(temp, rect.size)
    surface.blit(temp, rect.topleft)

def try_load_font(size):
    prefer = os.path.join(ASSETS, "fonts", "PressStart2P.ttf")
    try:
        if os.path.exists(prefer):
            return pygame.font.Font(prefer, size)
    except:
        pass
    return pygame.font.SysFont(None, size)

# ---------- UI Controls ----------
class Button:
    def __init__(self, rect, text, font, on_click=None, tooltip=None, theme='neutral'):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.tooltip = tooltip
        self.enabled = True
        self.hovered = False
        self.theme = theme

    def draw(self, surface):
        color = (235,235,235) if self.enabled else (170,170,170)
        base, hover, border_col = PALETTES.get(self.theme, PALETTES['neutral'])
        bg = hover if self.hovered and self.enabled else base
        draw_shadow(surface, self.rect, radius=14, offset=(0,6), alpha=100)
        draw_smooth_rect(surface, self.rect, bg, radius=14, border=2, border_color=border_col)
        label = self.font.render(self.text, True, color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if not self.enabled: return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()

class Dropdown:
    def __init__(self, rect, font, options, default_text="None", on_select=None):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.options = options[:]
        self.open = False
        self.selected = None
        self.default_text = default_text
        self.on_select = on_select

    def draw(self, surface):
        bg = (20,28,20)
        border = (36,60,36)
        draw_shadow(surface, self.rect, radius=14, offset=(0,6), alpha=100)
        draw_smooth_rect(surface, self.rect, bg, radius=14, border=2, border_color=border)
        text = self.selected if self.selected else self.default_text
        label = self.font.render(text, True, (240,240,240))
        surface.blit(label, (self.rect.x+12, self.rect.y+(self.rect.h-label.get_height())//2))
        # caret
        pygame.draw.polygon(surface, (200,200,200),
                            [(self.rect.right-22, self.rect.y+self.rect.h//2-4),
                             (self.rect.right-12, self.rect.y+self.rect.h//2-4),
                             (self.rect.right-17, self.rect.y+self.rect.h//2+4)])
        if self.open:
            opt_h = self.rect.h
            panel = pygame.Rect(self.rect.x, self.rect.bottom+6, self.rect.w, opt_h*len(self.options))
            draw_shadow(surface, panel, radius=12, offset=(0,6), alpha=110)
            pygame.draw.rect(surface, (240,240,240), panel, border_radius=12)
            for i, opt in enumerate(self.options):
                r = pygame.Rect(panel.x, panel.y+i*opt_h, panel.w, opt_h)
                pygame.draw.rect(surface, (255,255,255), r, border_radius=0)
                lab = self.font.render(opt, True, (40,40,40))
                surface.blit(lab, (r.x+12, r.y+(r.h-lab.get_height())//2))
                pygame.draw.line(surface, (230,230,230), (r.x, r.bottom-1), (r.right, r.bottom-1))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.open:
                opt_h = self.rect.h
                panel = pygame.Rect(self.rect.x, self.rect.bottom+6, self.rect.w, opt_h*len(self.options))
                if panel.collidepoint(event.pos):
                    index = (event.pos[1]-panel.y)//opt_h
                    if 0 <= index < len(self.options):
                        self.selected = self.options[index]
                        if self.on_select: self.on_select(self.selected)
                    self.open = False
                elif self.rect.collidepoint(event.pos):
                    self.open = False
                else:
                    self.open = False
            else:
                if self.rect.collidepoint(event.pos):
                    self.open = True

class ModalHistory:
    def __init__(self, get_history):
        self.get_history = get_history
        self.visible = False

    def draw(self, surface, screen_rect, font_header, font_row):
        if not self.visible: return
        overlay = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        surface.blit(overlay, (0,0))
        w = int(screen_rect.w*0.65); h = int(screen_rect.h*0.65)
        panel = pygame.Rect((screen_rect.w-w)//2, (screen_rect.h-h)//2, w, h)
        draw_glass_card(surface, panel, radius=18, bg=(250,250,250,235), border=(60,60,60), border_alpha=80)
        title = font_header.render("History", True, (20,20,20))
        surface.blit(title, (panel.x+16, panel.y+12))
        headers = ["#", "Time", "Steps", "Rank", "Mode"]
        col_w = [60, 200, 160, 120, w-60-200-160-120-48]
        x = panel.x+24; y = panel.y+64
        for i, head in enumerate(headers):
            lab = font_row.render(head, True, (60,60,60)); surface.blit(lab, (x, y)); x += col_w[i]
        y += 28; pygame.draw.line(surface, (220,220,220), (panel.x+16, y), (panel.right-16, y))
        y += 12
        history = self.get_history()
        row_alt = (245,245,245)
        for idx, item in enumerate(history, start=1):
            if idx % 2 == 0:
                pygame.draw.rect(surface, row_alt, pygame.Rect(panel.x+16, y-4, panel.w-32, 26), border_radius=6)
            x = panel.x+24
            cols = [str(idx), item.get("time_str","--"), str(item.get("steps","--")), item.get("rank","--"), item.get("mode","--")]
            for i, val in enumerate(cols):
                lab = font_row.render(val, True, (40,40,40)); surface.blit(lab, (x, y)); x += col_w[i]
            y += 26
            if y > panel.bottom-32: break

# ---------- Sprites ----------
class FloatingBanana(pygame.sprite.Sprite):
    def __init__(self, image, cell_size):
        super().__init__()
        self.base_image = image
        self.cell_size = cell_size
        self.image = image
        self.rect = self.image.get_rect()
        self.t = 0.0

    def update(self, dt):
        self.t += dt
        dy = math.sin(self.t*2.2) * (self.cell_size*0.10)
        self.offset = (0, int(dy))

    def draw(self, surface, pos_px):
        shadow = pygame.Surface((self.rect.w, self.rect.h//6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,80), shadow.get_rect())
        surface.blit(shadow, (pos_px[0], pos_px[1]+self.rect.h-6))
        surface.blit(self.base_image, (pos_px[0], pos_px[1]+self.offset[1]))

class MonkeyIdle(pygame.sprite.Sprite):
    def __init__(self, frames, fallback, cell_size):
        super().__init__()
        self.frames = frames if frames else [fallback]
        self.cell_size = cell_size
        self.index = 0; self.timer = 0.0; self.fps = 6 if len(self.frames)>1 else 0

    def update(self, dt):
        if self.fps>0 and len(self.frames)>1:
            self.timer += dt
            if self.timer >= 1.0/self.fps:
                self.timer = 0.0; self.index = (self.index+1) % len(self.frames)

    def current(self):
        return self.frames[self.index]

# ---------- Maze data ----------
def make_placeholder_maze(cols, rows):
    grid = [[1 if random.random()<0.25 else 0 for _ in range(cols)] for _ in range(rows)]
    grid[0][0] = 0; grid[rows-1][cols-1] = 0
    return grid

# ---------- App ----------
class App:
    def __init__(self):
        pygame.init()
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode((1280, 800), flags)
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.window_rect = self.screen.get_rect()
        self.running = True

        # Performance optimization - Cache system
        self._image_cache = {}
        self._surface_cache = {}
        self._last_cell_size = None
        self._bg_cache = {}

        # assets
        self.bg_jungle = load_image(IMG("bg_jungle.png"))
        self.bg_start = load_image(IMG("bg_start.png"))
        self.tile_wall = load_image(IMG("tile_wall.png"))
        self.monkey_img = load_image(IMG("monkey.png"))
        self.banana_img = load_image(IMG("banana_rainbow.png"))

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
        self.modal_history = ModalHistory(lambda: self.history)

        # window controls
        self.btn_close = Button((self.window_rect.w-48-12, 12, 48, 28), "✕", self.font_small, self.quit, theme='red')
        self.btn_max   = Button((self.window_rect.w-48-12-56, 12, 48, 28), "▢", self.font_small, self.toggle_fullscreen, theme='blue')
        self.btn_min   = Button((self.window_rect.w-48-12-112, 12, 48, 28), "—", self.font_small, self.minimize, theme='yellow')

        # start screen
        self.btn_start = Button((0,0,260,56), "START", self.font_ui, self.goto_game, theme='green')

        # game UI
        self.compute_layout()
        spx = self.window_rect.w - RIGHT_PANEL_W + 20
        cur_y = 110  # moved down so not covered by window controls
        self.btn_restart = Button((spx, cur_y, RIGHT_PANEL_W-40, 48), "↻  RESTART", self.font_ui, self.restart_level, theme='orange'); cur_y+=64
        self.btn_play    = Button((spx, cur_y, (RIGHT_PANEL_W-48)//2, 48), "▶  PLAY",  self.font_ui, self.toggle_play, theme='green')
        self.btn_pause   = Button((spx+(RIGHT_PANEL_W-48)//2+8, cur_y, (RIGHT_PANEL_W-48)//2, 48), "⏸  PAUSE", self.font_ui, self.toggle_play, theme='yellow'); cur_y+=64
        self.btn_auto    = Button((spx, cur_y, RIGHT_PANEL_W-40, 48), "⚙  AUTO SOLVE", self.font_ui, self.toggle_auto, theme='blue'); cur_y+=64
        self.dropdown    = Dropdown((spx, cur_y, RIGHT_PANEL_W-40, 44), self.font_ui, ["BFS","DFS","UCS","A*","Bidirectional Search"], default_text="None", on_select=self.set_algo); cur_y+=64
        self.btn_history = Button((spx, cur_y, RIGHT_PANEL_W-40, 48), "🕘  HISTORY", self.font_ui, self.open_history, theme='purple'); cur_y+=64
        self.btn_back    = Button((spx, cur_y, RIGHT_PANEL_W-40, 48), "←  BACK", self.font_ui, self.goto_start, theme='red')

        # maze
        self.maze = make_placeholder_maze(MAZE_COLS, MAZE_ROWS)
        self.player = [0,0]
        self.prepare_sprites()

        # prebuild random floor map for repeatability
        random.seed(42)
        self.floor_map = [[random.randrange(len(self.floor_tiles)) for _ in range(MAZE_COLS)] for _ in range(MAZE_ROWS)]

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
    def minimize(self):
        try: pygame.display.iconify()
        except: pass

    def toggle_fullscreen(self):
        global FULLSCREEN
        FULLSCREEN = not FULLSCREEN
        if FULLSCREEN:
            pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((1280,800))
        self.screen = pygame.display.get_surface()
        self.window_rect = self.screen.get_rect()
        self.compute_layout()

    def quit(self):
        self.running = False

    # ---- Layout
    def compute_layout(self):
        screen = self.window_rect
        left_space = screen.w - RIGHT_PANEL_W
        margin = 24
        avail_w = left_space - margin*2
        avail_h = screen.h - margin*2
        cell_w = avail_w // MAZE_COLS
        cell_h = avail_h // MAZE_ROWS
        self.cell_size = min(cell_w, cell_h)
        maze_w = self.cell_size * MAZE_COLS
        maze_h = self.cell_size * MAZE_ROWS
        self.maze_rect = pygame.Rect((left_space - maze_w)//2 + margin, (screen.h-maze_h)//2, maze_w, maze_h)

    # ---- State transitions
    def goto_start(self):
        self.save_run(label="Manual" if not self.auto_on else f"Auto ({self.selected_algo or 'None'})")
        self.state = "start"; self.modal_history.visible=False

    def goto_game(self):
        self.state = "game"; self.reset_run()

    def reset_run(self):
        self.steps = 0; self.timer = 0.0; self.start_time = time.time()
        self.paused = False; self.auto_on=False
        self.player=[0,0]
        self.maze = make_placeholder_maze(MAZE_COLS, MAZE_ROWS)

    def restart_level(self): self.reset_run()
    def toggle_play(self): self.paused = not self.paused
    def toggle_auto(self): self.auto_on = not self.auto_on
    def set_algo(self, name): self.selected_algo = name
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
            if self.state == "start": self.btn_start.handle_event(event)
            for b in (self.btn_close, self.btn_max, self.btn_min): b.handle_event(event)
            if self.state == "game":
                for b in (self.btn_restart, self.btn_play, self.btn_pause, self.btn_auto, self.btn_history, self.btn_back): b.handle_event(event)
                self.dropdown.handle_event(event)
                if event.type == pygame.KEYDOWN and not self.paused:
                    if event.key in (pygame.K_LEFT, pygame.K_a): self.move(-1,0)
                    if event.key in (pygame.K_RIGHT, pygame.K_d): self.move(1,0)
                    if event.key in (pygame.K_UP, pygame.K_w): self.move(0,-1)
                    if event.key in (pygame.K_DOWN, pygame.K_s): self.move(0,1)
            if self.modal_history.visible and (event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN)):
                self.modal_history.visible=False

    def move(self, dx, dy):
        c, r = self.player; nc, nr = c+dx, r+dy
        if 0 <= nc < MAZE_COLS and 0 <= nr < MAZE_ROWS:
            if self.maze[nr][nc] == 0:
                self.player=[nc,nr]; self.steps+=1

    # ---- Update / Draw
    def update(self, dt):
        if self.state=="game" and not self.paused:
            self.timer += dt; self.monkey_idle.update(dt); self.banana.update(dt)

    def draw_start(self):
        # background full, no blur
        bg = pygame.transform.smoothscale(self.bg_start, (self.window_rect.w, self.window_rect.h))
        self.screen.blit(bg, (0,0))
        # place START slightly left and lower (~82% h)
        self.btn_start.rect.center = (int(self.window_rect.centerx*0.85), int(self.window_rect.h*0.82))
        self.btn_start.draw(self.screen)
        for b in (self.btn_min, self.btn_max, self.btn_close): b.draw(self.screen)

    def draw_game(self):
        # jungle background full - use cached version
        bg_scaled = self.get_scaled_background(self.bg_jungle, (self.window_rect.w, self.window_rect.h))
        self.screen.blit(bg_scaled, (0,0))

        # sidebar card
        sidebar = pygame.Rect(self.window_rect.w-RIGHT_PANEL_W+10, 14, RIGHT_PANEL_W-20, self.window_rect.h-28)
        draw_glass_card(self.screen, sidebar, radius=22, bg=(18,24,18,190), border=(110,150,110), border_alpha=70)
        # chips
        t = f"{int(self.timer//60):02d}:{int(self.timer%60):02d}"
        chip_h = 36; x0 = sidebar.x+18; y0 = sidebar.y+50
        chip1 = pygame.Rect(x0, y0, 140, chip_h)
        draw_smooth_rect(self.screen, chip1, (26,34,26,220), radius=18, border=2, border_color=(86,116,86))
        self.screen.blit(self.font_small.render("⏱  "+t, True, (235,235,235)), (chip1.x+12, chip1.y+7))
        chip2 = pygame.Rect(chip1.right+10, y0, 120, chip_h)
        draw_smooth_rect(self.screen, chip2, (26,34,26,220), radius=18, border=2, border_color=(86,116,86))
        self.screen.blit(self.font_small.render("🚶  "+str(self.steps), True, (235,235,235)), (chip2.x+12, chip2.y+7))

        # buttons
        spx = sidebar.x+18; cur_y = y0 + chip_h + 24
        self.btn_restart.rect.topleft = (spx, cur_y); cur_y+=64
        self.btn_play.rect.topleft = (spx, cur_y)
        self.btn_pause.rect.topleft = (spx+(RIGHT_PANEL_W-48)//2+8, cur_y); cur_y+=64
        self.btn_auto.rect.topleft = (spx, cur_y); cur_y+=64
        self.dropdown.rect.topleft = (spx, cur_y); cur_y+=64
        self.btn_history.rect.topleft = (spx, cur_y); cur_y+=64
        self.btn_back.rect.topleft = (spx, cur_y)
        for b in (self.btn_restart, self.btn_play, self.btn_pause, self.btn_auto, self.btn_history, self.btn_back):
            b.draw(self.screen)
        self.dropdown.draw(self.screen)

        # maze frame card
        draw_glass_card(self.screen, self.maze_rect, radius=16, bg=(12,22,12,140), border=(90,120,90), border_alpha=55)

        # draw random floor tiles using cached scaled versions
        cell = self.cell_size
        for r in range(MAZE_ROWS):
            for c in range(MAZE_COLS):
                x = self.maze_rect.x + c*cell
                y = self.maze_rect.y + r*cell
                idx = self.floor_map[r][c]
                # Use pre-scaled cached tiles instead of scaling every frame
                self.screen.blit(self.scaled_floor_tiles[idx], (x,y))

        # draw walls using cached scaled tile
        for r in range(MAZE_ROWS):
            for c in range(MAZE_COLS):
                if self.maze[r][c] == 1:
                    x = self.maze_rect.x + c*cell; y = self.maze_rect.y + r*cell
                    # Use pre-scaled cached wall tile
                    self.screen.blit(self.scaled_wall_tile, (x, y))

        # draw player
        px = self.maze_rect.x + self.player[0]*cell + (cell - self.monkey_idle.current().get_width())//2
        py = self.maze_rect.y + self.player[1]*cell + (cell - self.monkey_idle.current().get_height())//2
        self.screen.blit(self.monkey_idle.current(), (px, py))

        # draw banana goal
        gx = self.maze_rect.x + (MAZE_COLS-1)*cell + (cell - self.banana.base_image.get_width())//2
        gy = self.maze_rect.y + (MAZE_ROWS-1)*cell + (cell - self.banana.base_image.get_height())//2
        self.banana.draw(self.screen, (gx, gy))

        # window buttons
        for b in (self.btn_min, self.btn_max, self.btn_close): b.draw(self.screen)

        # history modal
        self.modal_history.draw(self.screen, self.window_rect, self.font_ui, self.font_small)

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

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)/1000.0
            self.handle_events(); self.update(dt)
            if self.state=="start": self.draw_start()
            else: self.draw_game()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    App().run()
