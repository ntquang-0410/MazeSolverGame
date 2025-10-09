import random
import heapq
import time
from collections import deque
from typing import List, Tuple, Optional, Dict
from Model.node_cell import Node_Cell

# Generation Algorithms: DFS, Kruskal, Binary Tree, Wilson, Recursive Division
# Solving Algorithms: BFS, DFS, UCS, A*, Bidirectional Search
# Các trạng thái của Node_Cell:
# 0: Wall
# 1: Path
# 2: Start
# 3: End
# 4: Path Found
# 5: Moved Path

class GenerationModel:
    def __init__(self, maze_width, height_width, Node_Cell, mode):
        self.maze_width = maze_width
        self.height_width = height_width
        self.mode = mode

        # Khởi tạo lưới với tất cả ô là tường (status = 0)
        self.grid = [[Node_Cell(x, y, 0, False, 0, 0) for x in range(maze_width)] for y in range(height_width)]

        # Thuộc tính bổ sung cho quá trình sinh mê cung
        self.start_pos: Optional[Tuple[int, int]] = (1, 1) # Mặc định vị trí bắt đầu
        self.end_pos: Optional[Tuple[int, int]] = (maze_width - 2, height_width - 2) # Mặc định vị trí kết thúc
        self.generation_complete = False # Cờ để kiểm tra quá trình sinh mê cung đã hoàn thành


    def __get_neighbors(self, x: int, y: int, distance: int = 2) -> List[Tuple[int, int]]:
        """Lấy danh sách ô láng giềng hợp lệ"""
        neighbors = []
        directions = [(0, distance), (0, -distance), (distance, 0), (-distance, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.maze_width and 0 <= ny < self.height_width:
                neighbors.append((nx, ny)) # Sửa lỗi: Thêm láng giềng vào danh sách
        return neighbors

    def DFS(self, start_x: int, start_y: int):
        """Thuật toán Depth-First Search để sinh mê cung"""
        stack = [(start_x, start_y)]
        self.grid[start_y][start_x].status = 1  # Đánh dấu là path

        while stack:
            current_x, current_y = stack[-1]
            neighbors = []

            # Sửa lỗi: truyền đúng tham số distance
            for nx, ny in self.__get_neighbors(current_x, current_y, 2):
                if self.grid[ny][nx].status == 0:
                    neighbors.append(nx, ny)

            if neighbors:
                # Chọn ngẫu nhiên một láng giềng
                next_x, next_y = random.choice(neighbors)

                # Phá tường giữa ô hiện tại và ô láng giềng
                wall_x = (current_x + next_x) // 2
                wall_y = (current_y + next_y) // 2

                self.grid[wall_y][wall_x].status = 1  # Path
                self.grid[next_y][next_x].status = 1  # Path

                stack.append((next_x, next_y))
            else:
                stack.pop()

    def Kruskal(self):
        """Thuật toán Kruskal để sinh mê cung"""
        # Tạo danh sách tất cả các tường có thể phá
        walls = []

        # Khởi tạo các ô lẻ là path
        for y in range(1, self.height_width, 2):
            for x in range(1, self.maze_width, 2):
                self.grid[y][x].status = 1  # Path

                # Thêm tường ngang
                if x + 2 < self.maze_width:
                    walls.append((x, y, x + 2, y))

                # Thêm tường dọc
                if y + 2 < self.height_width:
                    walls.append((x, y, x, y + 2))

        random.shuffle(walls)

        # Union-Find để theo dõi các thành phần liên thông
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

        # Phá tường nếu hai ô chưa kết nối
        for x1, y1, x2, y2 in walls:
            if union((x1, y1), (x2, y2)):
                wall_x = (x1 + x2) // 2
                wall_y = (y1 + y2) // 2
                self.grid[wall_y][wall_x].status = 1  # Path

    def Binary_Tree(self):
        """Thuật toán Binary Tree để sinh mê cung"""
        for y in range(1, self.height_width, 2):
            for x in range(1, self.maze_width, 2):
                self.grid[y][x].status = 1  # Path

                # Chọn ngẫu nhiên hướng: lên hoặc trái
                directions = []
                if y > 1:  # Có thể đi lên
                    directions.append("up")
                if x > 1:  # Có thể đi trái
                    directions.append("left")

                if directions:
                    direction = random.choice(directions)
                    if direction == "up":
                        self.grid[y - 1][x].status = 1  # Path
                    else:  # left
                        self.grid[y][x - 1].status = 1  # Path

    def Wilson(self):
        """Thuật toán Wilson để sinh mê cung"""
        # Tạo danh sách tất cả các ô lẻ
        cells = [(x, y) for y in range(1, self.height_width, 2)
                 for x in range(1, self.maze_width, 2)]

        # Chọn ô đầu tiên làm điểm bắt đầu
        start = random.choice(cells)
        self.grid[start[1]][start[0]].status = 1  # Path
        remaining = [cell for cell in cells if cell != start]

        while remaining:
            # Chọn ô ngẫu nhiên chưa trong mê cung
            current = random.choice(remaining)
            path = [current]

            # Random walk cho đến khi gặp ô đã trong mê cung
            while self.grid[current[1]][current[0]].status != 1:
                neighbors = self.__get_neighbors(current[0], current[1])
                valid_neighbors = [(x, y) for x, y in neighbors
                                   if 1 <= x < self.maze_width - 1 and 1 <= y < self.height_width - 1]

                if valid_neighbors:
                    next_cell = random.choice(valid_neighbors)

                    # Xóa loop nếu có
                    if next_cell in path:
                        path = path[:path.index(next_cell) + 1]
                    else:
                        path.append(next_cell)

                    current = next_cell

            # Thêm đường đi vào mê cung
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]

                self.grid[y1][x1].status = 1  # Path

                # Phá tường giữa hai ô
                wall_x = (x1 + x2) // 2
                wall_y = (y1 + y2) // 2
                self.grid[wall_y][wall_x].status = 1  # Path

            # Cập nhật danh sách ô còn lại
            remaining = [cell for cell in remaining
                         if self.grid[cell[1]][cell[0]].status != 1]

    def Recursive_Division(self):
        """Thuật toán Recursive Division để sinh mê cung"""
        # Bắt đầu với toàn bộ khu vực là đường đi
        for y in range(self.height_width):
            for x in range(self.maze_width):
                if y == 0 or y == self.height_width - 1 or x == 0 or x == self.maze_width - 1:
                    self.grid[y][x].status = 0  # Wall
                else:
                    self.grid[y][x].status = 1  # Path

        self.__divide(1, 1, self.maze_width - 2, self.height_width - 2)

    def __divide(self, x: int, y: int, width: int, height: int):
        """Đệ quy chia khu vực thành các phần nhỏ hơn"""
        if width < 2 or height < 2:
            return

        # Chọn hướng chia
        horizontal = random.choice([True, False])

        if horizontal and height >= 3:
            # Chia ngang
            wall_y = y + random.randrange(1, height, 2)

            # Tạo tường ngang
            for wx in range(x, x + width):
                self.grid[wall_y][wx].status = 0  # Wall

            # Tạo lỗ ngẫu nhiên
            hole_x = x + random.randrange(0, width)
            if hole_x % 2 == 0:
                hole_x += 1 if hole_x < x + width - 1 else -1
            self.grid[wall_y][hole_x].status = 1  # Path

            # Đệ quy chia hai phần
            self.__divide(x, y, width, wall_y - y)
            self.__divide(x, wall_y + 1, width, height - (wall_y - y + 1))

        elif width >= 3:
            # Chia dọc
            wall_x = x + random.randrange(1, width, 2)

            # Tạo tường dọc
            for wy in range(y, y + height):
                self.grid[wy][wall_x].status = 0  # Wall

            # Tạo lỗ ngẫu nhiên
            hole_y = y + random.randrange(0, height)
            if hole_y % 2 == 0:
                hole_y += 1 if hole_y < y + height - 1 else -1
            self.grid[hole_y][wall_x].status = 1  # Path

            # Đệ quy chia hai phần
            self.__divide(x, y, wall_x - x, height)
            self.__divide(wall_x + 1, y, width - (wall_x - x + 1), height)
    def generate_maze(self):
        """Sinh mê cung theo thuật toán đã chọn"""
        if self.mode == "DFS":
            self.DFS(1, 1)  # Thêm tham số bắt buộc
        elif self.mode == "Kruskal":
            self.Kruskal()
        elif self.mode == "Binary_Tree":
            self.Binary_Tree()
        elif self.mode == "Wilson":
            self.Wilson()
        elif self.mode == "Recursive_Division":
            self.Recursive_Division()

        self.__set_start_end()
        self.generation_complete = True

    def __set_start_end(self):
        """Đặt điểm bắt đầu và kết thúc"""
        # Tìm ô đường đi đầu tiên làm điểm bắt đầu
        for y in range(self.height_width):
            for x in range(self.maze_width):
                if self.grid[y][x].status == 1:  # Path
                    self.start_pos = (x, y)
                    self.grid[y][x].status = 2  # Start
                    break
            if self.start_pos:
                break

        # Tìm ô đường đi cuối cùng làm điểm kết thúc
        for y in range(self.height_width-1, -1, -1):
            for x in range(self.maze_width-1, -1, -1):
                if self.grid[y][x].status == 1:  # Path
                    self.end_pos = (x, y)
                    self.grid[y][x].status = 3  # End
                    break
            if self.end_pos:
                break

class SolvingModel:
    def __init__(self, maze_grid: List[List[Node_Cell]], maze_width: int, maze_height: int):
        # Dữ liệu mê cung
        self.maze_grid = maze_grid
        self.maze_width = maze_width
        self.maze_height = maze_height

        # Thuật toán và kết quả
        self.algorithm = None
        self.solution_path: List[Tuple[int, int]] = []
        self.visited_cells: List[Tuple[int, int]] = []

        # Trạng thái giải
        self.solving_complete = False
        self.solution_found = False

        # Vị trí start/end
        self.start_pos: Optional[Tuple[int, int]] = (1, 1) # Mặc định vị trí bắt đầu
        self.end_pos: Optional[Tuple[int, int]] = (maze_width - 2, maze_height - 2) # Mặc định vị trí kết thúc

        # Metrics
        self.steps_taken = 0
        self.path_length = 0
        self.nodes_expanded = 0
        self.solving_time = 0.0

    def reset_solving_state(self):
        """Reset trạng thái để giải lại"""
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
        """Lấy các ô láng giềng hợp lệ (không phải tường)"""
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.maze_width and 0 <= ny < self.maze_height and
                self.maze_grid[ny][nx].status != 0):  # Không phải tường
                neighbors.append((nx, ny))

        return neighbors

    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Hàm heuristic cho A* (Manhattan distance)"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def reconstruct_path(self, came_from: Dict[Tuple[int, int], Tuple[int, int]], current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Tái tạo đường đi từ came_from dictionary"""
        path = []
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        return path

    def BFS(self) -> bool:
        """Breadth-First Search - Tìm đường đi ngắn nhất"""
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

            for neighbor in self.get_neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

                    # Đánh dấu ô đã thăm
                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5  # Moved Path

                    self.visited_cells.append(neighbor)

        return False

    def DFS(self) -> bool:
        """Depth-First Search - Tìm một đường đi (không nhất thiết ngắn nhất)"""
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

            for neighbor in self.get_neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    stack.append(neighbor)

                    # Đánh dấu ô đã thăm
                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5  # Moved Path

                    self.visited_cells.append(neighbor)

        return False

    def UCS(self) -> bool:
        """Uniform Cost Search - Tìm đường đi với chi phí thấp nhất"""
        if not self.start_pos or not self.end_pos:
            return False

        # Priority queue: (cost, position)
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

            for neighbor in self.get_neighbors(*current):
                new_cost = current_cost + 1  # Giả sử mỗi bước có cost = 1

                if neighbor not in visited and (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]):
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    heapq.heappush(heap, (new_cost, neighbor))

                    # Đánh dấu ô đã thăm
                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5  # Moved Path

                    self.visited_cells.append(neighbor)

        return False

    def A_star(self) -> bool:
        """A* Search - Tìm đường đi tối ưu với heuristic"""
        if not self.start_pos or not self.end_pos:
            return False

        # Priority queue: (f_score, g_score, position)
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

            for neighbor in self.get_neighbors(*current):
                tentative_g_score = g_score_current + 1

                if neighbor not in visited and (neighbor not in g_score or tentative_g_score < g_score[neighbor]):
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor, self.end_pos)
                    came_from[neighbor] = current
                    heapq.heappush(heap, (f_score, tentative_g_score, neighbor))

                    # Đánh dấu ô đã thăm
                    if neighbor != self.end_pos:
                        self.maze_grid[neighbor[1]][neighbor[0]].status = 5  # Moved Path

                    self.visited_cells.append(neighbor)

        return False

    def Bidirectional_Search(self) -> bool:
        """Bidirectional Search - Tìm kiếm từ cả hai đầu"""
        if not self.start_pos or not self.end_pos:
            return False

        # Khởi tạo cho tìm kiếm từ start
        queue_start = deque([self.start_pos])
        visited_start = {self.start_pos}
        came_from_start = {self.start_pos: None}

        # Khởi tạo cho tìm kiếm từ end
        queue_end = deque([self.end_pos])
        visited_end = {self.end_pos}
        came_from_end = {self.end_pos: None}

        while queue_start or queue_end:
            # Tìm kiếm từ start
            if queue_start:
                current_start = queue_start.popleft()
                self.nodes_expanded += 1

                # Kiểm tra giao điểm
            # Sửa lỗi logic tái tạo đường đi
                if current_start in visited_end:
                    self.solution_path = self.reconstruct_path(came_from_start, current_start)
                    path_end = self.reconstruct_path(came_from_end, current_start)
                    path_end.reverse()
                    self.solution_path.extend(path_end[1:])
                    self.path_length = len(self.solution_path)
                    return True

                for neighbor in self.get_neighbors(*current_start):
                    if neighbor not in visited_start:
                        visited_start.add(neighbor)
                        came_from_start[neighbor] = current_start
                        queue_start.append(neighbor)

                        if neighbor not in [self.start_pos, self.end_pos]:
                            self.maze_grid[neighbor[1]][neighbor[0]].status = 5  # Moved Path

                        self.visited_cells.append(neighbor)

            # Tìm kiếm từ end
            if queue_end:
                current_end = queue_end.popleft()
                self.nodes_expanded += 1

                # Kiểm tra giao điểm
                if current_end in visited_start:
                    # Tái tạo đường đi
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

                for neighbor in self.get_neighbors(*current_end):
                    if neighbor not in visited_end:
                        visited_end.add(neighbor)
                        came_from_end[neighbor] = current_end
                        queue_end.append(neighbor)

                        if neighbor not in [self.start_pos, self.end_pos]:
                            self.maze_grid[neighbor[1]][neighbor[0]].status = 5  # Moved Path

                        self.visited_cells.append(neighbor)

        return False

    def solve_maze(self, algorithm: str) -> bool:
        """Giải mê cung với thuật toán được chọn"""
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

        # Đánh dấu đường đi tìm được
        if self.solution_found:
            for pos in self.solution_path:
                if pos not in [self.start_pos, self.end_pos]:
                    self.maze_grid[pos[1]][pos[0]].status = 4  # Path Found

        return self.solution_found