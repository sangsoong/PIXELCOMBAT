import pygame
import sys
import math
import random

from paths import *

# ================================================== initialize ==================================================

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

PLAYER_SIZE = (WIDTH/16, HEIGHT/16)
ENEMY_SIZE = (WIDTH/16, HEIGHT/16)
VER_DOOR_SIZE = (WIDTH*(3/64)*(115/100), HEIGHT*(10/64)*(115/100))
HOR_DOOR_SIZE = (WIDTH*(10/64)*(115/100), HEIGHT*(3/64)*(115/100))
off_x = HOR_DOOR_SIZE[0]*0.5
off_y = VER_DOOR_SIZE[1]*0.5
DOOR_POS_UP = (WIDTH/2, off_y)
DOOR_POS_LEFT = (off_x, HEIGHT/2)
DOOR_POS_DOWN = (WIDTH/2, HEIGHT-off_y)
DOOR_POS_RIGHT = (WIDTH-off_x, HEIGHT/2)

L_MAIN = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
L_INTRO = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_RUNNING = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
L_GAMEOVER = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
layers = {"main": L_MAIN,
          "intro": L_INTRO,
          "running": L_RUNNING,
          "gameover": L_GAMEOVER}

# ================================================== classes ==================================================

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
    def __init__(self, path, pos, size):
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def goto(self, pos):
        self.rect.center = pos

    def draw(self, win):
        win.blit(self.image, self.rect)

class Background(Image):
    def __init__(self, path):
        super().__init__(path, (WIDTH/2, HEIGHT/2), (WIDTH, HEIGHT))

class Button(Image):
    def __init__(self, path, hov_path, pos, size):
        super().__init__(path, pos, size)
        self.hov_image = pygame.image.load(hov_path).convert_alpha()
        self.hov_image = pygame.transform.scale(self.hov_image, size)
        self.hov_rect = self.hov_image.get_rect(center=pos)
        self.hov_mask = pygame.mask.from_surface(self.hov_image)

    def goto(self, pos):
        super().goto(pos)
        self.hov_rect.center = pos
    
    def draw(self, win):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            win.blit(self.hov_image, self.rect)
        else:
            win.blit(self.image, self.rect)

class Structure(Image):
    def __init__(self, path, pos, size):
        super().__init__(path, pos, size)

class Entity(Image):
    def __init__(self, room, path, pos, size):
        self.room = room
        super().__init__(path, pos, size)

class Player(Entity):
    def __init__(self, room, pos, size):
        super().__init__(room, WRK_PLAYER, pos, size)
        self.dir_up = 0
        self.dir_left = 0
        self.dir_down = 0
        self.dir_right = 0
        self.speed = 5

    def move_dir(self, key, push):
        directions = [(pygame.K_w, "dir_up", -1), (pygame.K_a, "dir_left", -1), (pygame.K_s, "dir_down", 1), (pygame.K_d, "dir_right", 1)]
        for k, direction, w in directions:
            if key == k:
                self.__setattr__(direction, push * w * self.speed)
            
    def move(self):
        directions = [(self.dir_up, "centery"), (self.dir_left, "centerx"), (self.dir_down, "centery"), (self.dir_right, "centerx")]
        for direction, axis in directions:
            self.rect.__setattr__(axis, self.rect.__getattribute__(axis) + direction)
            for objects in Logic.wkg_colliders:
                for object in objects:
                    if pygame.sprite.collide_mask(object, self):
                        self.rect.__setattr__(axis, self.rect.__getattribute__(axis) - direction)
                        break
    
    def room_to(self):
        for side, door in self.room.door.items():
            if door != 0 and pygame.sprite.collide_mask(self, door):
                room = self.room.side[side]
                self.room = room
                if door.rect.centery < CENTER[1] - 10:
                    self.goto((self.rect.centerx, DOOR_POS_DOWN[1] - (HOR_DOOR_SIZE[1])))
                elif door.rect.centerx < CENTER[0] - 10:
                    self.goto((DOOR_POS_RIGHT[0] - (VER_DOOR_SIZE[0]), self.rect.centery))
                elif door.rect.centery > CENTER[1] + 10:
                    self.goto((self.rect.centerx, DOOR_POS_UP[1] + (HOR_DOOR_SIZE[1])))
                elif door.rect.centerx > CENTER[0] + 10:
                    self.goto((DOOR_POS_LEFT[0] + (VER_DOOR_SIZE[0]) + 1, self.rect.centery))
                break

class Enemy1(Entity):
    def __init__(self, path, room, pos, size):
        super().__init__(path, room, pos, size)
        Logic.wkg_enemies.append(self)

