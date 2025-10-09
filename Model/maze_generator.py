"""
Maze Generation Algorithms
Contains GenerationModel class with various maze generation algorithms:
- DFS (Depth-First Search)
- Kruskal's Algorithm
- Binary Tree
- Wilson's Algorithm
- Recursive Division
"""
import random
from typing import List, Tuple, Optional
from Model.node_cell import Node_Cell


class GenerationModel:
    """Model for generating mazes using various algorithms"""
    
    def __init__(self, maze_width: int, maze_height: int, algorithm: str):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.Algorithm = algorithm
        self.Maze = [[Node_Cell(x, y, 0, False, float('inf'), float('inf')) 
                     for x in range(maze_width)] 
                     for y in range(maze_height)]
        self.Maze_Backup = self.Maze
        
        # Generation properties
        self.start_pos: Optional[Tuple[int, int]] = (1, 1)
        self.end_pos: Optional[Tuple[int, int]] = (maze_width - 2, maze_height - 2)
        self.generation_complete = False
        
        # Animation support
        self.animated_generation = False
        self.generation_steps = []  # List of (x, y, action) tuples
        self.current_step = 0

    def __get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighbors for maze generation (2 cells apart)"""
        neighbors = []
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < self.maze_width - 1 and 1 <= ny < self.maze_height - 1:
                neighbors.append((nx, ny))

        return neighbors

    def DFS(self):
        """Depth-First Search maze generation algorithm"""
        stack = [(1, 1)]
        visited = set()
        visited.add((1, 1))
        self.Maze[1][1].status = 1  # Path
        
        if self.animated_generation:
            self.generation_steps.append((1, 1, 'path'))

        while stack:
            current_x, current_y = stack[-1]
            neighbors = self.__get_neighbors(current_x, current_y)

            # Filter unvisited neighbors
            unvisited_neighbors = []
            for nx, ny in neighbors:
                if (nx, ny) not in visited and self.Maze[ny][nx].status == 0:
                    unvisited_neighbors.append((nx, ny))

            if unvisited_neighbors:
                next_x, next_y = random.choice(unvisited_neighbors)
                visited.add((next_x, next_y))

                # Break wall between current and next
                wall_x = (current_x + next_x) // 2
                wall_y = (current_y + next_y) // 2
                self.Maze[wall_y][wall_x].status = 1
                self.Maze[next_y][next_x].status = 1
                
                if self.animated_generation:
                    self.generation_steps.append((wall_x, wall_y, 'break_wall'))
                    self.generation_steps.append((next_x, next_y, 'path'))

                stack.append((next_x, next_y))
            else:
                stack.pop()

    def Kruskal(self):
        """Kruskal's maze generation algorithm"""
        walls = []

        # Initialize odd cells as paths
        for y in range(1, self.maze_height, 2):
            for x in range(1, self.maze_width, 2):
                self.Maze[y][x].status = 1
                
                if self.animated_generation:
                    self.generation_steps.append((x, y, 'path'))

                if x + 2 < self.maze_width:
                    walls.append((x, y, x + 2, y))
                if y + 2 < self.maze_height:
                    walls.append((x, y, x, y + 2))

        random.shuffle(walls)

        # Union-Find data structure
        parent = {}

        def find(pos):
            if pos not in parent:
                parent[pos] = pos
            if parent[pos] != pos:
                parent[pos] = find(parent[pos])
            return parent[pos]

        def union(pos1, pos2):
            p1, p2 = find(pos1), find(pos2)
            if p1 != p2:
                parent[p1] = p2
                return True
            return False

        # Break walls if cells are not connected
        for x1, y1, x2, y2 in walls:
            if union((x1, y1), (x2, y2)):
                wall_x = (x1 + x2) // 2
                wall_y = (y1 + y2) // 2
                self.Maze[wall_y][wall_x].status = 1
                
                if self.animated_generation:
                    self.generation_steps.append((wall_x, wall_y, 'break_wall'))

    def Binary_Tree(self):
        """Binary Tree maze generation algorithm"""
        for y in range(1, self.maze_height, 2):
            for x in range(1, self.maze_width, 2):
                self.Maze[y][x].status = 1
                
                if self.animated_generation:
                    self.generation_steps.append((x, y, 'path'))

                directions = []
                if y > 1:
                    directions.append("up")
                if x > 1:
                    directions.append("left")

                if directions:
                    direction = random.choice(directions)
                    if direction == "up":
                        self.Maze[y - 1][x].status = 1
                        if self.animated_generation:
                            self.generation_steps.append((x, y - 1, 'break_wall'))
                    else:
                        self.Maze[y][x - 1].status = 1
                        if self.animated_generation:
                            self.generation_steps.append((x - 1, y, 'break_wall'))

    def Wilson(self):
        """Wilson's maze generation algorithm"""
        cells = [(x, y) for y in range(1, self.maze_height, 2)
                 for x in range(1, self.maze_width, 2)]

        start = random.choice(cells)
        self.Maze[start[1]][start[0]].status = 1
        
        if self.animated_generation:
            self.generation_steps.append((start[0], start[1], 'path'))
        
        remaining = [cell for cell in cells if cell != start]

        while remaining:
            current = random.choice(remaining)
            path = [current]

            while self.Maze[current[1]][current[0]].status != 1:
                neighbors = self.__get_neighbors(current[0], current[1])
                valid_neighbors = [(x, y) for x, y in neighbors
                                   if 1 <= x < self.maze_width - 1 and 1 <= y < self.maze_height - 1]

                if valid_neighbors:
                    next_cell = random.choice(valid_neighbors)

                    if next_cell in path:
                        path = path[:path.index(next_cell) + 1]
                    else:
                        path.append(next_cell)

                    current = next_cell

            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]

                self.Maze[y1][x1].status = 1
                
                if self.animated_generation:
                    self.generation_steps.append((x1, y1, 'path'))

                wall_x = (x1 + x2) // 2
                wall_y = (y1 + y2) // 2
                self.Maze[wall_y][wall_x].status = 1
                
                if self.animated_generation:
                    self.generation_steps.append((wall_x, wall_y, 'break_wall'))

            remaining = [cell for cell in remaining
                        if self.Maze[cell[1]][cell[0]].status != 1]

    def Recursive_Division(self):
        """Recursive Division maze generation algorithm"""
        # Start with all paths
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if y == 0 or y == self.maze_height - 1 or x == 0 or x == self.maze_width - 1:
                    self.Maze[y][x].status = 0  # Wall
                else:
                    self.Maze[y][x].status = 1  # Path
        self.__divide(1, 1, self.maze_width - 2, self.maze_height - 2)

    def __divide(self, x: int, y: int, width: int, height: int):
        """Recursively divide area into smaller sections"""
        if width < 2 or height < 2:
            return

        horizontal = random.choice([True, False])

        if horizontal and height >= 3:
            wall_y = y + random.randrange(1, height, 2)

            for wx in range(x, x + width):
                self.Maze[wall_y][wx].status = 0
                if self.animated_generation:
                    self.generation_steps.append((wx, wall_y, 'build_wall'))

            hole_x = x + random.randrange(0, width)
            if hole_x % 2 == 0:
                hole_x += 1 if hole_x < x + width - 1 else -1
            self.Maze[wall_y][hole_x].status = 1
            
            if self.animated_generation:
                self.generation_steps.append((hole_x, wall_y, 'break_wall'))

            self.__divide(x, y, width, wall_y - y)
            self.__divide(x, wall_y + 1, width, height - (wall_y - y + 1))

        elif width >= 3:
            wall_x = x + random.randrange(1, width, 2)

            for wy in range(y, y + height):
                self.Maze[wy][wall_x].status = 0
                if self.animated_generation:
                    self.generation_steps.append((wall_x, wy, 'build_wall'))

            hole_y = y + random.randrange(0, height)
            if hole_y % 2 == 0:
                hole_y += 1 if hole_y < y + height - 1 else -1
            self.Maze[hole_y][wall_x].status = 1
            
            if self.animated_generation:
                self.generation_steps.append((wall_x, hole_y, 'break_wall'))

            self.__divide(x, y, wall_x - x, height)
            self.__divide(wall_x + 1, y, width - (wall_x - x + 1), height)

    def __set_start_end(self):
        """Set start and end positions in the maze"""
        # Find first path cell as start
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.Maze[y][x].status == 1:
                    self.start_pos = (x, y)
                    self.Maze[y][x].status = 2  # Start
                    break
            if self.start_pos:
                break

        # Find last path cell as end
        for y in range(self.maze_height - 1, -1, -1):
            for x in range(self.maze_width - 1, -1, -1):
                if self.Maze[y][x].status == 1:
                    self.end_pos = (x, y)
                    self.Maze[y][x].status = 3  # End
                    break
            if self.end_pos:
                break

    def init_maze_reset(self):
        """Backup current maze state"""
        self.Maze_Backup = self.Maze

    def reset_maze(self):
        """Reset maze to backup state"""
        self.Maze = self.Maze_Backup
        self.generation_complete = False
        self.start_pos = None
        self.end_pos = None
        self.generation_steps = []
        self.current_step = 0

    def apply_next_step(self) -> bool:
        """
        Apply next generation step for animation
        Returns True if there are more steps, False if done
        """
        if self.current_step >= len(self.generation_steps):
            return False
        
        x, y, action = self.generation_steps[self.current_step]
        
        if action == 'path':
            self.Maze[y][x].status = 1
        elif action == 'break_wall':
            self.Maze[y][x].status = 1
        elif action == 'build_wall':
            self.Maze[y][x].status = 0
        
        self.current_step += 1
        return self.current_step < len(self.generation_steps)

    def generate_maze(self):
        """Generate maze using selected algorithm"""
        # Nếu đang ở chế độ animation, tạo một temporary maze để thu thập steps
        if self.animated_generation:
            # Backup maze hiện tại
            original_maze = self.Maze
            
            # Tạo temporary maze để chạy thuật toán
            self.Maze = [[Node_Cell(x, y, 0, False, float('inf'), float('inf')) 
                         for x in range(self.maze_width)] 
                         for y in range(self.maze_height)]
        
        # Chạy thuật toán để thu thập steps
        if self.Algorithm == "DFS":
            self.DFS()
        elif self.Algorithm == "Kruskal":
            self.Kruskal()
        elif self.Algorithm == "Binary_Tree":
            self.Binary_Tree()
        elif self.Algorithm == "Wilson":
            self.Wilson()
        elif self.Algorithm == "Recursive_Division":
            self.Recursive_Division()

        # Nếu đang ở chế độ animation, restore maze ban đầu
        if self.animated_generation:
            # Khởi tạo lại maze về trạng thái ban đầu
            self.Maze = [[Node_Cell(x, y, 0, False, float('inf'), float('inf')) 
                         for x in range(self.maze_width)] 
                         for y in range(self.maze_height)]
            
            # Set viền ngoài là tường
            for y in range(self.maze_height):
                for x in range(self.maze_width):
                    if y == 0 or y == self.maze_height - 1 or x == 0 or x == self.maze_width - 1:
                        self.Maze[y][x].status = 0
                    else:
                        # Nếu là Recursive Division thì bắt đầu với path
                        if self.Algorithm == "Recursive_Division":
                            self.Maze[y][x].status = 1
                        else:
                            self.Maze[y][x].status = 0
            
            # Reset current step
            self.current_step = 0
        else:
            # Chế độ bình thường - set start/end
            self.init_maze_reset()
            self.__set_start_end()
            self.generation_complete = True
        
        return self.Maze
