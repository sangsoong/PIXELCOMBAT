import math
import pygame
import sys
import random

# ======================================== class ========================================

class Floor:
    def __init__(self, image):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()

    def re_pos(self):
        if self.rect.x < -10:
            self.rect.x += 20 + WIDTH
        if self.rect.x > WIDTH + 10:
            self.rect.x -= 20 + WIDTH
        if self.rect.y < -10:
            self.rect.y += 20 + HEIGHT
        if self.rect.y > HEIGHT + 10:
            self.rect.y -= 20 + HEIGHT

    def draw(self):
        L_Floor.blit(self.image, self.rect)

class Player:
    def __init__(self, image, x, y):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
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
        for objects in relative_objects:
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
            ran_y = -10 if random.randint(1, 2) == 1 else HEIGHT + 10
        else:
            ran_x = -10 if random.randint(1, 2) == 1 else WIDTH + 10
            ran_y = random.randint(0, HEIGHT)

        if cls.summon_delay - (current_sec % cls.summon_delay) - 0.1 < 0:
            if cls.summon_onoff:
                enemies.append(Enemy(ENEMY, ran_x, ran_y))
                cls.summon_onoff = False
        else:
            cls.summon_onoff = True

    def __init__(self, image, x, y):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2

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

# initialize
pygame.init()

# fps
CLOCK = pygame.time.Clock()

# time
ENTER_TICK = pygame.time.get_ticks()
current_tick = 0

# display
WIDTH = 800
HEIGHT = 800
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Title")
SCREEN.fill((255, 255, 255))

# layer
layers = []
L_Floor = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA).convert_alpha()
L_Enemy = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA).convert_alpha()
L_Player = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA).convert_alpha()

layers.append(L_Floor)
layers.append(L_Enemy)
layers.append(L_Player)

# sprite
GROUND = "sprites/ground.png"
PLAYER = "sprites/player.png"
ENEMY = "sprites/enemy.png"

# object
floors = []
movable_objects = []
relative_objects = []

'''
for i in range(-2, 3):
    for j in range(-2, 3):
        floor = Floor(GROUND)
        floor.rect.center = ((WIDTH/4)*i, (HEIGHT/4)*j)
        floors.append(floor)
'''
player = Player(PLAYER, WIDTH / 2, HEIGHT / 2)
enemies = []

movable_objects.append([player])
movable_objects.append(enemies)
movable_objects.append(floors)
relative_objects.append(enemies)
relative_objects.append(floors)

# ======================================== main ========================================

def main():
    run = True
    while run:
        # ==================== setting ====================

        # time
        current_tick = pygame.time.get_ticks() - ENTER_TICK
        current_sec = current_tick / 1000

        # reset screen
        for layer in layers:
            layer.fill((0, 0, 0, 0))

        # ==================== event ====================

        # event check
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                player.move_to(event.key, 1)
            if event.type == pygame.KEYUP:
                player.move_to(event.key, 0)

        # floor
        #for floor in floors:
        #    floor.re_pos()

        # enemy
        Enemy.summon(current_sec)
        for enemy in enemies:
            enemy.move(player)

        # player
        player.move()

        # ==================== update ====================

        # update screen
        for objects in movable_objects:
            for object in objects:
                object.draw()
        for layer in layers:
            SCREEN.blit(layer, (0, 0))
        pygame.display.update()
        CLOCK.tick(60)

# ======================================== run ========================================

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
