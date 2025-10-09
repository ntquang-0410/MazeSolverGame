# 📚 Hướng Dẫn Cấu Trúc Code Mới - MazeSolverGame

## 🎯 Tổng quan
Dự án đã được tổ chức lại theo mô hình **MVC (Model-View-Controller)** chuẩn để dễ quản lý, bảo trì và mở rộng.

## 📁 Cấu trúc thư mục mới

```
MazeSolverGame/
├── main.py                      # Entry point của ứng dụng
├── config.py                    # ⭐ Constants và settings tập trung
│
├── Model/                       # 📊 Lớp Model - Logic dữ liệu
│   ├── __init__.py             # Exports: Node_Cell, GenerationModel, SolvingModel
│   ├── node_cell.py            # ⭐ Class Node_Cell (ô trong mê cung)
│   ├── maze_generator.py       # ⭐ Class GenerationModel (sinh mê cung)
│   └── maze_solver.py          # ⭐ Class SolvingModel (giải mê cung)
│
├── View/                        # 🎨 Lớp View - Giao diện
│   ├── __init__.py             # Main App class và exports
│   ├── utils.py                # ⭐ Utility functions (draw, load_image...)
│   │
│   ├── components/             # 📦 UI Components
│   │   ├── __init__.py
│   │   ├── button.py           # ⭐ Button component
│   │   ├── dropdown.py         # TODO: Dropdown component
│   │   └── modals.py           # TODO: Modal dialogs
│   │
│   ├── sprites/                # 🎮 Game Sprites
│   │   ├── __init__.py
│   │   ├── monkey.py           # TODO: Monkey sprite
│   │   └── banana.py           # TODO: Banana sprite
│   │
│   └── assets/                 # 🖼️ Tài nguyên (images, fonts...)
│       ├── button/
│       ├── tiles/
│       └── ...
│
└── Controller/                  # 🎮 Lớp Controller - Logic điều khiển
    ├── __init__.py             # TODO: Exports
    ├── game_controller.py      # TODO: Game logic controller
    └── maze_controller.py      # TODO: Maze interaction controller
```

## ✅ Đã hoàn thành

### 1. **config.py** - Quản lý cấu hình tập trung
```python
from config import GAME_TITLE, FPS, MAZE_COLS, MAZE_ROWS
from config import PALETTES, CELL_STATUS
```

**Lợi ích:**
- Dễ thay đổi settings
- Tránh hardcode
- Dễ tìm kiếm giá trị cấu hình

### 2. **Model** - Đã tách thành 3 file riêng biệt

#### `Model/node_cell.py`
```python
from Model import Node_Cell

cell = Node_Cell(x, y, status, visited, g_cost, h_cost)
```

#### `Model/maze_generator.py`
```python
from Model import GenerationModel

generator = GenerationModel(width, height, "DFS")
maze = generator.generate_maze()
```

**Thuật toán hỗ trợ:**
- DFS (Depth-First Search)
- Kruskal's Algorithm
- Binary Tree
- Wilson's Algorithm
- Recursive Division

#### `Model/maze_solver.py`
```python
from Model import SolvingModel

solver = SolvingModel(maze_grid, width, height)
solver.solve_maze("A*")
```

**Thuật toán hỗ trợ:**
- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- UCS (Uniform Cost Search)
- A* (A-Star)
- Bidirectional Search

### 3. **View/utils.py** - Utility functions
```python
from View.utils import load_image, draw_shadow, draw_glass_card
from View.utils import calculate_button_size

image = load_image("path/to/image.png")
draw_shadow(surface, rect)
```

**Functions:**
- `load_image()` - Load ảnh với error handling
- `draw_shadow()` - Vẽ bóng đổ
- `draw_glass_card()` - Vẽ card glassmorphism
- `draw_smooth_rect()` - Vẽ hình chữ nhật mượt
- `try_load_font()` - Load font
- `calculate_button_size()` - Tính kích thước button

### 4. **View/components/button.py** - Button component
```python
from View.components.button import Button

button = Button(
    rect=(x, y, width, height),
    text="Click Me",
    font=my_font,
    on_click=callback_function,
    theme='green',
    bg_image=button_image
)

button.draw(surface)
button.handle_event(event)
```