class Room:
    def __init__(self, pos, type):
        paths = [(WRK_WALL1, WRK_FLOOR1), (WRK_WALL1, WRK_FLOOR1), (WRK_WALL1, WRK_FLOOR1)]
        self.wall = Structure(paths[type][0], CENTER, SIZE)
        self.floor = Background(paths[type][1])
        self.pos = pos
        self.type = type
        self.side = {"up": 0,
                    "left": 0,
                    "down": 0,
                    "right": 0}
        self.door = {"up": 0,
                     "left": 0,
                     "down": 0,
                     "right": 0}

    def generate(self):
        room_cnt = Dungeon.room_cnt
        map_size = Dungeon.map_size
        rooms = Dungeon.rooms
        rooms_pos = Dungeon.rooms_pos
        x, y = self.pos
        dirs1 = [(x, y+1), (x-1, y), (x, y-1), (x+1, y)]
        dirs2 = [(y, map_size[1]-1), (x, 0), (y, 0), (x, map_size[0]-1)]
        dirs3 = ["up", "left", "down", "right"]
        for i in range(0, 4):
            if random.randint(0, 2):
                if len(rooms) < room_cnt:
                    if dirs2[i][0] != dirs2[i][1]:
                        if dirs1[i] not in rooms_pos or len(rooms) == 1:
                            newroom = self.side[dirs3[i]] = Room(dirs1[i], 2)
                            self.side[dirs3[i]] = newroom
                            newroom.side[dirs3[(i+2)%4]] = self
                            rooms.append(newroom)
                            rooms_pos.append(dirs1[i])
    
    def set_door(self):
        paths = [WRK_DOOR1, WRK_DOOR1, WRK_DOOR1]
        if self.side["up"]:
            self.door["up"] = Structure(paths[self.type], DOOR_POS_UP, (HOR_DOOR_SIZE))
        if self.side["left"]:
            self.door["left"] = Structure(paths[self.type], DOOR_POS_LEFT, (VER_DOOR_SIZE))
        if self.side["down"]:
            self.door["down"] = Structure(paths[self.type], DOOR_POS_DOWN, (HOR_DOOR_SIZE))
        if self.side["right"]:
            self.door["right"] = Structure(paths[self.type], DOOR_POS_RIGHT, (VER_DOOR_SIZE))

class Dungeon:
    map_size = [5, 5]
    floor = 0
    room_cnt = 0
    rooms = []
    rooms_pos = []

    @classmethod
    def initiaize(cls):
        cls.floor = 0
        cls.room_cnt = 0
        cls.rooms.clear()
        cls.rooms_pos.clear()

    @classmethod
    def next_floor(cls):
        cls.floor += 1
        cls.room_cnt = cls.floor + 4
        cls.rooms.clear()
        cls.rooms_pos.clear()
        cls.generate()
        walls = []
        for room in cls.rooms:
            walls.append(room.wall)
        Logic.wkg_colliders.append(walls)

    @classmethod
    def generate(cls):
        start_x = random.randint(0, cls.map_size[0]-1)
        start_y = random.randint(0, cls.map_size[1]-1)
        while True:
            cls.rooms.clear
            cls.rooms_pos.clear()
            start_room = Room((start_x, start_y), 0)
            cls.rooms.append(start_room)
            cls.rooms_pos.append(start_room.pos)
            for i in range(0, cls.room_cnt-1):
                if len(cls.rooms) == i:
                    break
                cls.rooms[i].generate()
                cls.rooms[i].set_door()
            if len(cls.rooms) == cls.room_cnt:
                break
        cls.rooms[-1].type = 1
        cls.rooms[-1].set_door()

class Logic:
    mode = "main"
    cur_tick = 0
    
    main_background = Background(MAIN_BACKGROUND)
    main_start = Button(MAIN_START, MAIN_START_HOVER, (WIDTH*1/2, HEIGHT*8/10), (200, 70))
    main_exit = Button(MAIN_EXIT, MAIN_EXIT_HOVER, (WIDTH*1/2, HEIGHT*9/10), (200, 70))
    
    intro_loading = Image(EFFECT_BLACK, CENTER, SIZE)
    intro_percentage = Text("", (255, 255, 255), CENTER, 30)
    intro_time = 0
    
    wkg_player = None
    wkg_enemies = []
    wkg_colliders = []

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
        cls.main_background.draw(L_MAIN)
        cls.main_start.draw(L_MAIN)
        cls.main_exit.draw(L_MAIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if cls.main_start.rect.collidepoint(event.pos):
                    cls.mode = "intro"
                    return True
                if cls.main_exit.rect.collidepoint(event.pos):
                    return False
        return True

    @classmethod
    def intro(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        cls.intro_percentage.write(f"{cls.intro_time}%")
        cls.intro_loading.draw(L_INTRO)
        cls.intro_percentage.draw(L_INTRO)
        cls.intro_time += 2
        if cls.intro_time > 100:
            cls.mode = "running"
            Dungeon.next_floor()
            cls.wkg_player = Player(Dungeon.rooms[0], CENTER, PLAYER_SIZE)
        return True
    
    @classmethod
    def running(cls):
        player = cls.wkg_player
        player.room.floor.draw(L_RUNNING)
        player.room.wall.draw(L_RUNNING)
        for door in player.room.door.values():
            if door != 0:
                door.draw(L_RUNNING)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                player.move_dir(event.key, 1)
            if event.type == pygame.KEYUP:
                player.move_dir(event.key, 0)
        player.move()
        player.room_to()
        player.draw(L_RUNNING)
        return True

    @classmethod
    def gameover(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        cls.mode = "main"
        return True

# ================================================== run ==================================================
if __name__ == "__main__":
    Logic.start()
    sys.exit()
