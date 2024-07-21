import math
import pygame
import sys
import random

# ======================================== class ========================================

class Button:
    def __init__(self, name, image, x, y, w, h):
        self.name = name
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (w, h))
        self.w = w
        self.h = h
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def re_image(self, image, x, y, w, h):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (w, h))
        self.w = w
        self.h = h
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, win):
        win.blit(self.image, self.rect)

class Floor:
    def __init__(self, image):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (410, 410))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def re_pos(self):
        if self.rect.x <= WIDTH * (-0.5):
            self.rect.x = WIDTH
        if self.rect.x > WIDTH:
            self.rect.x = WIDTH * (-0.5)
        if self.rect.y <= HEIGHT * (-0.5):
            self.rect.y = HEIGHT
        if self.rect.y > HEIGHT:
            self.rect.y = HEIGHT * (-0.5)

    def draw(self):
        L_Floor.blit(self.image, self.rect)

class Player:
    def __init__(self, image, x, y):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.center = (x, y)
        self.dir_up = 0
        self.dir_left = 0
        self.dir_down = 0
        self.dir_right = 0
        self.speed = 3

    def move_to(self, key, push):
        if key == pygame.K_w:
            self.dir_up = push * -1 * self.speed
        elif key == pygame.K_a:
            self.dir_left = push * -1 * self.speed
        elif key == pygame.K_s:
            self.dir_down = push * 1 * self.speed
        elif key == pygame.K_d:
            self.dir_right = push * 1 * self.speed

    def move(self):
        for objects in nonplayer_moving_objects:
            for object in objects:
                object.rect.y -= self.dir_up
                object.rect.x -= self.dir_left
                object.rect.y -= self.dir_down
                object.rect.x -= self.dir_right

        '''
        for objects in self.collides:
            for object in objects:
                if pygame.sprite.collide_mask(self, object):
                    self.rect.y -= self.dir_up
                    self.rect.x -= self.dir_left
                    self.rect.y -= self.dir_down
                    self.rect.x -= self.dir_right
        '''

    def draw(self):
        L_Player.blit(self.image, self.rect)

class Enemy:
    summon_delay = 1.5  # must be greater than 1
    summon_onoff = False

    @classmethod
    def summon(cls, current_sec):
        ran_x = 0
        ran_y = 0
        if random.randint(1, 2) == 1:
            ran_x = random.randint(0, WIDTH)
            ran_y = -50 if random.randint(1, 2) == 1 else HEIGHT + 50
        else:
            ran_x = -50 if random.randint(1, 2) == 1 else WIDTH + 50
            ran_y = random.randint(0, HEIGHT)

        if cls.summon_delay - (current_sec % cls.summon_delay) - 0.1 < 0:
            if cls.summon_onoff:
                enemies.append(Enemy(START_ENEMY, ran_x, ran_y))
                cls.summon_onoff = False
        else:
            cls.summon_onoff = True

    def __init__(self, image, x, y):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.center = (x, y)
        self.speed = 1

    def move(self, target):
        off_x = target.rect.x - self.rect.x
        off_y = target.rect.y - self.rect.y
        dist = math.sqrt(off_x*off_x + off_y*off_y)
        if dist != 0:
            cos = off_x / dist
            sin = off_y / dist
            speed_x = cos * self.speed
            speed_y = sin * self.speed

            self.rect.x += speed_x
            self.rect.y += speed_y
            if pygame.sprite.collide_mask(self, target):
                self.rect.x -= speed_x
                self.rect.y -= speed_y

    def draw(self):
        L_Enemy.blit(self.image, self.rect)

# ======================================== setting ========================================

# ========== initialize ==========
pygame.init()

# ========== time ==========
CLOCK = pygame.time.Clock()
ENTER_TICK = pygame.time.get_ticks()
current_tick = 0

# ========== screen ==========
WIDTH = 800
HEIGHT = 800
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("hackAslash")
SCREEN.fill((255, 255, 255))
pygame.display.update()

