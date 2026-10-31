"""Fruit and bomb physics/collision model."""
import math


class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit"):
        self.x = float(x)
        self.y = float(y)
        self.prev_x = float(x)
        self.prev_y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.gravity = float(gravity)
        self.radius = int(radius)
        self.kind = kind
        self.sliced = False
        self.color = (220, 60, 60)

    def update(self):
        self.prev_x, self.prev_y = self.x, self.y
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        return math.hypot(self.x - x, self.y - y) <= self.radius

    @staticmethod
    def _point_segment_distance(px, py, ax, ay, bx, by):
        """Minimum Euclidean distance from point P to segment AB."""
        dx, dy = bx - ax, by - ay
        denom = dx * dx + dy * dy
        if denom == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denom))
        closest_x, closest_y = ax + t * dx, ay + t * dy
        return math.hypot(px - closest_x, py - closest_y)

    def intersects_segment(self, start, end, padding=0):
        """Continuous collision test accounting for blade and fruit movement.

        Both the mouse blade point and fruit centre are assumed to move linearly
        over the same event interval. In relative coordinates, collision occurs
        when the relative path segment comes within the fruit radius of origin.
        This catches fast swipes and fruit motion between rendered frames.
        """
        ax, ay = start
        bx, by = end
        relative_start = (self.prev_x - ax, self.prev_y - ay)
        relative_end = (self.x - bx, self.y - by)
        return self._point_segment_distance(
            0.0, 0.0,
            relative_start[0], relative_start[1],
            relative_end[0], relative_end[1]
        ) <= self.radius + padding

    def off_screen(self, height):
        return self.y - self.radius > height
