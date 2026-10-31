"""Game state, difficulty, collision, audio and rendering for Fruit Slice."""
import math
import os
import random
import struct
import tempfile
import wave

import pygame
from .fruit import Fruit

WHITE = (245, 247, 255)
MUTED = (165, 177, 202)
DARK_PANEL = (30, 38, 64)
FRUIT_COLORS = [(235, 83, 90), (247, 157, 61), (246, 211, 79), (100, 202, 133)]

DIFFICULTIES = {
    "EASY": {"spawn_interval": 72, "bomb_chance": 0.08, "speed_scale": 0.88, "label": "Relaxed pace"},
    "MEDIUM": {"spawn_interval": 55, "bomb_chance": 0.15, "speed_scale": 1.00, "label": "Balanced challenge"},
    "HARD": {"spawn_interval": 39, "bomb_chance": 0.23, "speed_scale": 1.16, "label": "Fast and risky"},
}


class SoundBank:
    """Generate short WAV effects locally; no bundled audio files are needed."""
    def __init__(self):
        self.sounds = {}
        if not pygame.mixer.get_init():
            return
        try:
            self.sounds = {
                "slice": self._make_tone(660, 0.075, 0.20, sweep=260),
                "bomb": self._make_tone(115, 0.35, 0.34, sweep=-65),
                "over": self._make_tone(260, 0.45, 0.27, sweep=-150),
            }
        except (pygame.error, OSError, ValueError):
            self.sounds = {}

    @staticmethod
    def _make_tone(frequency, duration, volume, sweep=0):
        sample_rate = 22050
        frames = int(sample_rate * duration)
        fd, path = tempfile.mkstemp(suffix=".wav", prefix="fruit_slice_")
        os.close(fd)
        try:
            with wave.open(path, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                data = bytearray()
                phase = 0.0
                for i in range(frames):
                    t = i / max(1, frames - 1)
                    freq = max(35, frequency + sweep * t)
                    phase += 2 * math.pi * freq / sample_rate
                    envelope = (1 - t) ** 1.7
                    sample = int(32767 * volume * envelope * math.sin(phase))
                    data.extend(struct.pack("<h", sample))
                wav.writeframes(data)
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.55)
            return sound
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def play(self, key):
        sound = self.sounds.get(key)
        if sound is not None:
            try:
                sound.play()
            except pygame.error:
                self.sounds.clear()