# ========== path ==========
MENU_BACKGROUND = "sprites/menu_background.png"
MENU_START = "sprites/menu_start.png"
MENU_START_HOVER = "sprites/menu_start_hover.png"
MENU_EXIT = "sprites/menu_exit.png"
MENU_EXIT_HOVER = "sprites/menu_exit_hover.png"
START_GROUND = "sprites/start_ground.png"
START_PLAYER = "sprites/start_player.png"
START_ENEMY = "sprites/start_enemy.png"

# ========== layer ==========
layers = {}
L_Menu = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_Intro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_Floor = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
L_Enemy = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
L_Player = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)

layers[0] = [L_Menu]
layers[1] = [L_Floor, L_Enemy, L_Player]

# ========== sprite ==========
# menu
menu_background = pygame.image.load(MENU_BACKGROUND).convert_alpha()
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
menu_start = Button("menu_start", MENU_START, WIDTH*1/10, HEIGHT*8/10, 100, 50)
menu_exit = Button("menu_exit", MENU_EXIT, WIDTH*1/10, HEIGHT*9/10, 100, 50)

# start
floors = []
for i in range(0, 3):
    for j in range(0, 3):
        floor = Floor(START_GROUND)
        floor.rect.x = (WIDTH/2)*j
        floor.rect.y = (HEIGHT/2)*i
        floors.append(floor)
player = Player(START_PLAYER, WIDTH / 2, HEIGHT / 2)
enemies = []

movable_objects = []
movable_objects.append([player])
movable_objects.append(enemies)
movable_objects.append(floors)

nonplayer_moving_objects = []
nonplayer_moving_objects.append(enemies)
nonplayer_moving_objects.append(floors)

# end

# ======================================== main ========================================

def main():
    state = 0
    intro = 255

    run = True
    while run:
        # ========== setting ==========
        # time
        current_tick = pygame.time.get_ticks() - ENTER_TICK
        current_sec = current_tick / 1000

        # reset screen
        SCREEN.fill((255, 255, 255))
        for key, value in layers.items():
            if key == state:
                for layer in value:
                    layer.fill((0, 0, 0, 0))

        # ========== event ==========
        # event check
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_start.rect.collidepoint(event.pos):
                    state = 1
                if menu_exit.rect.collidepoint(event.pos):
                    run = False
            if event.type == pygame.KEYDOWN:
                player.move_to(event.key, 1)
            if event.type == pygame.KEYUP:
                player.move_to(event.key, 0)

        # button hover check
        if menu_start.rect.collidepoint(pygame.mouse.get_pos()):
            menu_start.re_image(MENU_START_HOVER, menu_start.rect.x, menu_start.rect.y, menu_start.w, menu_start.h)
        else:
            menu_start.re_image(MENU_START, menu_start.rect.x, menu_start.rect.y, menu_start.w, menu_start.h)
        if menu_exit.rect.collidepoint(pygame.mouse.get_pos()):
            menu_exit.re_image(MENU_EXIT_HOVER, menu_exit.rect.x, menu_exit.rect.y, menu_exit.w, menu_exit.h)
        else:
            menu_exit.re_image(MENU_EXIT, menu_exit.rect.x, menu_exit.rect.y, menu_exit.w, menu_exit.h)

        # menu : 0
        if state == 0:
            L_Menu.blit(menu_background, (0, 0))
            menu_start.draw(L_Menu)
            menu_exit.draw(L_Menu)

        # start : 1
        if state == 1:
            # floor
            for floor in floors:
                floor.re_pos()

            # enemy
            Enemy.summon(current_sec)
            for enemy in enemies:
                enemy.move(player)

            # player
            player.move()

        # end : 2
        if state == 2:
            pass

        # ========== update ==========
        # update screen
        for objects in movable_objects:
            for object in objects:
                object.draw()
        for key, value in layers.items():
            if key == state:
                for layer in value:
                    SCREEN.blit(layer, (0, 0))
        if state == 1 and intro:    # intro
            L_Intro.fill((0, 0, 0, intro))
            SCREEN.blit(L_Intro, (0, 0))
            intro -= 5

        pygame.display.update()
        CLOCK.tick(60)

# ======================================== run ========================================

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
