#!/usr/bin/env python3
"""
Performance testing tool for the maze game GUI
Measures FPS, memory usage, and render times
"""

import pygame
import psutil
import time
import os
import sys

# Add the View directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'View'))

class PerformanceMonitor:
    def __init__(self):
        self.fps_samples = []
        self.memory_samples = []
        self.render_times = []
        self.start_time = time.time()
        self.process = psutil.Process()

    def update(self, clock, render_start_time):
        # FPS measurement
        fps = clock.get_fps()
        if fps > 0:  # Avoid division by zero on first frame
            self.fps_samples.append(fps)

        # Memory usage
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.memory_samples.append(memory_mb)

        # Render time
        render_time = time.time() - render_start_time
        self.render_times.append(render_time * 1000)  # Convert to ms

    def get_stats(self):
        if not self.fps_samples:
            return "No data collected yet"

        avg_fps = sum(self.fps_samples) / len(self.fps_samples)
        min_fps = min(self.fps_samples)
        max_fps = max(self.fps_samples)

        avg_memory = sum(self.memory_samples) / len(self.memory_samples)
        max_memory = max(self.memory_samples)

        avg_render_time = sum(self.render_times) / len(self.render_times)
        max_render_time = max(self.render_times)

        total_time = time.time() - self.start_time

        return f"""
PERFORMANCE STATS (after {total_time:.1f}s):
=========================================
FPS:
  Average: {avg_fps:.1f}
  Min: {min_fps:.1f}
  Max: {max_fps:.1f}
  
Memory Usage:
  Average: {avg_memory:.1f} MB
  Peak: {max_memory:.1f} MB
  
Render Time:
  Average: {avg_render_time:.2f} ms
  Max: {max_render_time:.2f} ms
  
Frame Consistency:
  Samples: {len(self.fps_samples)}
  Stable 60fps: {sum(1 for fps in self.fps_samples if fps >= 58)}/{len(self.fps_samples)} ({sum(1 for fps in self.fps_samples if fps >= 58)/len(self.fps_samples)*100:.1f}%)
"""

def test_performance():
    """Run performance test"""
    pygame.init()

    # Import after pygame init
    from main import App

    print("Starting performance test...")
    print("Press ESC or close window to stop and see results")

    # Create app with performance monitoring
    app = App()
    monitor = PerformanceMonitor()

    # Override the main loop to add performance monitoring
    while app.running:
        render_start = time.time()

        dt = app.clock.tick(60) / 1000.0
        app.handle_events()
        app.update(dt)

        if app.state == "start":
            app.draw_start()
        else:
            app.draw_game()

        pygame.display.flip()

        # Performance monitoring
        monitor.update(app.clock, render_start)

        # Check for ESC key to exit early
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            break

        # Auto-stop after 30 seconds for automated testing
        if time.time() - monitor.start_time > 30:
            print("\nAuto-stopping after 30 seconds...")
            break

    pygame.quit()

    # Print results
    print(monitor.get_stats())

    # Performance evaluation
    avg_fps = sum(monitor.fps_samples) / len(monitor.fps_samples) if monitor.fps_samples else 0
    stable_fps_ratio = sum(1 for fps in monitor.fps_samples if fps >= 58) / len(monitor.fps_samples) if monitor.fps_samples else 0
    avg_memory = sum(monitor.memory_samples) / len(monitor.memory_samples) if monitor.memory_samples else 0

    print("\nPERFORMANCE EVALUATION:")
    print("=" * 40)

    if avg_fps >= 55:
        print("✅ FPS: EXCELLENT (>55 avg)")
    elif avg_fps >= 45:
        print("⚠️  FPS: GOOD (45-55 avg)")
    else:
        print("❌ FPS: POOR (<45 avg)")

    if stable_fps_ratio >= 0.9:
        print("✅ Frame Stability: EXCELLENT (>90% stable)")
    elif stable_fps_ratio >= 0.7:
        print("⚠️  Frame Stability: GOOD (70-90% stable)")
    else:
        print("❌ Frame Stability: POOR (<70% stable)")

    if avg_memory < 100:
        print("✅ Memory Usage: EXCELLENT (<100MB)")
    elif avg_memory < 200:
        print("⚠️  Memory Usage: GOOD (100-200MB)")
    else:
        print("❌ Memory Usage: HIGH (>200MB)")

if __name__ == "__main__":
    test_performance()