class GameEngine:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.font_title = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 34, bold=True)
        self.font = pygame.font.SysFont("Arial", 25)
        self.font_small = pygame.font.SysFont("Arial", 19)
        self.font_tiny = pygame.font.SysFont("Arial", 16)
        self.sound = SoundBank()
        self.selected_difficulty = "MEDIUM"
        self._difficulty_rects = {}
        self._replay_rect = pygame.Rect(0, 0, 0, 0)
        self.reset_game()

    def apply_difficulty(self):
        settings = DIFFICULTIES[self.selected_difficulty]
        self.spawn_interval = settings["spawn_interval"]
        self.bomb_chance = settings["bomb_chance"]
        self.speed_scale = settings["speed_scale"]

    def reset_game(self):
        self.apply_difficulty()
        self.fruits = []
        self.trail = []
        self._spawn_timer = 0
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""
        self.final_score = None
        self._game_over_sound_played = False
        self._last_mouse_pos = None
        self._difficulty_rects = {}

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2.5, 2.5)
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"
        fruit = Fruit(x, self.height + 30, vx, vy, 0.35 * self.speed_scale, kind=kind)
        fruit.color = (35, 39, 53) if kind == "bomb" else random.choice(FRUIT_COLORS)
        self.fruits.append(fruit)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if not self.game_over:
                self._handle_motion(event.pos)
            else:
                self._last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.game_over:
            if self._replay_rect.collidepoint(event.pos):
                self.reset_game()
                return
            for difficulty, rect in self._difficulty_rects.items():
                if rect.collidepoint(event.pos):
                    self.selected_difficulty = difficulty
                    return
        elif event.type == pygame.KEYDOWN and self.game_over:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_game()
            elif event.key == pygame.K_1:
                self.selected_difficulty = "EASY"
            elif event.key == pygame.K_2:
                self.selected_difficulty = "MEDIUM"
            elif event.key == pygame.K_3:
                self.selected_difficulty = "HARD"

    def _handle_motion(self, pos):
        if self._last_mouse_pos is not None:
            start, end = self._last_mouse_pos, pos
            for fruit in list(self.fruits):
                if not fruit.sliced and fruit.intersects_segment(start, end, padding=5):
                    self._slice(fruit)
                    if self.game_over:
                        break
            self.trail.append((pos, 0))
        else:
            self.trail.append((pos, 0))
        self._last_mouse_pos = pos
        self.trail = [(point, age + 1) for point, age in self.trail if age < 13]
        if len(self.trail) > 18:
            self.trail = self.trail[-18:]

    def _slice(self, fruit):
        fruit.sliced = True
        if fruit.kind == "bomb":
            self.sound.play("bomb")
            self._end_game("BOMB SLICED")
        else:
            self.score += 1
            self.sound.play("slice")

    def _end_game(self, reason):
        if self.game_over:
            return
        self.game_over = True
        self.game_over_reason = reason
        self.final_score = self.score
        if not self._game_over_sound_played:
            self.sound.play("over")
            self._game_over_sound_played = True

    def handle_input(self):
        pass

    def update(self):
        if self.game_over:
            return
        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        remaining = []
        for fruit in self.fruits:
            fruit.update()
            if fruit.sliced:
                continue
            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue
            remaining.append(fruit)
        self.fruits = remaining
        self.trail = [(point, age + 1) for point, age in self.trail if age < 12]
        if self.lives <= 0:
            self._end_game("OUT OF LIVES")

    def render(self, screen):
        self._draw_background(screen)
        if self.game_over:
            self._draw_game_over(screen)
        else:
            self._draw_game(screen)

    def _draw_background(self, screen):
        screen.fill((20, 25, 45))
        pygame.draw.line(screen, (42, 54, 83), (0, self.height - 15), (self.width, self.height - 15), 2)
        pygame.draw.circle(screen, (29, 40, 68), (self.width - 30, 100), 90, 2)
        pygame.draw.circle(screen, (29, 40, 68), (35, self.height - 55), 55, 2)

    def _draw_game(self, screen):
        title = self.font_title.render("FRUIT SLICE", True, WHITE)
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
        score = self.font.render(f"SCORE  {self.score:03d}", True, WHITE)
        lives = self.font.render(f"LIVES  {self.lives}", True, WHITE)
        diff = self.font_small.render(self.selected_difficulty, True, (118, 205, 255))
        screen.blit(score, (22, 27))
        screen.blit(lives, (self.width - lives.get_width() - 22, 27))
        screen.blit(diff, (self.width // 2 - diff.get_width() // 2, 70))

        for fruit in self.fruits:
            if fruit.kind == "bomb":
                pygame.draw.circle(screen, (15, 18, 28), (int(fruit.x), int(fruit.y)), fruit.radius + 3)
                pygame.draw.circle(screen, (205, 211, 226), (int(fruit.x), int(fruit.y)), fruit.radius, 2)
                pygame.draw.circle(screen, (246, 178, 80), (int(fruit.x + 7), int(fruit.y - 23)), 5)
                pygame.draw.circle(screen, (220, 90, 75), (int(fruit.x), int(fruit.y)), 5)
            else:
                pygame.draw.circle(screen, fruit.color, (int(fruit.x), int(fruit.y)), fruit.radius)
                pygame.draw.circle(screen, (255, 255, 255), (int(fruit.x - 8), int(fruit.y - 9)), 6)
                pygame.draw.line(screen, (77, 150, 88), (int(fruit.x), int(fruit.y - fruit.radius + 3)),
                                 (int(fruit.x + 5), int(fruit.y - fruit.radius - 9)), 4)

        points = [point for point, _age in self.trail]
        if len(points) >= 2:
            pygame.draw.lines(screen, (180, 235, 255), False, points, 4)
            pygame.draw.lines(screen, (75, 168, 235), False, points, 1)
        hint = self.font_tiny.render("Move your mouse through fruit to slice. Avoid bombs!", True, MUTED)
        screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 35))

    def _draw_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((6, 10, 24, 220))
        screen.blit(overlay, (0, 0))
        panel = pygame.Rect(75, 55, self.width - 150, self.height - 110)
        pygame.draw.rect(screen, DARK_PANEL, panel, border_radius=22)
        pygame.draw.rect(screen, (75, 105, 155), panel, width=2, border_radius=22)

        title = self.font_title.render("GAME OVER", True, (255, 115, 112))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 82))
        reason = self.font.render(self.game_over_reason, True, MUTED)
        screen.blit(reason, (self.width // 2 - reason.get_width() // 2, 137))
        final = self.font_large.render(f"FINAL SCORE  {self.final_score:03d}", True, WHITE)
        screen.blit(final, (self.width // 2 - final.get_width() // 2, 184))

        prompt = self.font.render("Choose difficulty for your next round", True, WHITE)
        screen.blit(prompt, (self.width // 2 - prompt.get_width() // 2, 250))
        self._difficulty_rects = {}
        button_w, gap = 150, 18
        start_x = self.width // 2 - (button_w * 3 + gap * 2) // 2
        for i, name in enumerate(("EASY", "MEDIUM", "HARD")):
            rect = pygame.Rect(start_x + i * (button_w + gap), 292, button_w, 57)
            self._difficulty_rects[name] = rect
            active = self.selected_difficulty == name
            color = (42, 112, 100) if active else (49, 64, 96)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (117, 202, 232) if active else (89, 112, 151), rect, 2, border_radius=10)
            label = self.font.render(name, True, WHITE)
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.y + 8))
            desc = self.font_tiny.render(DIFFICULTIES[name]["label"], True, (207, 218, 235))
            screen.blit(desc, (rect.centerx - desc.get_width() // 2, rect.y + 36))

        self._replay_rect = pygame.Rect(self.width // 2 - 140, 380, 280, 48)
        pygame.draw.rect(screen, (62, 142, 91), self._replay_rect, border_radius=11)
        replay = self.font.render("PLAY AGAIN  [ENTER]", True, WHITE)
        screen.blit(replay, (self._replay_rect.centerx - replay.get_width() // 2,
                             self._replay_rect.centery - replay.get_height() // 2))
        controls = self.font_small.render("1 / 2 / 3 select difficulty     |     ESC quit", True, MUTED)
        screen.blit(controls, (self.width // 2 - controls.get_width() // 2, 447))
        selected = self.font_tiny.render(f"Next round: {self.selected_difficulty}", True, (118, 205, 255))
        screen.blit(selected, (self.width // 2 - selected.get_width() // 2, 474))
