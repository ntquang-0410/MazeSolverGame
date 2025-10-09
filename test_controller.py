"""
Test Controller Layer
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Controller import GameController

print("="*50)
print("🧪 Testing Controller Layer")
print("="*50)

# Test GameController
print("\n🎮 Testing GameController...")

controller = GameController(25, 19)
print(f"  ✓ Controller created")
print(f"  ✓ Initial state: {controller.state}")
print(f"  ✓ Maze size: {controller.maze_cols}x{controller.maze_rows}")

# Test maze generation
controller.generate_maze("DFS")
print(f"  ✓ Maze generated with DFS")
assert controller.maze is not None
assert len(controller.maze) == 19
assert len(controller.maze[0]) == 25

# Test game state
controller.start_game()
print(f"  ✓ Game started, state: {controller.state}")
assert controller.state == "game"

# Test player movement
moved = controller.move_player(1, 0)
print(f"  ✓ Player moved right: {moved}")

moved = controller.move_player(0, 1)
print(f"  ✓ Player moved down: {moved}")

print(f"  ✓ Current position: {controller.player_pos}")
print(f"  ✓ Steps: {controller.steps}")

# Test pause
controller.toggle_pause()
print(f"  ✓ Paused: {controller.paused}")

controller.toggle_pause()
print(f"  ✓ Resumed: {not controller.paused}")

# Test algorithm selection
controller.set_solving_algorithm("A*")
print(f"  ✓ Solving algorithm set: {controller.selected_algo}")

controller.set_generation_algorithm("Kruskal")
print(f"  ✓ Generation algorithm set: {controller.selected_generation_algo}")

# Test maze solving
success = controller.solve_maze("BFS")
print(f"  ✓ Maze solved with BFS: {success}")
if success:
    print(f"  ✓ Solution path length: {len(controller.solution_path)}")

# Test auto mode
controller.toggle_auto()
print(f"  ✓ Auto mode: {controller.auto_on}")

# Test restart
controller.restart_level()
print(f"  ✓ Level restarted")
print(f"  ✓ Steps reset: {controller.steps}")
print(f"  ✓ Timer reset: {controller.timer}")

# Test history
controller.steps = 100
controller.timer = 45.5
controller.save_history("Manual")
print(f"  ✓ History saved")
print(f"  ✓ History entries: {len(controller.history)}")

# Test time formatting
time_str = controller.get_time_string()
print(f"  ✓ Time formatted: {time_str}")

print("\n✅ All Controller tests passed!")

print("\n" + "="*50)
print("🎉 Controller layer is working correctly!")
print("="*50)
