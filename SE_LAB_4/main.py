"""Fruit Slice - improved Fruit Ninja style game for SE Lab 4.

Controls: move the mouse to slice fruit. After game over, choose Easy/Medium/Hard,
press ENTER to replay with the selected difficulty, or ESC to quit.
"""
import pygame
from game.game_engine import GameEngine

WIDTH, HEIGHT = 700, 600
FPS = 60
BACKGROUND = (20, 25, 45)


def main():
    pygame.init()
    # Sound is optional: the engine safely falls back if mixer/audio is unavailable.
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Slice | SE Lab 4")
    clock = pygame.time.Clock()
    engine = GameEngine(WIDTH, HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                engine.handle_event(event)

        engine.handle_input()
        engine.update()
        screen.fill(BACKGROUND)
        engine.render(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
