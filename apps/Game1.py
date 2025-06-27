import os
import pygame
from enum import Enum

os.environ['SDL_VIDEO_CENTERED'] = '1'

LEVEL_1 = [
    "________________________",
    "|                    XX|",
    "|                    XX|",
    "|   _________________XX|",
    "|   |                  |",
    "|   |                  |",
    "|   |                  |",
    "|                      |",
    "|                      |",
    "L____________________  |",
    "|                      |",
    "|                      |",
    "L   ___________________|",
]

LEVEL_2 = [
    "________________________",
    "|                    XX|",
    "|                    XX|",
    "|   _________________XX|",
    "|   |                  |",
    "|   |                  |",
    "|       ____________   |",
    "|       |              |",
    "L_______|              |",
    "|       |   ___________|",
    "|       |              |",
    "|       |              |",
    "|   |   L___________   |",
    "|   |                  |",
    "|   |                  |",
    "|   L__________________|",
]

PLAYER_HEALTH_MAX = 400
PLAYER_START_X = 5
PLAYER_START_Y = 85
FIRE_DAMAGE_PER_TICK = 2

class GameStatus(Enum):
    INACTIVE = 1,
    ACTIVE = 2,
    PLAYER_DEAD = 3
    LEVEL_WON = 4
    COUNTDOWN = 5

class Settings:
    def __init__(self):
        self.display_width = 1000
        self.display_height = 700

class Goal:
    def __init__(self, x, y, width, height):
        self.y = float(y)
        self.goal_rect = pygame.Rect(x, y, width, height)

class GameState:
    """
    Game coords 0,0 are upper left corner
    x grows from left to right
    y grows from top to bottom
    """
    def __init__(self):
        # I think player x,y is upper left corner of player area
        self.player_rect = pygame.Rect(5, 85, 10, 10)
        self.player_health = 100
        self.player_image = None
        self.game_height = 100
        self.game_width = 100
        # game_scroll_speed is how fast the walls move downward
        self.game_scroll_speed = .1
        self.game_status = GameStatus.INACTIVE
        self.goal = None
        self.hit_wall = False
        self.player_frying = False

class Wall:
    def __init__(self, x, y, width, height):
        self.y = float(y)
        self.wall_rect = pygame.Rect(x, y, width, height)

