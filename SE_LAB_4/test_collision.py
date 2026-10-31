from game.fruit import Fruit

f = Fruit(100, 100, 0, 0, 0.0, radius=20)
assert f.intersects_segment((0, 100), (200, 100))
assert not f.intersects_segment((0, 10), (200, 10))
assert f.intersects_segment((80, 80), (120, 120))
assert not f.intersects_segment((0, 200), (200, 200))
print('PASS: swept-segment collision geometry')

# Moving fruit crosses a stationary blade between updates.
moving = Fruit(200, 100, 0, 0, 0.0, radius=20)
moving.prev_x = 0
moving.prev_y = 100
assert moving.intersects_segment((100, 100), (100, 100))
print('PASS: moving-fruit relative collision')
