"""
Quick Test Script
Test the refactored code structure
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model():
    """Test Model package"""
    print("🧪 Testing Model...")
    from Model import GenerationModel, SolvingModel, Node_Cell
    
    # Test Node_Cell
    cell = Node_Cell(0, 0, 1, False, 0, 0)
    assert cell.get_position() == (0, 0)
    print("  ✓ Node_Cell works")
    
    # Test GenerationModel
    generator = GenerationModel(11, 11, "DFS")
    maze = generator.generate_maze()
    assert generator.generation_complete
    print(f"  ✓ GenerationModel works (generated {len(maze)}x{len(maze[0])} maze)")
    
    # Test SolvingModel
    solver = SolvingModel(maze, 11, 11)
    solver.start_pos = generator.start_pos
    solver.end_pos = generator.end_pos
    result = solver.solve_maze("BFS")
    print(f"  ✓ SolvingModel works (found path: {result}, length: {solver.path_length})")
    
    print("✅ Model tests passed!\n")

def test_config():
    """Test config module"""
    print("🧪 Testing config...")
    from config import GAME_TITLE, FPS, PALETTES, CELL_STATUS
    
    assert GAME_TITLE == "Monkey's Treasure"
    assert FPS == 60
    assert 'neutral' in PALETTES
    assert 'WALL' in CELL_STATUS
    print("  ✓ All config values accessible")
    print("✅ Config tests passed!\n")

def test_view_utils():
    """Test View utils"""
    print("🧪 Testing View.utils...")
    from View.utils import calculate_button_size, get_asset_path
    
    # Test calculate_button_size
    size = calculate_button_size(None, target_width=100)
    assert size == (100, 40)
    print("  ✓ calculate_button_size works")
    
    # Test get_asset_path
    path = get_asset_path("test.png")
    assert "assets" in path
    print("  ✓ get_asset_path works")
    
    print("✅ View.utils tests passed!\n")

def test_view_components():
    """Test View components"""
    print("🧪 Testing View.components...")
    from View.components import Button
    
    # Test Button import
    assert Button is not None
    print("  ✓ Button component imported")
    
    print("✅ View.components tests passed!\n")

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 Testing Refactored Code Structure")
    print("=" * 50 + "\n")
    
    try:
        test_config()
        test_model()
        test_view_utils()
        test_view_components()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print("\n✨ The refactored code structure is working correctly!")
        print("📚 See REFACTORING_GUIDE.md for documentation")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