class Game1:
    def __init__(self):
        self.running = True
        self.continue_game = False

    def init_level(self, level_num):
        level = LEVEL_1
        if level_num == 2:
            level = LEVEL_2
        self.game_state.game_width = len(level[0]) * 5

        self.walls = []
        # as we discover the vertically-specd walls, store them until each is "done"
        col_walls = []
        # vars for discovering width and height of the goal rect
        goal_x = 0
        goal_y = 0
        for i in range(len(level[0])):
            col_walls.append(None)
        # scan map one row at a time
        for row_index in range(len(level)):
            row = level[row_index]
            # we only discover one horizontal wall at a time
            row_wall = None
            for col_index in range(len(row)):
                char = row[col_index]
                if char == "X":
                    if not self.game_state.goal:
                        self.game_state.goal = Goal(col_index * 5, row_index * 5, 5, 5)
                        goal_x = col_index
                        goal_y = row_index
                    else:
                        if col_index > goal_x:
                            self.game_state.goal.goal_rect.width += 5
                            goal_x = col_index
                        if row_index > goal_y:
                            self.game_state.goal.goal_rect.height += 5
                            goal_y = row_index
                    # extend horizontal wall by 1 if next cell is a vertical wall
                    if col_index < (len(row) - 1) and row[col_index + 1] == "|":
                        self.game_state.goal.goal_rect.width += 1

                    # if the bottom-most X then also do a row wall
                    if row_index == len(level) - 1 or level[row_index + 1][col_index] != "X":
                        char = "_"
                if char == "_" or char == "L":
                    if not row_wall:
                        row_wall = Wall(col_index * 5, (row_index + 1) * 5, 5, 1)
                    else: # extend the current horizontal wall
                        row_wall.wall_rect.width += 5
                    # extend horizontal wall by 1 if next cell is a vertical wall
                    if col_index < (len(row) - 1) and row[col_index + 1] == "|":
                        row_wall.wall_rect.width += 1
                if char == "|" or char == "L":
                    if not col_walls[col_index]:
                        col_walls[col_index] = Wall(col_index * 5, row_index * 5, 1, 5)
                    else:
                        col_walls[col_index].wall_rect.height += 5
                if char == " ":
                    if row_wall: # end the current horizontal wall
                        self.walls.append(row_wall)
                        row_wall = None
                    if col_walls[col_index]:
                        # if this is a rightmost wall then push it over by 5
                        if col_index == len(level[0]) - 1:
                            col_walls[col_index].wall_rect.x += 4
                            col_walls[col_index].wall_rect.width = 2
                        self.walls.append(col_walls[col_index])
                        col_walls[col_index] = None
            if row_wall:
                # if this wall hits the map's right side then extend it 5 more
                row_wall.wall_rect.width += 5
                self.walls.append(row_wall)

            
        # finish up any walls that are still open
        for col_index in range(len(level[0])):
            if col_walls[col_index]:
                # if this is a rightmost wall then push it over by 5
                if col_index == len(level[0]) - 1:
                    col_walls[col_index].wall_rect.x += 4
                    col_walls[col_index].wall_rect.width = 2
                self.walls.append(col_walls[col_index])
                col_walls[col_index] = None

        # shift all walls up so bottom of level is at the bottom of the screen
        # when the level starts
        for wall in self.walls:
            wall.y -= 50
            wall.wall_rect = pygame.Rect(
                wall.wall_rect.x,
                wall.y,
                wall.wall_rect.width,
                wall.wall_rect.height
            )

        # shift the goal as well
        self.game_state.goal.y -= 50
        self.game_state.goal.goal_rect = pygame.Rect(
            self.game_state.goal.goal_rect.x,
            self.game_state.goal.y,
            self.game_state.goal.goal_rect.width,
            self.game_state.goal.goal_rect.height
        )
        self.goal_image = pygame.transform.scale(self.goal_image, (self.translate_x(self.game_state.goal.goal_rect.width), self.translate_y(self.game_state.goal.goal_rect.height)))

    def reset_player(self):
        self.game_state.player_health = PLAYER_HEALTH_MAX
        self.game_state.player_rect.x = PLAYER_START_X
        self.game_state.player_rect.y = PLAYER_START_Y
        self.game_state.player_rolling = False
        self.game_state.player_frying = False

    def load_level(self, level_num):
        """
        Loads the level and resets some game state
        """
        self.pause = False
        self.game_state.game_status = GameStatus.COUNTDOWN
        self.game_state.countdown_timer = 0
        self.game_state.goal = None
        self.init_level(level_num)
        self.reset_player()
        self.tick_num = 0
        
        if level_num == 1:
            pygame.mixer.music.load('sounds/begins.wav')
        else:
            pygame.mixer.music.load('sounds/hurry.wav')
        pygame.mixer.music.set_volume(.25)
        
    def get_sprite_frame(self, sheet, x, y, width, height):
        frame = pygame.Surface([width, height], pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (x, y, width, height))
        return frame

    def init_game(self):
        # pygame.init()
        
        # holding a key sents another event every 100ms
        pygame.key.set_repeat(100)

        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.game_state = GameState()

        # load images and fonts
        self.blood_splat = pygame.image.load("images/bloodsplats_0003.png")
        self.blood_splat = pygame.transform.scale(self.blood_splat, (300, 300))
        pygame.display.set_icon(pygame.image.load("images/dude.png"))
        self.text_font = pygame.font.Font("fonts/SEVESBRG.TTF", 36)
        self.countdown_font = pygame.font.Font("fonts/SEVESBRG.TTF", 48)
        self.title_font = pygame.font.Font("fonts/shadow_dead.ttf", 48)

        self.game_state.player_image = pygame.image.load("images/egg1.png")
        self.game_state.player_image = pygame.transform.scale(self.game_state.player_image, (self.translate_x(self.game_state.player_rect.width), self.translate_y(self.game_state.player_rect.height)))
        self.game_state.dead_image = pygame.image.load("images/dead.png")
        self.game_state.dead_image = pygame.transform.scale(self.game_state.dead_image, (self.translate_x(self.game_state.player_rect.width), self.translate_y(self.game_state.player_rect.height)))
        self.game_state.pan_image = pygame.image.load("images/pan.png")
        self.game_state.pan_image = pygame.transform.scale(self.game_state.pan_image, (self.translate_x(self.game_state.player_rect.width + 15), self.translate_y(self.game_state.player_rect.height + 15)))
        
        fire_sheet = pygame.image.load("images/firespritesheet.png")
        self.fire_images = [
            pygame.transform.scale(self.get_sprite_frame(fire_sheet, 0, 0, 41, 40), (82, 80)),
            pygame.transform.scale(self.get_sprite_frame(fire_sheet, 43, 0, 41, 40), (82, 80)),
            pygame.transform.scale(self.get_sprite_frame(fire_sheet, 85, 0, 41, 40), (82, 80)),
        ]
        self.fire_counter = 0

        self.goal_image = pygame.image.load("images/nest_64.png")

        # load sounds        
        self.victory_sound = pygame.mixer.Sound("sounds/victory.wav")
        self.victory_sound.set_volume(.1)
        self.death_sound = pygame.mixer.Sound("sounds/death.wav")
        self.hit_wall_sound = pygame.mixer.Sound("sounds/egg_roll.wav")
        self.hit_wall_sound_channel = None
        self.egg_fry_sound = pygame.mixer.Sound("sounds/egg_fry.wav")
        self.egg_fry_sound.set_volume(.2)
        self.egg_fry_sound_channel = None

        self.window = pygame.display.set_mode((
            self.settings.display_width,
            self.settings.display_height))

        self.load_level(1)

    def init_input(self):
        self.move_x = 0
        self.move_y = 0

    def process_input(self):
        self.init_input()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state.game_status = GameStatus.INACTIVE
                self.continue_game = False
                break
            elif event.type == pygame.KEYDOWN:
                if self.game_state.game_status == GameStatus.LEVEL_WON:
                    self.load_level(2)
                    break
                elif self.game_state.game_status == GameStatus.PLAYER_DEAD:
                    if event.key == pygame.K_y:
                        self.continue_game = True
                        self.game_state.game_status = GameStatus.INACTIVE
                        break
                    elif event.key == pygame.K_n:
                        self.continue_game = False
                        self.game_state.game_status = GameStatus.INACTIVE
                        break
                elif self.game_state.game_status == GameStatus.ACTIVE:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.game_status = GameStatus.INACTIVE
                        self.continue_game = False
                        break
                    elif event.key == pygame.K_SPACE:
                        self.pause = not self.pause
                        if self.pause:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()                            
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.move_x = 2
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.move_x = -2
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.move_y = 2
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.move_y = -2

    def move_walls(self):
        for wall in self.walls:
            wall.y += self.game_state.game_scroll_speed
            wall.wall_rect = pygame.Rect(wall.wall_rect.x, wall.y, wall.wall_rect.width, wall.wall_rect.height)

    def move_goal(self):
        self.game_state.goal.y += self.game_state.game_scroll_speed
        self.game_state.goal.goal_rect = pygame.Rect(self.game_state.goal.goal_rect.x, self.game_state.goal.y, self.game_state.goal.goal_rect.width, self.game_state.goal.goal_rect.height)

    def update_state(self):
        self.game_state.hit_wall = False
        self.game_state.player_frying = False

        self.game_state.player_rect.x += self.move_x
        # check for horizontal edges of screen
        if self.game_state.player_rect.x < 0:
            self.game_state.player_rect.x = 0
        elif self.game_state.player_rect.x + self.game_state.player_rect.width > self.game_state.game_width:
            self.game_state.player_rect.x = self.game_state.game_width - self.game_state.player_rect.width

        self.game_state.player_rect.y += self.move_y
        # check for vertical edges of screen
        if self.game_state.player_rect.y < 0:
            self.game_state.player_rect.y = 0

        # did the player run into any walls?
        for wall in self.walls:
            if self.game_state.player_rect.colliderect(wall.wall_rect):
                if self.move_x > 0: # collide right
                    self.game_state.player_rect.x = wall.wall_rect.x - self.game_state.player_rect.width
                    self.game_state.hit_wall = True
                elif self.move_x < 0: # collide left
                    self.game_state.player_rect.x = wall.wall_rect.x + wall.wall_rect.width
                    self.game_state.hit_wall = True
                elif self.move_y < 0: # collide up
                    self.game_state.player_rect.y = wall.wall_rect.y + wall.wall_rect.height
                    self.game_state.hit_wall = True
                elif self.move_y > 0: # collide down
                    self.game_state.player_rect.y = wall.wall_rect.y - self.game_state.player_rect.height
                    self.game_state.hit_wall = True

        self.move_walls()
        self.move_goal()

        # did any walls run into the player
        for wall in self.walls:
            if self.game_state.player_rect.colliderect(wall.wall_rect):
                self.game_state.player_rect.y = wall.wall_rect.y + wall.wall_rect.height
                self.game_state.hit_wall = True

        # did the player get to the goal
        if self.game_state.game_status == GameStatus.ACTIVE and self.game_state.player_rect.colliderect(self.game_state.goal.goal_rect):
            self.game_state.game_status = GameStatus.LEVEL_WON
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self.hit_wall_sound_channel.stop()
            self.victory_sound.play(0)

        # check if the player is damaged or killed
        if self.game_state.game_status == GameStatus.ACTIVE and (self.game_state.player_rect.y + self.game_state.player_rect.height) >= (self.game_state.game_height - 3):
            self.game_state.player_health -= FIRE_DAMAGE_PER_TICK
            self.game_state.player_frying = True
            if self.game_state.player_health <= 0:
                self.game_state.game_status = GameStatus.PLAYER_DEAD
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                if self.egg_fry_sound_channel:
                    self.egg_fry_sound_channel.stop()
                if self.hit_wall_sound_channel:
                    self.hit_wall_sound_channel.stop()
                self.death_sound.play(0)

    def translate_x(self, x):
        return (x / self.game_state.game_width) * self.settings.display_width

    def translate_y(self, y):
        return (y / self.game_state.game_height) * self.settings.display_height

    def translate_rect(self, rect):
        return pygame.Rect(
            self.translate_x(rect.x),
            self.translate_y(rect.y),
            self.translate_x(rect.width),
            self.translate_y(rect.height),
        )
    
    def render(self):
        self.window.fill((0,0,0))

        # draw goal
        self.window.blit(self.goal_image, (
                self.translate_x(self.game_state.goal.goal_rect.x),
                self.translate_y(self.game_state.goal.y)
            )
        )

        # draw walls
        for wall in self.walls:
            pygame.draw.rect(
                self.window, 
                (0, 0, 255), 
                (
                    self.translate_x(wall.wall_rect.x),
                    self.translate_y(wall.y), # use the float y for smoother moving
                    self.translate_x(wall.wall_rect.width),
                    self.translate_y(wall.wall_rect.height)
                )
            )

        # display cooked value
        surface = self.text_font.render("Cooked", True, (255, 255, 255))
        self.window.blit(surface, (self.window.get_width() - surface.get_width() - 200, 10))
        pygame.draw.rect(
            self.window,
            pygame.Color(255, 0, 0),
            (
                self.window.get_width() - 188,
                12,
                176 * (400 - min(400, self.game_state.player_health)) / 400,
                surface.get_height() - 11
            )
        )
        pygame.draw.rect(
            self.window,
            pygame.Color("white"),
            (
                self.window.get_width() - 190,
                10,
                180,
                surface.get_height() - 8
            ),
            2
        )

        # display continue prompt if player wins the level
        if self.game_state.game_status == GameStatus.LEVEL_WON:
            pygame.draw.rect(self.window, 
                pygame.Color("brown"), 
                (230, 130, 540, 120)
            )
            surface = self.text_font.render("You escaped!", True, (0, 200, 0))
            x = (self.window.get_width() - surface.get_width()) // 2
            self.window.blit(surface, (x, 150))
            surface = self.text_font.render("Press any key to continue", True, (0, 200, 0))
            x = (self.window.get_width() - surface.get_width()) // 2
            self.window.blit(surface, (x, 200))

        # render fire along bottom of screen
        j = 0
        for i in range(12):
            self.window.blit(self.fire_images[(self.fire_counter + j) % 3], (i * 82, self.settings.display_height - 65))
            j += 1

        if self.game_state.game_status == GameStatus.ACTIVE and self.tick_num % 10 == 0 and not self.pause:
            self.fire_counter = (self.fire_counter + 1) % len(self.fire_images)

        # display continue prompt if player is dead
        if self.game_state.game_status == GameStatus.PLAYER_DEAD:
            x = self.translate_x(self.game_state.player_rect.x)
            y = self.translate_y(self.game_state.player_rect.y) - 20
            self.window.blit(self.blood_splat, (x - 50, self.settings.display_height - 200))

            pygame.draw.rect(self.window, 
                pygame.Color("cadetblue3"), 
                (300, 130, 400, 120)
            )
            surface = self.text_font.render("You died. :(", True, (200, 0, 0))
            x = (self.window.get_width() - surface.get_width()) // 2
            self.window.blit(surface, (x, 150))
            surface = self.text_font.render("Try Again? (y/n)", True, (200, 0, 0))
            x = (self.window.get_width() - surface.get_width()) // 2
            self.window.blit(surface, (x, 200))

        # frying pan
        pan_x = self.translate_x(self.game_state.player_rect.x - 6)
        pan_y = self.settings.display_height - 125
        self.window.blit(self.game_state.pan_image, (pan_x, pan_y))

        # draw alive player
        if self.game_state.game_status == GameStatus.COUNTDOWN or self.game_state.game_status == GameStatus.ACTIVE or self.game_state.game_status == GameStatus.LEVEL_WON:
            temp_rect = self.translate_rect(self.game_state.player_rect)
            self.window.blit(self.game_state.player_image, (temp_rect.x, temp_rect.y))

        # draw dead player
        if self.game_state.game_status == GameStatus.PLAYER_DEAD:
            x = self.translate_x(self.game_state.player_rect.x)
            self.window.blit(self.game_state.dead_image, (x, self.settings.display_height - 70))

        # check countdown
        if self.game_state.game_status == GameStatus.COUNTDOWN:
            self.game_state.countdown_timer += 1
            if self.game_state.countdown_timer < 100:
                surface = self.countdown_font.render("Ready.", True, (0, 255, 0))
                x = (self.window.get_width() - surface.get_width()) // 2
                self.window.blit(surface, (x, 160))
            elif self.game_state.countdown_timer < 200:
                surface = self.countdown_font.render("Set.", True, (0, 255, 0))
                x = (self.window.get_width() - surface.get_width()) // 2
                self.window.blit(surface, (x, 160))
            elif self.game_state.countdown_timer < 300:
                surface = self.countdown_font.render("Go!!!", True, (0, 255, 0))
                x = (self.window.get_width() - surface.get_width()) // 2
                self.window.blit(surface, (x, 160))
            else:
                self.game_state.game_status = GameStatus.ACTIVE
                pygame.mixer.music.play(-1)

        pygame.display.update()

        self.tick_num = (self.tick_num + 1) % 60

        # player wall collision sound
        # if not self.egg_roll_sound_channel or not self.egg_roll_sound_channel.get_busy():
        if self.game_state.game_status == GameStatus.ACTIVE and self.game_state.hit_wall and not self.pause and not self.game_state.player_frying:
            self.hit_wall_sound_channel = self.hit_wall_sound.play(0, 100)
        
        if self.game_state.game_status == GameStatus.ACTIVE and self.game_state.player_frying and not self.pause:
            if not self.egg_fry_sound_channel or not self.egg_fry_sound_channel.get_busy():
                self.egg_fry_sound_channel = self.egg_fry_sound.play(0)

    def play_game(self):
        self.init_game()
        
        while self.game_state.game_status != GameStatus.INACTIVE:
            self.process_input()

            if not self.pause:
                if self.game_state.game_status == GameStatus.ACTIVE:
                    self.update_state()
                                
            self.render()
            self.clock.tick(60)

    def run(self):
        while self.running:
            self.play_game()
            self.running = self.continue_game
