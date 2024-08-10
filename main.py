import math
from turtle import screensize
import pygame
import sys
import random

from paths import *

# ================================================== classes ========================================

class Text:
    def __init__(self, text, color=(0, 0, 0), pos=(0, 0), size=10, font=None):
        self.rawtext = text
        self.rawcolor = color
        self.rawsize = size
        self.font = pygame.font.Font(font, size)
        self.text = self.font.render(text, False, color)
        self.rect = self.text.get_rect(center=pos)
    
    def write(self, text):
        self.text = self.font.render(text, False, self.rawcolor)
        self.rect = self.text.get_rect(center=self.rect.center)
    
    def goto(self, pos):
        self.rect.center = pos

    def draw(self, win):
        win.blit(self.text, self.rect)

class Image:
    def __init__(self, image, pos, size):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=pos)

    def goto(self, pos):
        self.rect.center = pos

    def draw(self, win):
        win.blit(self.image, self.rect)

class Background(Image):
    def __init__(self, image):
        super().__init__(image, (WIDTH/2, HEIGHT/2), (WIDTH, HEIGHT))

class Button(Image):
    def __init__(self, image, hov_image, pos, size):
        super().__init__(image, pos, size)
        self.hov_image = pygame.image.load(hov_image).convert_alpha()
        self.hov_image = pygame.transform.scale(self.hov_image, size)
        self.hov_rect = self.hov_image.get_rect(center=pos)

    def goto(self, pos):
        super().goto(pos)
        self.hov_rect.center = pos
    
    def draw(self, win):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            win.blit(self.hov_image, self.rect)
        else:
            win.blit(self.image, self.rect)

class Structure(Image):
    def __init__(self, image, pos, size):
        super().__init__(image, pos, size)

class Entity(Image):
    def __init__(self, image, pos, size):
        super().__init__(image, pos, size)

class Player(Entity):
    def __init__(self, pos, size):
        super().__init__(START_PLAYER, pos, size)
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
        for objects in running_collidable_objects:
            for object in objects:
                if pygame.sprite.collide_mask(self.image, object.image):
                    return False
        self.rect.y += self.dir_up
        self.rect.x += self.dir_left
        self.rect.y += self.dir_down
        self.rect.x += self.dir_right

class Enemy1(Entity):
    def __init__(self, x, y):
        super().__init__(START_ENEMY1, x, y)

class Logic:
    mode = "main"
    cur_tick = 0
    intro_time = 0

    @classmethod
    def start(cls):
        run = True
        while run:
            CLOCK.tick(60)
            cls.cur_tick = pygame.time.get_ticks() - ENTER_TICK
            SCREEN.fill((255, 255, 255))
            layers[cls.mode].fill((0, 0, 0, 0))

            if cls.mode == "main":
                run = cls.main()
            elif cls.mode == "intro":
                run = cls.intro()
            elif cls.mode == "running":
                run = cls.running()
            elif cls.mode == "gameover":
                run = cls.gameover()
            
            SCREEN.blit(layers[cls.mode], (0, 0))
            pygame.display.update()
        pygame.quit()
    
    @classmethod
    def main(cls):
        main_background.draw(L_MAIN)
        main_start.draw(L_MAIN)
        main_exit.draw(L_MAIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if main_start.rect.collidepoint(event.pos):
                    cls.mode = "intro"
                    return True
                if main_exit.rect.collidepoint(event.pos):
                    return False
        return True

    @classmethod
    def intro(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        intro_percentage.write(f"{cls.intro_time}%")
        intro_loading.draw(L_INTRO)
        intro_percentage.draw(L_INTRO)
        cls.intro_time += 2
        if cls.intro_time > 100:
            cls.mode = "running"
        return True
    
    @classmethod
    def running(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        return True

    @classmethod
    def gameover(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        cls.mode = "main"
        return True

# ================================================== variables ==================================================

pygame.init()

CLOCK = pygame.time.Clock()
ENTER_TICK = pygame.time.get_ticks()

WIDTH = 800
HEIGHT = 800
CENTER = (WIDTH/2, HEIGHT/2)
SIZE = (WIDTH, HEIGHT)
SCREEN = pygame.display.set_mode(SIZE)
pygame.display.set_caption("hackAslash")
SCREEN.fill((255, 255, 255))
pygame.display.update()

L_MAIN = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
L_INTRO = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_RUNNING = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_GAMEOVER = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
layers = {"main": L_MAIN,
          "intro": L_INTRO,
          "running": L_RUNNING,
          "gameover": L_GAMEOVER}

main_background = Background(MAIN_BACKGROUND)
main_start = Button(MAIN_START, MAIN_START_HOVER, (WIDTH*1/2, HEIGHT*8/10), (200, 70))
main_exit = Button(MAIN_EXIT, MAIN_EXIT_HOVER, (WIDTH*1/2, HEIGHT*9/10), (200, 70))

intro_loading = Image(EFFECT_BLACK, CENTER, SIZE)
intro_percentage = Text("", (255, 255, 255), CENTER, 30)

running_wall = Structure(START_WALL, CENTER, SIZE)
running_floor = Background(START_FLOOR)
running_player = Player(CENTER, (100, 100))
running_enemies = []
running_collidable_objects = [running_enemies]

# ======================================== run ========================================
if __name__ == "__main__":
    Logic.start()
    sys.exit()
