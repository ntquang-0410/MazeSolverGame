"""
Maze Solving Algorithms
Contains SolvingModel class with various pathfinding algorithms:
- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- UCS (Uniform Cost Search)
- A* (A-Star Search)
- Bidirectional Search
"""
import time
import heapq
from collections import deque
from typing import List, Tuple, Optional, Dict
from Model.node_cell import Node_Cell


class SolvingModel:
    """Model for solving mazes using various pathfinding algorithms"""
    
    def __init__(self, maze_grid: List[List[Node_Cell]], maze_width: int, maze_height: int):
        # Maze data
        self.maze_grid = maze_grid
        self.maze_width = maze_width
        self.maze_height = maze_height

        # Algorithm and results
        self.algorithm = None
        self.solution_path: List[Tuple[int, int]] = []
        self.visited_cells: List[Tuple[int, int]] = []

        # Solving state
        self.solving_complete = False
        self.solution_found = False

        # Start/End positions
        self.start_pos: Optional[Tuple[int, int]] = (1, 1)
        self.end_pos: Optional[Tuple[int, int]] = (maze_width - 2, maze_height - 2)

        # Metrics
        self.steps_taken = 0
        self.path_length = 0
        self.nodes_expanded = 0
        self.solving_time = 0.0

    def reset_solving_state(self):
        """Reset state for re-solving"""
        self.solution_path.clear()
        self.visited_cells.clear()
        self.solving_complete = False
        self.solution_found = False
        self.steps_taken = 0
        self.path_length = 0
        self.nodes_expanded = 0
        self.solving_time = 0.0

        # Reset visual state
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.maze_grid[y][x].status in [4, 5]:  # Path Found, Moved Path
                    if (x, y) == self.start_pos:
                        self.maze_grid[y][x].status = 2  # Start
                    elif (x, y) == self.end_pos:
                        self.maze_grid[y][x].status = 3  # End
                    else:
                        self.maze_grid[y][x].status = 1  # Path

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring cells (not walls)"""
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.maze_width and 
                0 <= ny < self.maze_height and 
                self.maze_grid[ny][nx].status != 0):
                neighbors.append((nx, ny))

        return neighbors

    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Heuristic function for A* (Manhattan distance)"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def reconstruct_path(self, came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary"""
        path = []
        current = self.end_pos

        while current is not None:
            path.append(current)
            current = came_from.get(current)

        path.reverse()
        return path

    def BFS(self) -> bool:
        """Breadth-First Search - Find shortest path"""
        if not self.start_pos or not self.end_pos:
            return False

        queue = deque([self.start_pos])
        visited = {self.start_pos}
        came_from = {self.start_pos: None}

        while queue:
            current = queue.popleft()
            self.nodes_expanded += 1

            if current == self.end_pos:
                self.solution_path = self.reconstruct_path(came_from)
                self.path_length = len(self.solution_path)
                return True

            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5

                    self.visited_cells.append(neighbor)

        return False

    def DFS(self) -> bool:
        """Depth-First Search - Find a path (not necessarily shortest)"""
        if not self.start_pos or not self.end_pos:
            return False

        stack = [self.start_pos]
        visited = {self.start_pos}
        came_from = {self.start_pos: None}

        while stack:
            current = stack.pop()
            self.nodes_expanded += 1

            if current == self.end_pos:
                self.solution_path = self.reconstruct_path(came_from)
                self.path_length = len(self.solution_path)
                return True

            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    stack.append(neighbor)

                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5

                    self.visited_cells.append(neighbor)

        return False

    def UCS(self) -> bool:
        """Uniform Cost Search - Find path with lowest cost"""
        if not self.start_pos or not self.end_pos:
            return False

        heap = [(0, self.start_pos)]
        visited = set()
        came_from = {self.start_pos: None}
        cost_so_far = {self.start_pos: 0}

        while heap:
            current_cost, current = heapq.heappop(heap)

            if current in visited:
                continue

            visited.add(current)
            self.nodes_expanded += 1

            if current == self.end_pos:
                self.solution_path = self.reconstruct_path(came_from)
                self.path_length = len(self.solution_path)
                return True

            for neighbor in self.get_neighbors(current[0], current[1]):
                new_cost = current_cost + 1

                if neighbor not in visited and (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]):
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    heapq.heappush(heap, (new_cost, neighbor))

                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5

                    self.visited_cells.append(neighbor)

        return False

    def A_star(self) -> bool:
        """A* Search - Find optimal path with heuristic"""
        if not self.start_pos or not self.end_pos:
            return False

        heap = [(0, 0, self.start_pos)]
        visited = set()
        came_from = {self.start_pos: None}
        g_score = {self.start_pos: 0}

        while heap:
            f_score, g_score_current, current = heapq.heappop(heap)

            if current in visited:
                continue

            visited.add(current)
            self.nodes_expanded += 1

            if current == self.end_pos:
                self.solution_path = self.reconstruct_path(came_from)
                self.path_length = len(self.solution_path)
                return True

            for neighbor in self.get_neighbors(current[0], current[1]):
                tentative_g_score = g_score_current + 1

                if neighbor not in visited and (neighbor not in g_score or tentative_g_score < g_score[neighbor]):
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor, self.end_pos)
                    came_from[neighbor] = current
                    heapq.heappush(heap, (f_score, tentative_g_score, neighbor))

                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5

                    self.visited_cells.append(neighbor)

        return False

    def Bidirectional_Search(self) -> bool:
        """Bidirectional Search - Search from both ends"""
        if not self.start_pos or not self.end_pos:
            return False

        # Initialize search from start
        queue_start = deque([self.start_pos])
        visited_start = {self.start_pos}
        came_from_start = {self.start_pos: None}

        # Initialize search from end
        queue_end = deque([self.end_pos])
        visited_end = {self.end_pos}
        came_from_end = {self.end_pos: None}

        while queue_start or queue_end:
            # Search from start
            if queue_start:
                current_start = queue_start.popleft()
                self.nodes_expanded += 1

                if current_start in visited_end:
                    # Reconstruct path
                    path_start = []
                    node = current_start
                    while node is not None:
                        path_start.append(node)
                        node = came_from_start.get(node)
                    path_start.reverse()

                    path_end = []
                    node = came_from_end[current_start]
                    while node is not None:
                        path_end.append(node)
                        node = came_from_end.get(node)

                    self.solution_path = path_start + path_end
                    self.path_length = len(self.solution_path)
                    return True

                for neighbor in self.get_neighbors(current_start[0], current_start[1]):
                    if neighbor not in visited_start:
                        visited_start.add(neighbor)
                        came_from_start[neighbor] = current_start
                        queue_start.append(neighbor)

                        if neighbor not in [self.start_pos, self.end_pos]:
                            self.maze_grid[neighbor[1]][neighbor[0]].status = 5

                        self.visited_cells.append(neighbor)

            # Search from end
            if queue_end:
                current_end = queue_end.popleft()
                self.nodes_expanded += 1

                if current_end in visited_start:
                    # Reconstruct path
                    path_start = []
                    node = current_end
                    while node is not None:
                        path_start.append(node)
                        node = came_from_start.get(node)
                    path_start.reverse()

                    path_end = []
                    node = came_from_end[current_end]
                    while node is not None:
                        path_end.append(node)
                        node = came_from_end.get(node)

                    self.solution_path = path_start + path_end
                    self.path_length = len(self.solution_path)
                    return True

                for neighbor in self.get_neighbors(current_end[0], current_end[1]):
                    if neighbor not in visited_end:
                        visited_end.add(neighbor)
                        came_from_end[neighbor] = current_end
                        queue_end.append(neighbor)

                        if neighbor not in [self.start_pos, self.end_pos]:
                            self.maze_grid[neighbor[1]][neighbor[0]].status = 5

                        self.visited_cells.append(neighbor)

        return False

    def solve_maze(self, algorithm: str) -> bool:
        """Solve maze using selected algorithm"""
        if not self.start_pos or not self.end_pos:
            return False

        self.algorithm = algorithm
        self.reset_solving_state()

        start_time = time.time()

        if algorithm == "BFS":
            self.solution_found = self.BFS()
        elif algorithm == "DFS":
            self.solution_found = self.DFS()
        elif algorithm == "UCS":
            self.solution_found = self.UCS()
        elif algorithm == "A*":
            self.solution_found = self.A_star()
        elif algorithm == "Bidirectional":
            self.solution_found = self.Bidirectional_Search()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        self.solving_time = time.time() - start_time
        self.solving_complete = True

        # Mark found path
        if self.solution_found:
            for pos in self.solution_path:
                if pos not in [self.start_pos, self.end_pos]:
                    self.maze_grid[pos[1]][pos[0]].status = 4  # Path Found

        return self.solution_found
