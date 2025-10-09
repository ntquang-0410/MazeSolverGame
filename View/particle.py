"""
Simple particle system used for generation / path effects.

Provides a minimal, dependency-free implementation that works with the
existing calls in `View.__init__.py`:

- ParticleSystem()
- clear()
- update(dt)
- draw(surface)
- emit_wall_break(x, y, cell_size)
- emit_path_creation(x, y, cell_size, path_color=None)

The implementation favors readability and small memory usage. Particles
are drawn as soft circles using temporary SRCALPHA surfaces.
"""
import math
import random
import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color")

    def __init__(self, x, y, vx, vy, life, size, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color


class ParticleSystem:
    def __init__(self):
        # list of Particle
        self.particles = []

    def clear(self):
        """Remove all particles."""
        self.particles.clear()

    def update(self, dt: float):
        """Advance simulation by dt seconds."""
        if not self.particles:
            return

        alive = []
        for p in self.particles:
            # simple Euler integration
            p.x += p.vx * dt
            p.y += p.vy * dt

            # gravity-like pull for wall-break effects
            p.vy += 40.0 * dt

            p.life -= dt
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surface: pygame.Surface):
        """Draw all particles onto the provided surface."""
        for p in self.particles:
            alpha = max(0, min(255, int(255 * (p.life / p.max_life))))
            col = (p.color[0], p.color[1], p.color[2], alpha)
            r = max(1, int(p.size))

            # create a temporary surface for alpha circle
            tmp = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(tmp, col, (r, r), r)
            # slightly offset to center
            surface.blit(tmp, (int(p.x - r), int(p.y - r)))

    def _emit(self, x, y, count, speed, life_range, size_range, colors):
        for _ in range(count):
            ang = random.random() * math.tau
            sp = random.uniform(speed * 0.5, speed * 1.0)
            vx = math.cos(ang) * sp
            vy = math.sin(ang) * sp
            life = random.uniform(life_range[0], life_range[1])
            size = random.uniform(size_range[0], size_range[1])
            color = random.choice(colors)
            self.particles.append(Particle(x, y, vx, vy, life, size, color))

    def emit_wall_break(self, x, y, cell_size):
        """Emit a burst of bright particles for breaking walls.

        x,y are screen coordinates (center). cell_size is used to scale
        the number and size of particles so the effect looks consistent
        at different zoom levels.
        """
        count = max(6, int(cell_size / 6))
        speed = max(80, cell_size * 2.5)
        life = (0.45, 0.9)
        size = (max(2, cell_size * 0.06), max(3, cell_size * 0.18))
        # warm colors
        colors = [
            (255, 200, 60),
            (255, 150, 30),
            (230, 120, 40),
            (200, 90, 30),
        ]
        self._emit(x, y, count, speed, life, size, colors)

    def emit_path_creation(self, x, y, cell_size, path_color=None):
        """Emit subtle particles when a path cell is created.

        path_color can be an RGB tuple to tint the particles.
        """
        count = max(4, int(cell_size / 10))
        speed = max(40, cell_size * 1.0)
        life = (0.6, 1.2)
        size = (max(1, cell_size * 0.04), max(3, cell_size * 0.12))

        if path_color is not None:
            colors = [path_color]
        else:
            # default gentle greenish palette
            colors = [
                (150, 220, 140),
                (120, 200, 120),
                (180, 240, 180),
            ]

        self._emit(x, y, count, speed, life, size, colors)


__all__ = ["ParticleSystem"]
