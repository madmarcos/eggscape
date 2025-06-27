import os
import pygame
from enum import Enum
from Game1 import Game1

os.environ['SDL_VIDEO_CENTERED'] = '1'

class Credit:
    def __init__(self, font, txt, w, y):
        self.surface = font.render(txt, True, (200, 200, 200))
        self.x = (w - self.surface.get_width()) / 2
        self.y = y

class Settings:
    def __init__(self):
        self.display_width = 1000
        self.display_height = 700

class Eggscape:
    def __init__(self):
        self.settings = Settings()
        self.splash_screen = False
        self.credits = False
        self.clock = pygame.time.Clock()
        self.ticks = 0
        
    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.KEYDOWN:
                if self.splash_screen and self.ticks > 620:
                    self.splash_screen = False
                elif self.credits and self.ticks > 300:
                    self.credits = False
                    
    def show_splash_page(self):
        self.splash_screen = True
        text_font = pygame.font.Font("fonts/SEVESBRG.TTF", 36)
        text2_font = pygame.font.Font("fonts/SEVESBRG.TTF", 48)
        title_font = pygame.font.Font("fonts/shadow_dead.ttf", 58)

        self.window = pygame.display.set_mode((
            self.settings.display_width,
            self.settings.display_height))
        
        pygame.mixer.music.load('sounds/splash.wav')

        self.ticks = 0
        line_1_rgb_val = pygame.Color(0, 0, 0)
        line_2_rgb_val = pygame.Color(0, 0, 0)
        while self.splash_screen:
            self.process_input()

            # render
            self.window.fill((0,0,0))

            if self.ticks == 59:
                pygame.mixer.music.play(-1)

            if self.ticks > 60 and self.ticks < 180:
                line_1_rgb_val.r = int((self.ticks - 60) * (255 / 120))
                line_1_rgb_val.g = line_1_rgb_val.r
                line_1_rgb_val.b = line_1_rgb_val.r
            if self.ticks > 240 and self.ticks < 360:
                line_2_rgb_val.r = int((self.ticks - 240) * (255 / 120))
                line_2_rgb_val.g = line_2_rgb_val.r
                line_2_rgb_val.b = line_2_rgb_val.r

            if self.ticks > 60:
                surface = text_font.render("Studio Docrob Presents", True, line_1_rgb_val)
                self.window.blit(surface, ((self.window.get_width() - surface.get_width()) / 2, 120))
            if self.ticks > 240:
                surface = text2_font.render("EGGSCAPE", True, line_2_rgb_val)
                self.window.blit(surface, ((self.window.get_width() - surface.get_width()) / 2, 200))
            if self.ticks > 433:
                surface = title_font.render("FROM BREAKFAST", True, (160, 0, 0))
                self.window.blit(surface, ((self.window.get_width() - surface.get_width()) / 2, 250))
            if self.ticks > 620:
                surface = text_font.render("Press any key...", True, (0, 160, 0))
                self.window.blit(surface, ((self.window.get_width() - surface.get_width()) / 2, 450))

            pygame.display.update()

            self.clock.tick(60)
            self.ticks += 1
            
        pygame.mixer.music.unload()

    def show_credits(self):
        self.credits = True

        self.window = pygame.display.set_mode((
            self.settings.display_width,
            self.settings.display_height))

        text_font = pygame.font.Font("fonts/Adventure.otf", 36)
        text2_font = pygame.font.Font("fonts/shadow_dead.ttf", 30)

        pygame.mixer.music.load('sounds/end.wav')

        y = 800
        credits = []
        credits.append(Credit(text2_font, "Designer".upper(), self.window.get_width(), y))
        y += 60
        credits.append(Credit(text_font, "Docrob", self.window.get_width(), y))
        y += 80
        credits.append(Credit(text2_font, "Dev".upper(), self.window.get_width(), y))
        y += 60
        credits.append(Credit(text_font, "Docrob", self.window.get_width(), y))
        y += 80
        credits.append(Credit(text2_font, "Artiste".upper(), self.window.get_width(), y))
        y += 60
        credits.append(Credit(text_font, "Solum", self.window.get_width(), y))
        y += 80
        credits.append(Credit(text2_font, "Critic".upper(), self.window.get_width(), y))
        y += 60
        credits.append(Credit(text_font, "Dawn", self.window.get_width(), y))
        y += 80
        credits.append(Credit(text2_font, "Sigma".upper(), self.window.get_width(), y))
        y += 60
        credits.append(Credit(text_font, "Jake", self.window.get_width(), y))
        y += 80
        credits.append(Credit(text2_font, "Dogs".upper(), self.window.get_width(), y))
        y += 60
        credits.append(Credit(text_font, "Oliver and Bersi", self.window.get_width(), y))

        pygame.mixer.music.play(5)

        self.ticks = 0
        while self.credits:
            self.process_input()

            # render
            self.window.fill((0,0,0))

            for credit in credits:
                self.window.blit(credit.surface, (credit.x, credit.y - self.ticks))

            pygame.display.update()

            self.clock.tick(60)
            self.ticks += 1
            
    def init_game(self):
        pygame.init()
        pygame.display.set_caption('Eggscape from Breakfast')
        pygame.display.set_icon(pygame.image.load("images/dude.png"))
        pygame.mixer.init()

    def close_game(self):
        pygame.quit()

    def run(self):
        self.init_game()

        # self.show_splash_page()

        # game = Game1()
        # game.run()

        self.show_credits()

        self.close_game()

if __name__ == "__main__":
    app = Eggscape()
    app.run()