import os

import pygame
import sys

from pygame import Surface
from pygame.font import Font
from pygame.mixer import Sound
from pygame.time import Clock


class Invaders:

    level: int
    lives: int
    running: bool
    landed: bool
    points: int
    pause: bool
    volume: float
    gameover: bool
    highscore: int

    start_time: int

    screen: Surface
    screen_width: int
    screen_height: int

    laser_sound: Sound
    gameover_sound: Sound
    alien_sound: Sound

    clock: Clock

    invader1: Surface
    invader2: Surface
    invader3: Surface
    invader_width: int
    invader_height: int

    tank: Surface
    tank_width: int
    tank_height: int

    small_font: Font
    large_font: Font
    huge_font: Font

    start_text: list[Surface]
    start_text_width: list[int]
    start_text_height: list[int]
    start_text_x: list[int]
    start_text_y: list[int]

    level_text: Surface
    lives_text: Surface
    points_text: Surface
    highscore_text: Surface
    pause_text: Surface
    gameover_text: Surface

    invader_rows: int
    invader_cols: int
    invader_count: int
    invader_x: list[list[int | None]]
    invader_y: list[list[int | None]]
    invader_i: list[list[int | None]]
    invader_d: int
    invader_t: int
    invader_l: int
    invader_h: int
    invader_z: int

    tank_x: int
    tank_y: int
    tank_d: int

    missile_x: int | None
    missile_y: int | None
    missile_h: int

    low_motion: bool

    BLACK: tuple[int, int, int]
    WHITE: tuple[int, int, int]
    YELLOW: tuple[int, int, int]

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Alien Invaders 2025")
        self.low_motion = False
        self.volume = 0.1
        self.highscore = 0
        self.reset_game()
        self.define_screen()
        self.define_sounds()
        self.define_invader()
        self.define_tank()
        self.define_clock()
        self.define_colours()
        self.define_text()
        self.reset_board()

    def resource(self, name):
        return os.path.join(os.path.dirname(__file__), name)


    def define_screen(self):
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def define_sounds(self):
        self.laser_sound = pygame.mixer.Sound(self.resource("laser.ogg"))
        self.gameover_sound = pygame.mixer.Sound(self.resource("gameover.ogg"))
        self.alien_sound = pygame.mixer.Sound(self.resource("alien.ogg"))

    def define_invader(self):
        self.invader1 = pygame.image.load(self.resource('invader-1.png'))
        self.invader2 = pygame.image.load(self.resource('invader-2.png'))
        self.invader3 = pygame.image.load(self.resource('invader-3.png'))
        self.invader_width = self.invader1.get_width()
        self.invader_height = self.invader1.get_height()

    def define_tank(self):
        self.tank = pygame.image.load(self.resource('tank-1.png'))
        self.tank_width = self.tank.get_width()
        self.tank_height = self.tank.get_height()

    def define_clock(self):
        self.clock = pygame.time.Clock()

    def define_colours(self):
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)

    def define_text(self):
        self.small_font = pygame.font.Font('freesansbold.ttf', 16)
        self.large_font = pygame.font.Font('freesansbold.ttf', 32)
        self.huge_font = pygame.font.Font('freesansbold.ttf', 64)

        self.start_text = [
            self.large_font.render(text, True, self.WHITE)
            for text in [
                'Press ENTER/RETURN To Start',
                'Z or LEFT = Left',
                'X or RIGHT = Right',
                '/ or UP = Fire',
                'L = Low Motion / Normal Motion',
                'P = Pause / Resume',
                '+ or - = Louder / Quieter',
                'ESC = Exit Game',
            ]
        ]
        self.start_text_width = [
            text.get_width()
            for text in self.start_text
        ]
        self.start_text_height = [
            text.get_height()
            for text in self.start_text
        ]
        self.start_text_x = [
            (self.screen_width - self.start_text_width[n]) // 2
            for n in range(len(self.start_text))
        ]
        top = (self.screen_height - sum(self.start_text_height)) // 2
        self.start_text_y = [
            top + n * self.start_text_height[0]
            for n in range(len(self.start_text))
        ]

        self.pause_text = self.huge_font.render('GAME PAUSED', True, self.WHITE)
        self.gameover_text = self.huge_font.render('GAME OVER', True, self.YELLOW)

        self.render_text()

    def begin_game(self):
        self.landed = False
        self.start_game()
        self.start_countdown()
        self.reset_board()

    def start_game(self):
        self.running = True

    def stop_game(self):
        self.running = False

    def pause_game(self):
        self.pause = not self.pause

    def start_countdown(self):
        self.start_time = 60

    def reset_invaders(self):
        self.invader_rows = 4
        self.invader_cols = self.screen_width // self.invader_width
        self.invader_count = self.invader_cols * self.invader_rows
        self.invader_x = [
            [
                n * self.invader_width
                for n in range(0, self.invader_cols)
            ]
            for _ in range(self.invader_rows)
        ]  # invader x
        self.invader_y = [
            [
                (self.invader_rows - 1 - n) * self.invader_height
                for _ in range(0, self.invader_cols)
            ]
            for n in range(self.invader_rows)
        ]  # invader y
        self.invader_i = [
            [
                None
                for _ in range(0, self.invader_cols)
            ]
            for _ in range(self.invader_rows)
        ]  # invader i
        self.invader_d = 5  # invader move amount
        self.invader_t = 0  # invader move timer
        self.invader_l = max(5, 40 - self.level * 2)  # time between moves
        self.invader_h = self.invader_height // 2
        self.invader_z = 1

    def reset_tank(self):
        self.tank_x = (self.screen_width - self.tank_width) // 2
        self.tank_y = self.screen_height - self.tank_height
        self.tank_d = 0

    def reset_missile(self):
        self.missile_x = None
        self.missile_y = None
        self.missile_h = 10

    def render_text(self):
        self.level_text = self.small_font.render(f'Level {self.level}', True, self.WHITE)
        self.lives_text = self.small_font.render(f'Lives {self.lives}', True, self.WHITE)
        self.points_text = self.small_font.render(f'{self.points:9,} Points', True, self.WHITE)
        self.highscore_text = self.small_font.render(f'High Score {self.highscore:9,}', True, self.WHITE)

    def reset_game(self):
        self.level = 1
        self.lives = 3
        self.running = False
        self.pause = False
        self.gameover = False
        self.points = 0
        self.start_countdown()

    def reset_board(self):
        self.reset_invaders()
        self.reset_tank()
        self.reset_missile()
        self.render_text()

    def is_running(self):
        return self.running and self.start_time == 0 and not self.pause

    def play_sound(self, sound, level=None):
        playing = pygame.mixer.Sound.play(sound)
        if playing:
            playing.set_volume(level or self.volume)

    def process_events(self):
        looping = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                looping = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.low_motion = not self.low_motion
                elif event.key == pygame.K_ESCAPE:
                    looping = False
                elif event.key == pygame.K_p:
                    if self.running:
                        self.pause_game()
                elif event.unicode == '-':
                    self.volume = max(0.0, self.volume - 0.1)
                elif event.unicode == '+':
                    self.volume = min(0.8, self.volume + 0.1)
                if self.is_running():
                    if event.key == pygame.K_LEFT or event.key == pygame.K_z:
                        self.tank_d = -1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_x:
                        self.tank_d = 1
            elif event.type == pygame.KEYUP:
                if self.is_running():
                    if event.key == pygame.K_LEFT or event.key == pygame.K_z:
                        self.tank_d = 0
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_x:
                        self.tank_d = 0
                    elif event.key == pygame.K_SLASH or event.key == pygame.K_UP:
                        if not self.missile_x:
                            self.missile_x = self.tank_x + self.tank_width // 2 - 1
                            self.missile_y = self.tank_y
                            self.play_sound(self.laser_sound)
                else:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.reset_board()
                        self.begin_game()
        return looping

    def move_invaders(self):
        self.invader_t += 1

        if self.invader_t % 2 == 0:
            for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
                for n in range(len(row_x)):
                    if row_x[n] is not None and row_i[n] is not None:
                        row_y[n] -= row_i[n]
                        if row_y[n] < 0:
                            row_x[n] = None

        if self.invader_t == self.invader_l:
            self.invader_t = 0
            self.invader_z = (self.invader_z + 1) % 2
            if not self.low_motion:
                self.play_sound(self.alien_sound)
            bounce = False
            for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
                for n in range(len(row_x)):
                    if row_x[n] is not None and row_i[n] is None:
                        row_x[n] += self.invader_d
                        if not 0 <= row_x[n] <= self.screen_width - self.invader_width:
                            bounce = True
            if bounce:
                self.invader_d = -self.invader_d  # switch directions
                for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
                    for n in range(len(row_x)):
                        if row_x[n] is not None and row_i[n] is None:
                            row_x[n] += self.invader_d
                            row_y[n] = min(self.screen_height - self.invader_height, row_y[n] + self.invader_h)
                self.invader_l = max(5, self.invader_l - 5)  # speed up the invader a little

    def move_tank(self):
        if self.tank_d < 0:
            self.tank_x = max(0, self.tank_x + self.tank_d)
        elif self.tank_d > 0:
            self.tank_x = min(self.screen_width - self.tank_width, self.tank_x + self.tank_d)

    def move_missile(self):
        if self.missile_x is not None:
            self.missile_y -= self.missile_h
            if self.missile_y <= 0:
                self.missile_x = None
                self.missile_y = None

    def check_missile_collision(self):
        if self.missile_x is None:
            return
        for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
            for n in range(len(row_x)):
                if row_x[n] is not None and row_i[n] is None:
                    if row_x[n] < self.missile_x < row_x[n] + self.invader_width:
                        if row_y[n] < self.missile_y < row_y[n] + self.invader_height:
                            if self.low_motion:
                                row_x[n] = None
                            else:
                                row_i[n] = self.invader_height // 4
                            self.missile_x = None
                            self.missile_y = None
                            self.invader_count = max(0, self.invader_count - 1)
                            self.points += 10
                            self.render_text()
                            return

    @staticmethod
    def collision(one: tuple[int, int, int, int], two: tuple[int, int, int, int]) -> bool:
        mid_x = one[0] + one[2] // 2
        mid_y = one[1] + one[3] // 2
        if two[0] <= mid_x < two[0] + two[2]:
            if two[1] <= mid_y < two[1] + two[3]:
                return True
        return False

    def check_tank_collision(self):
        for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
            for n in range(len(row_x)):
                if row_x[n] is not None and row_i[n] is None:
                    if self.collision((row_x[n], row_y[n], self.invader_width, self.invader_height), (self.tank_x, self.tank_y, self.tank_width, self.tank_height)):
                        return True
        return False

    def check_invader_landed(self):
        for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
            for n in range(len(row_x)):
                if row_x[n] is not None and row_i[n] is None:
                    if row_y[n] == self.screen_height - self.invader_height:
                        return True
        return False

    def check_game_over(self):
        if self.is_running():
            if self.invader_count == 0:
                self.level += 1
                self.start_countdown()
                return
            if self.check_tank_collision() or self.check_invader_landed():
                self.lives = max(0, self.lives - 1)
                if self.lives == 0:
                    self.gameover = True
                    if self.points > self.highscore:
                        self.highscore = self.points
                    self.play_sound(self.gameover_sound, level=max(1.0, self.level + 0.2))
                    self.render_text()
                    self.stop_game()
                else:
                    self.start_countdown()
                return

    def update_assets(self):
        self.move_invaders()
        self.move_tank()
        self.move_missile()
        self.check_missile_collision()
        self.check_game_over()

    def draw_background(self):
        self.screen.fill(self.BLACK)

    def draw_missile(self):
        if self.missile_x is not None:
            self.screen.fill(self.WHITE, (self.missile_x, self.missile_y, 2, 10))

    def draw_tank(self):
        self.screen.blit(self.tank, (self.tank_x, self.tank_y))

    def draw_invaders(self):
        for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
            for n in range(len(row_x)):
                if row_x[n] is not None:
                    if row_i[n] is None:
                        if self.low_motion or self.invader_z == 0:
                            self.screen.blit(self.invader1, (row_x[n], row_y[n]))
                        else:
                            self.screen.blit(self.invader2, (row_x[n], row_y[n]))
        for row_x, row_y, row_i in zip(self.invader_x, self.invader_y, self.invader_i):
            for n in range(len(row_x)):
                if row_x[n] is not None:
                    if row_i[n] is not None:
                        self.screen.blit(self.invader3, (row_x[n], row_y[n]))

    def draw_instructions(self):
        min_x = min(self.start_text_x)
        min_y = min(self.start_text_y)
        max_width = max(self.start_text_width)
        max_height = sum(self.start_text_height)
        self.screen.fill(self.WHITE, (min_x - 10, min_y - 10, max_width + 20, max_height + 20))
        self.screen.fill(self.BLACK, (min_x - 5, min_y - 5, max_width + 10, max_height + 10))
        for n in range(len(self.start_text)):
            self.screen.blit(self.start_text[n], (self.start_text_x[n], self.start_text_y[n]))

    def draw_text(self):
        self.screen.blit(self.level_text, (10, 0))
        self.screen.blit(self.lives_text, (self.screen_width - 10 - self.lives_text.get_width(), 0))
        self.screen.blit(self.points_text, ((self.screen_width - self.points_text.get_width())//4, 0))
        self.screen.blit(self.highscore_text, ((self.screen_width - self.points_text.get_width())*3//4, 0))
        if self.gameover:
            left = (self.screen_width - self.gameover_text.get_width()) // 2
            top = 80
            self.screen.blit(self.gameover_text, (left, top))
        if self.running:
            if self.pause:
                left = (self.screen_width - self.pause_text.get_width()) // 2
                top = 80
                self.screen.blit(self.pause_text, (left, top))
                self.draw_instructions()
        else:
            self.draw_instructions()

    @staticmethod
    def update_screen():
        pygame.display.flip()

    def draw_screen(self):
        self.draw_background()
        self.draw_missile()
        self.draw_tank()
        self.draw_invaders()
        self.draw_text()
        self.update_screen()

    def manage_frame_rate(self):
        self.clock.tick(60)

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()

    def handle_countdown(self):
        self.start_time = max(0, self.start_time - 1)
        if self.start_time == 0:
            self.reset_board()

    def run(self):
        looping = True
        while looping:
            looping = self.process_events()
            if self.is_running():
                self.update_assets()
            elif self.start_time > 0:
                self.handle_countdown()
            self.draw_screen()
            self.manage_frame_rate()
        self.quit()


def run():
    Invaders().run()

if __name__ == '__main__':
    run()
