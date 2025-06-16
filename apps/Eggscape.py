import os
import pygame
from enum import Enum

os.environ['SDL_VIDEO_CENTERED'] = '1'

class RunState(Enum):
    INACTIVE = 1,
    ACTIVE = 2,
    PLAYER_DEAD = 3
    LEVEL_WON = 4
    COUNTDOWN = 5

class Eggscape:
    def __init__(self):
        pass

    def run(self):
        while self.running:
            self.play_game()
            self.running = self.continue_game

if __name__ == "__main__":
    game = Eggscape()
    game.run()