**Features:**
- Hỗ trợ image background
- Hover effects
- Themes (neutral, green, yellow, orange, blue, purple, red)
- Aspect ratio preservation
- Click callbacks

## 📝 TODO - Cần hoàn thành

### 1. **View/components/dropdown.py**
- Tách Dropdown class từ View/__init__.py
- Component chọn thuật toán, độ khó

### 2. **View/components/modals.py**
- ModalHistory - Lịch sử chơi
- ModalVictory - Màn hình thắng

### 3. **View/sprites/monkey.py**
- MonkeyIdle class - Animation khỉ
- Sprite cho nhân vật

### 4. **View/sprites/banana.py**
- FloatingBanana class - Animation chuối
- Floating effect

### 5. **Controller/game_controller.py**
- Game state management
- Event handling
- Game loop coordination

### 6. **Controller/maze_controller.py**
- Maze generation control
- Maze solving control
- Player movement

### 7. **View/__init__.py refactoring**
- Import từ các module mới
- Giữ lại App class
- Xóa code đã tách ra

## 🔧 Cách sử dụng

### Import mới
```python
# Thay vì:
# from Model.__init__ import GenerationModel

# Dùng:
from Model import GenerationModel, SolvingModel, Node_Cell
from config import GAME_TITLE, FPS, PALETTES
from View.utils import load_image, draw_shadow
from View.components.button import Button
```

### Tạo maze
```python
# Generate maze
generator = GenerationModel(25, 19, "DFS")
maze = generator.generate_maze()

# Solve maze
solver = SolvingModel(maze, 25, 19)
solver.solve_maze("A*")

print(f"Path found: {solver.solution_found}")
print(f"Path length: {solver.path_length}")
print(f"Time: {solver.solving_time:.3f}s")
```

## 🎨 Code Style Guidelines

### Naming Conventions
- **Classes**: PascalCase (`GenerationModel`, `ButtonComponent`)
- **Functions**: snake_case (`load_image`, `draw_shadow`)
- **Constants**: UPPER_SNAKE_CASE (`GAME_TITLE`, `FPS`)
- **Variables**: snake_case (`maze_width`, `cell_size`)

### File Organization
- Mỗi class lớn nên có file riêng
- Utility functions nhóm theo chức năng
- Comments bằng tiếng Việt hoặc tiếng Anh đều được

### Import Order
1. Standard library imports
2. Third-party imports (pygame, etc.)
3. Local application imports

```python
import os
import sys
from typing import List, Tuple

import pygame

from config import GAME_TITLE
from Model import GenerationModel
from View.utils import load_image
```

## 🚀 Lợi ích của cấu trúc mới

### ✅ Dễ quản lý
- Code ngắn hơn, rõ ràng hơn
- Mỗi file có trách nhiệm riêng
- Dễ tìm kiếm và sửa lỗi

### ✅ Dễ làm việc nhóm
- Nhiều người có thể làm việc song song
- Ít conflict khi merge code
- Dễ review code

### ✅ Dễ mở rộng
- Thêm thuật toán mới: chỉ cần sửa 1 file
- Thêm UI component: tạo file mới trong components/
- Thêm sprite: tạo file mới trong sprites/

### ✅ Dễ test
- Test từng module riêng biệt
- Mock dependencies dễ dàng
- Unit test rõ ràng

### ✅ Reusable
- Components có thể dùng lại
- Utils functions dùng cho nhiều nơi
- Model tách biệt khỏi View

## 📚 Tài liệu tham khảo

- **MVC Pattern**: https://en.wikipedia.org/wiki/Model–view–controller
- **Python Project Structure**: https://docs.python-guide.org/writing/structure/
- **Pygame Documentation**: https://www.pygame.org/docs/

## 👥 Contributors

- Refactoring by: GitHub Copilot
- Original code: MazeSolverGame Team

---

**Ghi chú**: Đây là bước đầu tiên trong việc tổ chức lại code. Các bước tiếp theo sẽ hoàn thiện việc tách các components còn lại và xây dựng Controller layer.
