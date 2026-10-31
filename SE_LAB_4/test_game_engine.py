import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
pygame.init()
from game.game_engine import GameEngine, DIFFICULTIES
from game.fruit import Fruit

# Swept collision: segment crosses the circle although neither endpoint is inside.
f = Fruit(100, 100, 0, 0, 0.0, radius=20)
assert f.intersects_segment((0, 100), (200, 100))
assert not f.intersects_segment((0, 10), (200, 10))

engine = GameEngine(700, 600)
engine.fruits = [Fruit(100, 100, 0, 0, 0.0, kind='fruit')]
engine._last_mouse_pos = (0, 100)
engine._handle_motion((200, 100))
assert engine.score == 1, engine.score
assert engine.fruits[0].sliced

# Bomb ends game and freezes final score.
engine.reset_game()
engine.score = 4
bomb = Fruit(100, 100, 0, 0, 0.0, kind='bomb')
engine.fruits = [bomb]
engine._last_mouse_pos = (0, 100)
engine._handle_motion((200, 100))
assert engine.game_over and engine.final_score == 4

# Losing all lives ends the game with final score.
engine.reset_game()
engine.lives = 1
engine.fruits = [Fruit(100, 610, 0, 2, 0.0, radius=25, kind='fruit')]
engine.update()
assert engine.game_over and engine.game_over_reason == 'OUT OF LIVES'

# Difficulty values materially vary.
assert DIFFICULTIES['EASY']['spawn_interval'] > DIFFICULTIES['MEDIUM']['spawn_interval'] > DIFFICULTIES['HARD']['spawn_interval']
engine.selected_difficulty = 'HARD'
engine.reset_game()
assert engine.bomb_chance == DIFFICULTIES['HARD']['bomb_chance']

# Game-over UI renders without requiring an actual display window.
screen = pygame.Surface((700, 600))
engine.render(screen)
pygame.quit()
print('PASS: swept collision, fruit score, bomb game-over, life game-over, difficulty settings and rendering')
