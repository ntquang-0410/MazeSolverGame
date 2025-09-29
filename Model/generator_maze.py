import random
from View import Node_Cell
from View import Alert_View


def BFS(self, start, goal):
    queue = [(start, [start])]
    visited = set()
    while queue:
        (vertex, path) = queue.pop(0)
        if vertex in visited:
            continue

        for next in self.get_neighbors(vertex):
            if next == goal:
                return path + [next]
            else:
                queue.append((next, path + [next]))

        visited.add(vertex)
    return None

def DFS(self, start, goal):
    stack = [(start, [start])]
    visited = set()
    while stack:
        (vertex, path) = stack.pop()
        if vertex in visited:
            continue

        for next in self.get_neighbors(vertex):
            if next == goal:
                return path + [next]
            else:
                stack.append((next, path + [next]))

        visited.add(vertex)
    return None

def A_star(self, start, goal):
    open_set = set([start])
    closed_set = set()
    g = {}
    parents = {}
    g[start] = 0
    parents[start] = start

    while len(open_set) > 0:
        n = None

        for v in open_set:
            if n is None or g[v] + self.heuristic(v, goal) < g[n] + self.heuristic(n, goal):
                n = v

        if n == goal or self.get_neighbors(n) == []:
            pass
        else:
            for (m, weight) in self.get_neighbors(n).items():
                if m not in open_set and m not in closed_set:
                    open_set.add(m)
                    parents[m] = n
                    g[m] = g[n] + weight
                else:
                    if g[m] > g[n] + weight:
                        g[m] = g[n] + weight
                        parents[m] = n

                        if m in closed_set:
                            closed_set.remove(m)
                            open_set.add(m)

        if n is None:
            print('Path does not exist!')
            return None

        if n == goal:
            reconst_path = []

            while parents[n] != n:
                reconst_path.append(n)
                n = parents[n]

            reconst_path.append(start)
            reconst_path.reverse()

            return reconst_path

        open_set.remove(n)
        closed_set.add(n)

    print('Path does not exist!')
    return None

def heuristic(self, a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def get_neighbors(self, node):
    neighbors = []
    (x, y) = node
    if x > 0 and self.maze[y][x - 1] == 0:
        neighbors.append((x - 1, y))
    if x < self.width - 1 and self.maze[y][x + 1] == 0:
        neighbors.append((x + 1, y))
    if y > 0 and self.maze[y - 1][x] == 0:
        neighbors.append((x, y - 1))
    if y < self.height - 1 and self.maze[y + 1][x] == 0:
        neighbors.append((x, y + 1))
    return neighbors

def generate_maze(self):
    self.maze = [[1 for _ in range(self.width)] for _ in range(self.height)]
    start_x = random.randint(0, self.width // 2) * 2
    start_y = random.randint(0, self.height // 2) * 2
    self.maze[start_y][start_x] = 0
    walls = [(start_x + dx, start_y + dy) for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= start_x + dx < self.width and 0 <= start_y + dy < self.height]
    while walls:
        (wx, wy) = walls.pop(random.randint(0, len(walls) - 1))
        if self.maze[wy][wx] == 1:
            neighbors = [(wx + dx, wy + dy) for (dx, dy) in [(-2, 0), (2, 0), (0, -2), (0, 2)] if 0 <= wx + dx < self.width and 0 <= wy + dy < self.height and self.maze[wy + dy][wx + dx] == 0]
            if len(neighbors) == 1:
                (nx, ny) = neighbors[0]
                self.maze[wy][wx] = 0
                self.maze[(wy + ny) // 2][(wx + nx) // 2] = 0
                new_walls = [(wx + dx, wy + dy) for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= wx + dx < self.width and 0 <= wy + dy < self.height and self.maze[wy + dy][wx + dx] == 1]
                walls.extend(new_walls)
    return self.maze
