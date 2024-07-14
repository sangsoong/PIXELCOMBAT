import pygame, sys, random

# ======================================== setting ========================================

# initialize
pygame.init()

# fps
clock = pygame.time.Clock()

# time
enter_tick = pygame.time.get_ticks()
current_tick = 0

# display
WIDTH = 800
HEIGHT = 800
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Title")
SCREEN.fill((255, 255, 255))

# ======================================== class ========================================

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
        self.speed = 5

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
        self.rect.y += self.dir_up
        self.rect.x += self.dir_left
        self.rect.y += self.dir_down
        self.rect.x += self.dir_right
        '''
        if pygame.sprite.collide_mask(self, enemy):
            self.rect.y -= self.dir_up
            self.rect.x -= self.dir_left
            self.rect.y -= self.dir_down
            self.rect.x -= self.dir_right
        '''
        self.update()

    def update(self):
        SCREEN.blit(self.image, self.rect)

class Enemy:
    def __init__(self, image, x, y):
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1.5

    def move(self, target):
        if self.rect.y < target.rect.y:
            self.rect.y += self.speed
        if self.rect.y > target.rect.y:
            self.rect.y -= self.speed
        if self.rect.x < target.rect.x:
            self.rect.x += self.speed
        if self.rect.x > target.rect.x:
            self.rect.x -= self.speed

        if random.randint(0, 1) == 1:
            self.rect.y += self.speed / 3
        else:
            self.rect.y -= self.speed / 3
        if random.randint(0, 1) == 1:
            self.rect.x += self.speed / 3
        else:
            self.rect.x -= self.speed / 3

        self.update()

    def update(self):
        SCREEN.blit(self.image, self.rect)

# ======================================== main ========================================

def main():
    # initialize
    player = Player("sprites/player.png", WIDTH/2, HEIGHT/2)
    enemies = []
    enemy_summon_delay = 1.5   # must be greater than 1
    enemy_summon_onoff = False

    # repeat(main)
    run = True
    while run:
        # ==================== setting ====================

        # time
        current_tick = pygame.time.get_ticks() - enter_tick
        current_time = current_tick / 1000

        # reset screen
        SCREEN.fill((255, 255, 255))

        # ==================== event ====================

        # event check
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                player.move_to(event.key, 1)
            if event.type == pygame.KEYUP:
                player.move_to(event.key, 0)

        # enemy
        if enemy_summon_delay - (current_time % enemy_summon_delay) - 0.1 < 0:
            if enemy_summon_onoff:
                if random.randint(1, 2) == 1:
                    ran_x = random.randint(0, WIDTH)
                    ran_y = -10 if random.randint(1, 2) == 1 else HEIGHT + 10
                else:
                    ran_x = -10 if random.randint(1, 2) == 1 else WIDTH + 10
                    ran_y = random.randint(0, HEIGHT)
                enemies.append(Enemy("sprites/enemy.png", ran_x, ran_y))
                enemy_summon_onoff = False
        else:
            enemy_summon_onoff = True

        for enemy in enemies:
            enemy.move(player)

        # player
        player.move()

        # ==================== update ====================

        # update screen
        pygame.display.flip()
        clock.tick(60)

# ======================================== run ========================================

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
