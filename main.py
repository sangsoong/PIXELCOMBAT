import math
import pygame
import sys
import random

from paths import *

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

class Effect:
    def __init__(self, image, x, y, w, h):
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
        self.rect.center = (self.rect.x, self.rect.y)

    def re_pos(self):
        if self.rect.x <= WIDTH * (-0.5):
            self.rect.x = WIDTH - 5
        if self.rect.x > WIDTH:
            self.rect.x = WIDTH * (-0.5) + 5
        if self.rect.y <= HEIGHT * (-0.5):
            self.rect.y = HEIGHT - 5
        if self.rect.y > HEIGHT:
            self.rect.y = HEIGHT * (-0.5) + 5

    def draw(self):
        L_Floor.blit(self.image, self.rect)

class Player:
    def __init__(self, x, y):
        self.image_seq = 0
        self.image_mode = "idle"
        self.image = pygame.image.load(START_PLAYER_IDLE1).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=(WIDTH/2, HEIGHT/2))
        self.dir_up = 0
        self.dir_left = 0
        self.dir_down = 0
        self.dir_right = 0
        self.speed = 3

    def adjust_image(self, image, last_center):
        self.image = image
        self.rect = self.image.get_rect(center=last_center)

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
        cof = 1
        for objects in start_nonplayer_moving_objects:
            for object in objects:
                if objects in start_collidable_objects and pygame.sprite.collide_mask(self, object):
                    cof = 0.7
                    break
        for objects in start_nonplayer_moving_objects:
            for object in objects:
                object.rect.y -= self.dir_up * cof
                object.rect.x -= self.dir_left * cof
                object.rect.y -= self.dir_down * cof
                object.rect.x -= self.dir_right * cof

    def draw(self):
        if self.dir_up == 0 and self.dir_left == 0 and self.dir_down == 0 and self.dir_right == 0:
            start_player.image_mode = "idle"
        elif self.dir_up == -1*self.speed or self.dir_left == -1*self.speed or self.dir_right == -1*self.speed or self.dir_left == -1*self.speed:
            start_player.image_mode = "walk"
        self.image_seq += 1
        path = ""
        if self.image_mode == "idle":
            if self.image_seq >= len(START_PLAYER_IDLE)*10:
                self.image_seq = 0
            path = START_PLAYER_IDLE[self.image_seq // 10]
        elif self.image_mode == "walk":
            if self.image_seq >= len(START_PLAYER_WALK)*10:
                self.image_seq = 0
            path = START_PLAYER_WALK[self.image_seq // 10]
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (100, 100))
        self.adjust_image(image, self.rect.center)
        
        # 마우스 보기
        rel_x = pygame.mouse.get_pos()[0] - self.rect.centerx
        rel_y = self.rect.centery - pygame.mouse.get_pos()[1]
        angle = (180/math.pi) * math.atan2(rel_y, rel_x) + 90
        self.image = pygame.transform.rotate(self.image, angle)

        L_Player.blit(self.image, self.rect)

class Enemy:
    names = ["zombie1"]
    summon_delay = {"zombie1": 1.5,  # must be greater than 1
                    "none": 0}
    summon_onoff = {"zombie1": False,
                    "none": False}

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

        for name in cls.names:
            if cls.summon_delay[name] - (current_sec % cls.summon_delay[name]) - 0.1 < 0:
                if cls.summon_onoff[name]:
                    start_enemies.append(Enemy(ran_x, ran_y, name))
                    cls.summon_onoff[name] = False
            else:
                cls.summon_onoff[name] = True

    def __init__(self, x, y, name):
        self.image_seq = 0
        self.image_mode = "run"
        self.image = pygame.image.load(EFFECT_BLACK).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.name = name
        if name == "zombie1":
            self.speed = 1
        elif name == "none":
            self.speed = 2

    def move(self, target):
        off_x = target.rect.centerx - self.rect.centerx
        off_y = target.rect.centery - self.rect.centery
        dist = math.sqrt(off_x*off_x + off_y*off_y)
        if dist != 0:
            cos = off_x / dist
            sin = off_y / dist
            speed_x = cos * self.speed
            speed_y = sin * self.speed

            self.rect.centerx += speed_x
            self.rect.centery += speed_y
            if pygame.sprite.collide_mask(self, target):
                self.rect.centerx -= speed_x
                self.rect.centery -= speed_y
    
    def adjust_image(self, image, last_center):
        self.image = image
        self.rect = self.image.get_rect(center=last_center)

    def draw(self):
        self.image_seq += 1
        path = ""
        if self.name == "zombie1":
            if self.image_mode == "idle":
                if self.image_seq >= len(START_ENEMY1_IDLE)*10:
                    self.image_seq = 0
                path = START_ENEMY1_IDLE[self.image_seq // 10]
            elif self.image_mode == "run":
                if self.image_seq >= len(START_ENEMY1_WALK)*10:
                    self.image_seq = 0
                path = START_ENEMY1_WALK[self.image_seq // 10]
        
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (100, 100))
        self.adjust_image(image, self.rect.center)

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

# ========== layer ==========
layers = {}
L_Effect = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
L_Menu = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_Intro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_Floor = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
L_Enemy = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
L_Player = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)

layers[0] = [L_Menu, L_Effect]
layers[1] = [L_Floor, L_Enemy, L_Player, L_Effect]

# ========== sprite ==========
# effect
effect_black = pygame.image.load(EFFECT_BLACK).convert_alpha()
effect_fog = pygame.image.load(EFFECT_FOG).convert_alpha()

# menu
menu_background = pygame.image.load(MENU_BACKGROUND).convert_alpha()
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
menu_effects = []
for i in range(0, 5):
    ran_x = random.randint(WIDTH, WIDTH+2000)
    ran_y = random.randint(int(HEIGHT*(1/10)), int(HEIGHT*(9/10)))
    menu_effect = Effect(EFFECT_BLACK, ran_x, ran_y, 1000, 5)
    menu_effects.append(menu_effect)
menu_start = Button("menu_start", MENU_START, WIDTH*1/10, HEIGHT*8/10, 100, 50)
menu_exit = Button("menu_exit", MENU_EXIT, WIDTH*1/10, HEIGHT*9/10, 100, 50)

# start
start_floors = []
for i in range(0, 3):
    for j in range(0, 3):
        floor = Floor(START_GROUND2)
        floor.rect.x = (WIDTH/2)*j
        floor.rect.y = (HEIGHT/2)*i
        start_floors.append(floor)
start_player = Player(WIDTH / 2, HEIGHT / 2)
start_enemies = []

start_nonplayer_moving_objects = [start_floors, start_enemies]
start_collidable_objects = [start_enemies]

start_fog = Effect(EFFECT_FOG, 0, 0, WIDTH, HEIGHT)

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
            if state == 0:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_start.rect.collidepoint(event.pos):
                        state = 1
                    if menu_exit.rect.collidepoint(event.pos):
                        run = False
            if state == 1:
                if event.type == pygame.KEYDOWN:
                    start_player.move_to(event.key, 1)
                if event.type == pygame.KEYUP:
                    start_player.move_to(event.key, 0)

        if state == 0:
            L_Menu.blit(menu_background, (0, 0))
            menu_start.draw(L_Menu)
            menu_exit.draw(L_Menu)

            # button hover check
            if menu_start.rect.collidepoint(pygame.mouse.get_pos()):
                menu_start.re_image(MENU_START_HOVER, menu_start.rect.x, menu_start.rect.y, menu_start.w, menu_start.h)
            else:
                menu_start.re_image(MENU_START, menu_start.rect.x, menu_start.rect.y, menu_start.w, menu_start.h)
            if menu_exit.rect.collidepoint(pygame.mouse.get_pos()):
                menu_exit.re_image(MENU_EXIT_HOVER, menu_exit.rect.x, menu_exit.rect.y, menu_exit.w, menu_exit.h)
            else:
                menu_exit.re_image(MENU_EXIT, menu_exit.rect.x, menu_exit.rect.y, menu_exit.w, menu_exit.h)

            # effect
            for menu_effect in menu_effects:
                if menu_effect.rect.x < -1000:
                    menu_effect.rect.x = random.randint(WIDTH, WIDTH+1000)
                    menu_effect.rect.y = random.randint(int(HEIGHT*(1/20)), int(HEIGHT*(19/20)))
                else:
                    menu_effect.rect.x -= 15
                    menu_effect.draw(L_Effect)

        if state == 1:
            # floor
            for floor in start_floors:
                floor.re_pos()
                floor.draw()

            # enemy
            Enemy.summon(current_sec)
            for enemy in start_enemies:
                enemy.move(start_player)
                enemy.draw()

            # player
            start_player.move()
            start_player.draw()

            # effect
            start_fog.draw(L_Effect)

        if state == 2:
            pass

        # ========== update ==========
        # update layer
        for key, value in layers.items():
            if key == state:
                for layer in value:
                    SCREEN.blit(layer, (0, 0))
        # intro
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
