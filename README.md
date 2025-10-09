# 🎮 Monkey's Treasure - Maze Solver Game

Trò chơi giải mê cung với AI sử dụng các thuật toán tìm kiếm thông minh.

## 📋 Mục lục
- [Tính năng](#-tính-năng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cài đặt](#-cài-đặt)
- [Sử dụng](#-sử-dụng)
- [Refactoring](#-refactoring)

## ✨ Tính năng

### 🏗️ Thuật toán sinh mê cung
- **DFS** (Depth-First Search) - Sinh mê cung theo chiều sâu
- **Kruskal** - Sử dụng Union-Find
- **Binary Tree** - Mê cung có cấu trúc cây
- **Wilson** - Random walk algorithm
- **Recursive Division** - Chia đệ quy

### 🎯 Thuật toán giải mê cung
- **BFS** (Breadth-First Search) - Tìm đường đi ngắn nhất
- **DFS** (Depth-First Search) - Tìm đường đi
- **UCS** (Uniform Cost Search) - Chi phí đồng nhất
- **A*** (A-Star) - Tối ưu với heuristic
- **Bidirectional Search** - Tìm từ 2 đầu

### 🎨 Giao diện
- Thiết kế hiện đại với glassmorphism
- Animation mượt mà
- Responsive UI
- Performance optimization

## 📁 Cấu trúc dự án

```
MazeSolverGame/
├── main.py                 # Entry point
├── config.py              # Configuration
├── test_refactoring.py    # Test suite
├── REFACTORING_GUIDE.md   # Chi tiết refactoring
│
├── Model/                 # Data & Logic
│   ├── node_cell.py      # Cell class
│   ├── maze_generator.py # Generation algorithms
│   └── maze_solver.py    # Solving algorithms
│
├── View/                  # UI & Display
│   ├── __init__.py       # Main App
│   ├── utils.py          # Utilities
│   ├── components/       # UI components
│   ├── sprites/          # Game sprites
│   └── assets/           # Images, fonts
│
└── Controller/            # Game logic (TODO)
```

## 🔧 Cài đặt

### Yêu cầu
- Python 3.9+
- Pygame 2.0+

### Cài đặt dependencies
```bash
pip install pygame
```

### Clone repository
```bash
git clone https://github.com/ntquang-0410/MazeSolverGame.git
cd MazeSolverGame
```

## 🚀 Sử dụng

### Chạy game
```bash
python main.py
```

### Chạy tests
```bash
python test_refactoring.py
```

### Sử dụng như thư viện

```python
from Model import GenerationModel, SolvingModel

# Generate maze
generator = GenerationModel(25, 19, "DFS")
maze = generator.generate_maze()

# Solve maze
solver = SolvingModel(maze, 25, 19)
solver.start_pos = generator.start_pos
solver.end_pos = generator.end_pos
found = solver.solve_maze("A*")

print(f"Path found: {found}")
print(f"Path length: {solver.path_length}")
print(f"Time: {solver.solving_time:.3f}s")
print(f"Nodes expanded: {solver.nodes_expanded}")
```

## 🔄 Refactoring

Dự án đã được tổ chức lại theo mô hình **MVC (Model-View-Controller)**.

### ✅ Hoàn thành
- ✅ Tách Model thành các file riêng
- ✅ Tạo config.py cho constants
- ✅ Tách View utilities
- ✅ Tạo Button component
- ✅ Cấu trúc thư mục rõ ràng
- ✅ Test suite đầy đủ
- ✅ Documentation chi tiết

### 📝 TODO
- Tách các components còn lại (Dropdown, Modals)
- Tách sprites (Monkey, Banana)
- Xây dựng Controller layer
- Cập nhật View/__init__.py

Chi tiết xem [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)

## 📊 Performance

### Thời gian giải mê cung (25x19)
- BFS: ~0.010s
- DFS: ~0.008s
- UCS: ~0.012s
- A*: ~0.007s (nhanh nhất)
- Bidirectional: ~0.009s

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Git Commits

### Recent commits
```bash
git log --oneline -5
```

```
4901ee9 test: Add comprehensive test suite for refactored code
a4301c3 docs: Add refactoring guide and package init files
4e52ddc Refactor: Reorganize code structure following MVC pattern
95f9180 Save current changes before merge
...
```

## 📜 License

Dự án học tập - AI Course Project

## 👥 Team

- **Repository**: [ntquang-0410/MazeSolverGame](https://github.com/ntquang-0410/MazeSolverGame)
- **Branch**: view_01
- **Refactored**: October 2025

## 📚 References

- [Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Pathfinding Algorithms](https://en.wikipedia.org/wiki/Pathfinding)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model–view–controller)
- [Pygame Documentation](https://www.pygame.org/docs/)

---

**Note**: Đây là phiên bản đã được refactor. Code cũ được backup trong các file `.backup`.
