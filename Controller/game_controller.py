"""
Game Controller
Manages game state, logic, and coordinates between Model and View
"""
import time
from typing import Optional, Tuple, List, Dict
from Model import GenerationModel, SolvingModel


class GameController:
    """
    Controller for game logic and state management
    Separates business logic from View layer
    """
    
    def __init__(self, maze_cols: int = 25, maze_rows: int = 19):
        # Game configuration
        self.maze_cols = maze_cols
        self.maze_rows = maze_rows
        
        # Game state
        self.state = "start"  # "start", "game", "victory"
        self.paused = False
        self.game_won = False
        
        # Player state
        self.player_pos = [1, 1]  # Start position
        self.steps = 0
        
        # Timer
        self.timer = 0.0
        self.start_time = None
        
        # Maze
        self.maze = None
        self.maze_generated = None
        
        # Algorithm selection
        self.selected_algo = None  # Solving algorithm
        self.selected_generation_algo = None  # Generation algorithm
        
        # Auto-solve mode
        self.auto_on = False
        self.solver = None
        self.solution_path = []
        self.solution_index = 0
        
        # History
        self.history = []
        
        # Initialize with default maze
        self.generate_maze("DFS")
    
    def generate_maze(self, algorithm: str = "DFS"):
        """Generate new maze with specified algorithm"""
        self.selected_generation_algo = algorithm
        generation_model = GenerationModel(self.maze_cols, self.maze_rows, algorithm)
        self.maze_generated = generation_model.generate_maze()
        self.maze = self.maze_generated
        self.reset_game()
    
    def reset_game(self):
        """Reset game state"""
        self.steps = 0
        self.timer = 0.0
        self.start_time = time.time()
        self.paused = False
        self.game_won = False
        self.auto_on = False
        self.player_pos = [1, 1]
        self.solution_path = []
        self.solution_index = 0
        self.solver = None
    
    def start_game(self):
        """Start the game"""
        self.state = "game"
        self.reset_game()
    
    def restart_level(self):
        """Restart current level"""
        self.reset_game()
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        return self.paused
    
    def toggle_auto(self):
        """Toggle auto-solve mode"""
        self.auto_on = not self.auto_on
        
        if self.auto_on and self.selected_algo:
            # Initialize solver
            self.solve_maze(self.selected_algo)
        
        return self.auto_on
    
    def set_solving_algorithm(self, algorithm: str):
        """Set solving algorithm"""
        self.selected_algo = algorithm
    
    def set_generation_algorithm(self, algorithm: str):
        """Set generation algorithm"""
        self.selected_generation_algo = algorithm
    
    def solve_maze(self, algorithm: str) -> bool:
        """Solve current maze with specified algorithm"""
        if not self.maze:
            return False
        
        self.solver = SolvingModel(self.maze, self.maze_cols, self.maze_rows)
        
        # Find start and end positions from maze
        for y in range(self.maze_rows):
            for x in range(self.maze_cols):
                if self.maze[y][x].status == 2:  # Start
                    self.solver.start_pos = (x, y)
                elif self.maze[y][x].status == 3:  # End
                    self.solver.end_pos = (x, y)
        
        success = self.solver.solve_maze(algorithm)
        
        if success:
            self.solution_path = self.solver.solution_path
            self.solution_index = 0
        
        return success
    
    def move_player(self, dx: int, dy: int) -> bool:
        """
        Move player in specified direction
        Returns True if move was successful
        """
        if self.game_won or self.paused:
            return False
        
        c, r = self.player_pos
        nc, nr = c + dx, r + dy
        
        # Check bounds
        if not (0 <= nc < self.maze_cols and 0 <= nr < self.maze_rows):
            return False
        
        # Check if cell is walkable (Path, Start, or End)
        if self.maze[nr][nc].status in [1, 2, 3]:
            self.player_pos = [nc, nr]
            self.steps += 1
            
            # Check victory condition (reached end)
            if nc == self.maze_cols - 2 and nr == self.maze_rows - 2:
                self.game_won = True
                self.paused = True
                return True
            
            return True
        
        return False
    
    def auto_move(self) -> bool:
        """
        Automatically move player along solution path
        Returns True if moved, False if no more moves or auto is off
        """
        if not self.auto_on or not self.solution_path:
            return False
        
        if self.solution_index >= len(self.solution_path):
            return False
        
        target = self.solution_path[self.solution_index]
        current = self.player_pos
        
        # Calculate direction
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        
        # Normalize to single step
        if dx != 0:
            dx = 1 if dx > 0 else -1
        if dy != 0:
            dy = 1 if dy > 0 else -1
        
        # Try to move
        if self.move_player(dx, dy):
            # Check if reached target
            if self.player_pos == list(target):
                self.solution_index += 1
            return True
        
        return False
    
    def update(self, dt: float):
        """Update game state"""
        if self.state == "game" and not self.paused:
            self.timer += dt
            
            # Auto-solve movement (slower for visibility)
            if self.auto_on and hasattr(self, '_auto_timer'):
                self._auto_timer += dt
                if self._auto_timer >= 0.1:  # Move every 0.1 seconds
                    self._auto_timer = 0
                    self.auto_move()
            elif self.auto_on:
                self._auto_timer = 0
    
    def get_time_string(self) -> str:
        """Get formatted time string"""
        minutes = int(self.timer // 60)
        seconds = int(self.timer % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def save_history(self, label: str = "Manual"):
        """Save current run to history"""
        if self.start_time is None:
            return
        
        duration = self.timer
        steps = self.steps
        
        if duration <= 0 and steps <= 0:
            return
        
        # Calculate rank
        if duration < 30 and steps < 50:
            rank = "S"
        elif duration < 60:
            rank = "A"
        elif duration < 120:
            rank = "B"
        else:
            rank = "C"
        
        # Determine mode
        if "Auto" in label:
            mode = label
        elif self.auto_on:
            mode = f"Auto ({self.selected_algo or 'None'})"
        else:
            mode = "Manual"
        
        self.history.append({
            "time_str": self.get_time_string(),
            "steps": steps,
            "rank": rank,
            "mode": mode
        })
    
    def get_history(self) -> List[Dict]:
        """Get game history"""
        return self.history
    
    def goto_start(self):
        """Go back to start screen"""
        self.state = "start"
    
    def goto_game(self):
        """Go to game screen"""
        self.state = "game"
        self.reset_game()
