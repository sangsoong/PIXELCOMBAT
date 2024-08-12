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
pygame.display.set_caption("PIXEL COMBAT")
SCREEN.fill((255, 255, 255))
pygame.display.update()

FONT1 = "fonts\\neodgm.ttf"

PLAYER_SIZE = (WIDTH/16, HEIGHT/16)
ENEMY_SIZE = (WIDTH/16, HEIGHT/16)
VER_DOOR_SIZE = (WIDTH*(3/64)*(115/100), HEIGHT*(10/64)*(115/100))
HOR_DOOR_SIZE = (WIDTH*(10/64)*(115/100), HEIGHT*(3/64)*(115/100))
DOOR_OFF_X = VER_DOOR_SIZE[0]*0.5
DOOR_OFF_Y = HOR_DOOR_SIZE[1]*0.5
DOOR_POS_UP = (WIDTH/2, DOOR_OFF_Y)
DOOR_POS_LEFT = (DOOR_OFF_X, HEIGHT/2)
DOOR_POS_DOWN = (WIDTH/2, HEIGHT-DOOR_OFF_Y)
DOOR_POS_RIGHT = (WIDTH-DOOR_OFF_X, HEIGHT/2)
DUN_MAP_SIZE = (5, 5)
MAP_BKG_SIZE = (WIDTH*0.75, HEIGHT*0.75)
MAP_ROOM_SIZE = (MAP_BKG_SIZE[0]/DUN_MAP_SIZE[0], MAP_BKG_SIZE[1]/DUN_MAP_SIZE[1])
MAP_STATE_SIZE = (MAP_ROOM_SIZE[0]*0.75, MAP_ROOM_SIZE[1]*0.75)
MAP_VER_DOOR_SIZE = (VER_DOOR_SIZE[0]*MAP_ROOM_SIZE[0]/MAP_BKG_SIZE[0], VER_DOOR_SIZE[1]*MAP_ROOM_SIZE[1]/MAP_BKG_SIZE[1])
MAP_HOR_DOOR_SIZE = (HOR_DOOR_SIZE[0]*MAP_ROOM_SIZE[0]/MAP_BKG_SIZE[0], HOR_DOOR_SIZE[1]*MAP_ROOM_SIZE[1]/MAP_BKG_SIZE[1])

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
    def __init__(self, room, path, pos, size):
        self.room = room
        super().__init__(path, pos, size)

class Entity(Image):
    def __init__(self, room, path, pos, size):
        self.room = room
        super().__init__(path, pos, size)

class Projectile(Entity):
    def __init__(self, room, path, pos, size, angle, speed, owner):
        super().__init__(room, path, pos, size)
        self.angle = angle
        self.speed = speed
        self.owner = owner
    
    def collide_check(self):
        for collide in Logic.wrk_colliders:
            for object in collide:
                if object is not self and object.room == self.room and pygame.sprite.collide_mask(object, self):
                    if type(object) == Structure:
                        return (True, 0)
                    elif type(self.owner) == Enemy1 and type(object) == Player:
                        object.health -= 10
                        return (True, object)
                    elif type(self.owner) == Player and type(object) == Enemy1:
                        object.health -= 10
                        return (True, object)

    def move(self):
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y -= math.sin(self.angle) * self.speed

class Player(Entity):
    def __init__(self, room, pos, size):
        super().__init__(room, WRK_PLAYER, pos, size)
        self.dir_up = 0
        self.dir_left = 0
        self.dir_down = 0
        self.dir_right = 0
        self.speed = 4
        self.max_health = 50
        self.health = self.max_health
        self.shoot_delay = 0
        self.shoot_fomula_x = 0
        self.shoot_max_delay = 300/(self.shoot_fomula_x + 12) + 5

    def show_health(self):
        health = self.health
        if self.health < 0:
            health = 0
        elif self.health > self.max_health:
            health = self.max_health
            self.health = self.max_health
        health_bar = Image(EFFECT_RED, (self.rect.centerx, self.rect.midtop[1]-10), (self.health, 10))
        health_bar.draw(L_RUNNING)
        health_text = Text(f"{health}/{self.max_health}", (255, 255, 255), (self.rect.centerx, self.rect.midtop[1]-10), 20)
        health_text.draw(L_RUNNING)
    
    def set_shootdelay(self):
        self.shoot_max_delay = 300/(self.shoot_fomula_x + 12) + 5

    def shoot(self):
        self.shoot_delay += 1
        if self.shoot_delay >= self.shoot_max_delay:
            self.shoot_delay = 0
            rel_x = pygame.mouse.get_pos()[0] - self.rect.centerx
            rel_y = self.rect.centery - pygame.mouse.get_pos()[1]
            angle = math.atan2(rel_y, rel_x)
            projectile = Projectile(self.room, WRK_PLAYER_BULLET, self.rect.center, (10, 10), angle, 5, self)
            Logic.wrk_projectiles.append(projectile)

    def move_dir(self, key, push):
        directions = [(pygame.K_w, "dir_up", -1), (pygame.K_a, "dir_left", -1), (pygame.K_s, "dir_down", 1), (pygame.K_d, "dir_right", 1)]
        for k, direction, w in directions:
            if key == k:
                self.__setattr__(direction, push * w * self.speed)
            
    def move(self):
        directions = [(self.dir_up, "centery"), (self.dir_left, "centerx"), (self.dir_down, "centery"), (self.dir_right, "centerx")]
        for direction, axis in directions:
            self.rect.__setattr__(axis, self.rect.__getattribute__(axis) + direction)
            for objects in Logic.wrk_colliders:
                for object in objects:
                    if id(object) != id(self) and object.room == self.room and pygame.sprite.collide_mask(object, self):
                        if type(object) == Enemy1:
                            pass
                        elif type(object) == Projectile:
                            pass
                        else:
                            self.rect.__setattr__(axis, self.rect.__getattribute__(axis) - direction)
                            break
    
    def room_to(self):
        off_x = Logic.wrk_player.rect.width/2
        off_y = Logic.wrk_player.rect.height/2
        for side, door in self.room.door.items():
            if door != 0 and pygame.sprite.collide_mask(self, door):
                room = self.room.side[side]
                self.room = room
                if door.rect.centery < CENTER[1] - 10:
                    self.goto((self.rect.centerx, DOOR_POS_DOWN[1] - (HOR_DOOR_SIZE[1]/2) - off_y))
                elif door.rect.centerx < CENTER[0] - 10:
                    self.goto((DOOR_POS_RIGHT[0] - (VER_DOOR_SIZE[0]) - off_x, self.rect.centery))
                elif door.rect.centery > CENTER[1] + 10:
                    self.goto((self.rect.centerx, DOOR_POS_UP[1] + (HOR_DOOR_SIZE[1] + off_y)))
                elif door.rect.centerx > CENTER[0] + 10:
                    self.goto((DOOR_POS_LEFT[0] + (VER_DOOR_SIZE[0]) + off_x, self.rect.centery))
                break

class Enemy1(Entity):
    def __init__(self, room, path, pos, size):
        super().__init__(room, path, pos, size)
        self.speed = 1.5
        self.shoot_delay = 0
        self.shoot_max_delay = 60
        self.max_health = 30
        self.health = self.max_health

    def show_health(self):
        if self.health <= 0:
            for collide in Logic.wrk_colliders:
                for object in collide:
                    if object is self:
                        Logic.wrk_score["enemy"] += 1
                        collide.remove(object)
                    if type(object) == Projectile:
                        if object.owner == self:
                            collide.remove(object)
            Logic.wrk_player.health += 1
            Logic.wrk_player.shoot_fomula_x += 1
            Logic.wrk_player.set_shootdelay()
            return
        elif self.health > self.max_health:
            self.health = self.max_health
        health_bar = Image(EFFECT_RED, (self.rect.centerx, self.rect.midtop[1]-10), (self.health, 10))
        health_bar.draw(L_RUNNING)
        health_text = Text(f"{self.health}/{self.max_health}", (255, 255, 255), (self.rect.centerx, self.rect.midtop[1]-10), 20)
        health_text.draw(L_RUNNING)

    def move(self):
        for objects in Logic.wrk_colliders:
            for object in objects:
                if id(object) != id(self) and object.room == self.room and pygame.sprite.collide_mask(object, self):
                    if type(object) == Player:
                        return
                    elif type(object) == Enemy1:
                        pass
                    elif type(object) == Projectile:
                        pass
        rel_x = Logic.wrk_player.rect.centerx - self.rect.centerx
        rel_y = self.rect.centery - Logic.wrk_player.rect.centery
        angle = math.atan2(rel_y, rel_x)
        self.rect.centerx += math.cos(angle) * self.speed
        self.rect.centery -= math.sin(angle) * self.speed

    def shoot(self):
        self.shoot_delay += 1
        if self.shoot_delay > self.shoot_max_delay:
            self.shoot_delay = 0
            rel_x = Logic.wrk_player.rect.centerx - self.rect.centerx
            rel_y = self.rect.centery - Logic.wrk_player.rect.centery
            angle = math.atan2(rel_y, rel_x)
            projectile = Projectile(self.room, WRK_ENEMY1_BULLET, self.rect.center, (10, 10), angle, 5, self)
            Logic.wrk_projectiles.append(projectile)

class Room:
    def __init__(self, pos, type):
        paths = [(WRK_WALL1, WRK_FLOOR1), (WRK_WALL1, WRK_FLOOR1), (WRK_WALL1, WRK_FLOOR1)]
        self.wall = Structure(self, paths[type][0], CENTER, SIZE)
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
        self.enemies = []

    def generate(self):
        rooms = Dungeon.rooms
        rooms_pos = Dungeon.rooms_pos
        x, y = self.pos
        dirs1 = [(x, y+1), (x-1, y), (x, y-1), (x+1, y)]
        dirs2 = [(y, Dungeon.map_size[1]-1), (x, 0), (y, 0), (x, Dungeon.map_size[0]-1)]
        dirs3 = ["up", "left", "down", "right"]
        for i in range(0, 4):
            if random.randint(0, 2):
                if len(rooms) < Dungeon.room_cnt:
                    if dirs2[i][0] != dirs2[i][1]:
                        if dirs1[i] not in rooms_pos:
                            newroom = Room(dirs1[i], 2)
                            self.side[dirs3[i]] = newroom
                            newroom.side[dirs3[(i+2)%4]] = self
                            rooms.append(newroom)
                            rooms_pos.append(dirs1[i])
    
    def set_door(self):
        paths = [WRK_DOOR1, WRK_DOOR1, WRK_DOOR1]
        if self.side["up"]:
            self.door["up"] = Structure(self, paths[self.type], DOOR_POS_UP, (HOR_DOOR_SIZE))
        if self.side["left"]:
            self.door["left"] = Structure(self, paths[self.type], DOOR_POS_LEFT, (VER_DOOR_SIZE))
        if self.side["down"]:
            self.door["down"] = Structure(self, paths[self.type], DOOR_POS_DOWN, (HOR_DOOR_SIZE))
        if self.side["right"]:
            self.door["right"] = Structure(self, paths[self.type], DOOR_POS_RIGHT, (VER_DOOR_SIZE))
    
    def set_enemy(self, count):
        for i in range(0, count):
            enemy = None
            repeat = True
            while repeat:
                repeat = False
                ran_x = random.randint(0, SIZE[0])
                ran_y = random.randint(0, SIZE[1])
                for door in self.door.values():
                    if door != 0 and math.sqrt((ran_x - door.rect.centerx)**2 + (ran_y - door.rect.centery)**2) < max(door.rect.width, door.rect.height)*2:
                        repeat = True
                        break
                if repeat:
                    continue
                enemy = Enemy1(self, WRK_ENEMY1, (ran_x, ran_y), ENEMY_SIZE)
                for collide in Logic.wrk_colliders:
                    for object in collide:
                        if pygame.sprite.collide_mask(enemy, object):
                            repeat = True
                            break
                    if repeat:
                        break
            self.enemies.append(enemy)

class Dungeon:
    map_size = DUN_MAP_SIZE
    floor = 0
    max_floor = 4
    room_cnt = 0
    rooms = []
    rooms_pos = []

    @classmethod
    def initiaize(cls):
        cls.floor = 0
        cls.room_cnt = 0

    @classmethod
    def next_floor(cls):
        cls.floor += 1
        if cls.floor == cls.max_floor+1:
            return True
        cls.room_cnt = cls.floor + 4
        Logic.wrk_player.goto(CENTER)
        Logic.wrk_colliders.clear()
        Logic.wrk_colliders.append([Logic.wrk_player])
        Logic.wrk_colliders.append(Logic.wrk_projectiles)
        cls.generate()
        return False

    @classmethod
    def generate(cls):
        start_x = random.randint(0, cls.map_size[0]-1)
        start_y = random.randint(0, cls.map_size[1]-1)
        walls = []
        while True:
            cls.rooms.clear()
            cls.rooms_pos.clear()
            start_room = Room((start_x, start_y), 0)
            cls.rooms.append(start_room)
            cls.rooms_pos.append(start_room.pos)
            for i in range(0, cls.room_cnt):
                if len(cls.rooms) == i:
                    break
                cls.rooms[i].generate()
                cls.rooms[i].set_door()
                walls.append(cls.rooms[i].wall)
                Logic.wrk_colliders.append(cls.rooms[i].enemies)
            if len(cls.rooms) == cls.room_cnt:
                cls.rooms[-1].type = 1
                Logic.wrk_colliders.append(walls)
                break
        for room in cls.rooms:
            if room.type == 2:
                room.set_enemy(random.randint(cls.floor, cls.floor+2))
            elif room.type == 1:
                room.set_enemy(random.randint(cls.floor+4, cls.floor+6))
    
    @classmethod
    def map(cls, player):
        map = Image(WRK_MAP_BACKGROUND, CENTER, MAP_BKG_SIZE)
        map.draw(L_RUNNING)
        for room in cls.rooms:
            rel_x = room.pos[0] - int(cls.map_size[0]/2)
            rel_y = room.pos[1] - int(cls.map_size[1]/2)
            path = ""
            state = ""
            if room.type == 1:
                path = WRK_MAP_ROOM_BOSS
            elif len(room.enemies) == 0:
                path = WRK_MAP_ROOM_CLEAR
            elif len(room.enemies) > 0:
                path = WRK_MAP_ROOM_ENEMY
            image = Image(path, (CENTER[0]+MAP_ROOM_SIZE[0]*rel_x, CENTER[1]-MAP_ROOM_SIZE[1]*rel_y), MAP_ROOM_SIZE)
            image.draw(L_RUNNING)
            if room.pos == player.room.pos:
                state = WRK_MAP_STATE_PLAYER
            if state:
                state = Image(state, ((CENTER[0]+MAP_ROOM_SIZE[0]*rel_x, CENTER[1]-MAP_ROOM_SIZE[1]*rel_y)), MAP_STATE_SIZE)
                state.draw(L_RUNNING)
        for room in cls.rooms:
            for side, door in room.door.items():
                if door!= 0:
                    rel_x = room.pos[0] - int(cls.map_size[0]/2)
                    rel_y = room.pos[1] - int(cls.map_size[1]/2)
                    off_x = 0
                    off_y = 0
                    size = 0
                    if side == "up":
                        off_y = -MAP_ROOM_SIZE[1]/2
                        size = MAP_HOR_DOOR_SIZE
                    elif side == "left":
                        off_x = -MAP_ROOM_SIZE[0]/2
                        size = MAP_VER_DOOR_SIZE
                    elif side == "down":
                        off_y = MAP_ROOM_SIZE[1]/2
                        size = MAP_HOR_DOOR_SIZE
                    elif side == "right":
                        off_x = MAP_ROOM_SIZE[0]/2
                        size = MAP_VER_DOOR_SIZE
                    image = Image(WRK_DOOR1, (CENTER[0]+MAP_ROOM_SIZE[0]*rel_x+off_x, CENTER[1]-MAP_ROOM_SIZE[1]*rel_y+off_y), size)
                    image.draw(L_RUNNING)

class Logic:
    mode = "main"
    cur_tick = 0
    
    main_background = Background(MAIN_BACKGROUND)
    main_start = Button(MAIN_START, MAIN_START_HOVER, (WIDTH*1/2, HEIGHT*8/10), (200, 70))
    main_exit = Button(MAIN_EXIT, MAIN_EXIT_HOVER, (WIDTH*1/2, HEIGHT*9/10), (200, 70))
    
    intro_loading = Background(EFFECT_BLACK)
    intro_percentage = Text("", (255, 255, 255), CENTER, 30, FONT1)
    intro_time = 0
    
    wrk_player = Player(None, CENTER, PLAYER_SIZE)
    wrk_colliders = []
    wrk_projectiles = []
    wrk_score = {"enemy": 0}
    wrk_portal_time = 0
    wrk_player_shootdelay = Text("", (255, 255, 255), CENTER, 15, FONT1)
    wrk_player_floor = Text("", (255, 255, 255), CENTER, 15, FONT1)

    gameover_background = Background(GAMEOVER_BACKGROUND)
    gameover_subbackground = Image(EFFECT_WHITE_200, (WIDTH, -HEIGHT/2), SIZE)
    gameover_time = 150
    gameover_title = Image(GAMEOVER_TITLE, (CENTER[0], CENTER[1]*1/4), (SIZE[0]*7/8, SIZE[1]/7))
    gameover_score_floor = Text("", (0, 0, 0), CENTER, 40, FONT1)
    gameover_score_enemy = Text("", (0, 0, 0), (CENTER[0], CENTER[1]+40), 40, FONT1)
    gameover_notice = Text("스페이스바를 눌러 메인화면으로", (0, 0, 0), (CENTER[0], CENTER[1]+100), 30, FONT1)

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
            cls.wrk_player.room = Dungeon.rooms[0]
        return True
    
    @classmethod
    def running(cls):
        player = cls.wrk_player
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                player.move_dir(event.key, 1)
            if event.type == pygame.KEYUP:
                player.move_dir(event.key, 0)
        # 바닥, 벽, 문 그리기
        player.room.floor.draw(L_RUNNING)
        player.room.wall.draw(L_RUNNING)
        # 문 처리, 그리기
        if len(player.room.enemies) == 0:
            for door in player.room.door.values():
                if door != 0:
                    door.draw(L_RUNNING)
            player.room_to()
        # 포탈 처리, 그리기
        if player.room.type == 1 and len(player.room.enemies) == 0:
            cls.wrk_portal_time += 1
            if cls.wrk_portal_time > 23:
                cls.wrk_portal_time = 0
            portal = Image(WRK_PORTALS[cls.wrk_portal_time//6], CENTER, (WIDTH/9, HEIGHT/9))
            portal.draw(L_RUNNING)
            if pygame.sprite.collide_mask(portal, player):
                game_clear = Dungeon.next_floor()
                if game_clear:
                    cls.mode = "gameover"
                    return True
                player.room = Dungeon.rooms[0]
        # 적 처리, 그리기
        for enemy in player.room.enemies:
            enemy.show_health()
            enemy.move()
            enemy.shoot()
            enemy.draw(L_RUNNING)
        # 플레이어 처리, 그리기
        player.move()
        player.draw(L_RUNNING)
        player.show_health()
        if pygame.key.get_pressed()[pygame.K_TAB]:
            Dungeon.map(player)
        if pygame.mouse.get_pressed()[0]:
            player.shoot()
        cls.wrk_player_shootdelay.goto((50 + cls.wrk_player_shootdelay.rect.width/2, 50))
        cls.wrk_player_shootdelay.write(f"발사 속도 : {round(player.shoot_max_delay/60, 2)}초")
        cls.wrk_player_shootdelay.draw(L_RUNNING)
        cls.wrk_player_floor.goto((WIDTH - 50 - cls.wrk_player_floor.rect.width/2, 50))
        cls.wrk_player_floor.write(f"현재 층 : {Dungeon.floor}")
        cls.wrk_player_floor.draw(L_RUNNING)
        # 투사체 처리, 그리기
        for projectile in cls.wrk_projectiles:
            if projectile.room == player.room:
                projectile.move()
                is_collide = projectile.collide_check()
                if is_collide:
                    cls.wrk_projectiles.remove(projectile)
                    continue
                projectile.draw(L_RUNNING)
        # 게임오버 처리
        if player.health <= 0:
            cls.mode = "gameover"
            return True
        return True

    @classmethod
    def gameover(cls):
        cls.gameover_background.draw(L_GAMEOVER)
        if cls.gameover_time > 0:
            cls.gameover_time -= 1
        subback_y = -((HEIGHT/10000)*pow(cls.gameover_time, 2) - HEIGHT/2)
        cls.gameover_subbackground.goto((WIDTH/2, subback_y))
        cls.gameover_subbackground.draw(L_GAMEOVER)
        if cls.gameover_time == 0:
            cls.gameover_title.draw(L_GAMEOVER)
            cls.gameover_score_floor.write(f"최종 층 : {Dungeon.floor}")
            cls.gameover_score_enemy.write(f"처치한 적 : {cls.wrk_score["enemy"]}")
            cls.gameover_score_floor.draw(L_GAMEOVER)
            cls.gameover_score_enemy.draw(L_GAMEOVER)
            cls.gameover_notice.draw(L_GAMEOVER)
        # 초기화
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    cls.intro_percentage.write("")
                    cls.intro_time = 0
                    Dungeon.initiaize()
                    cls.wrk_projectiles.clear()
                    cls.wrk_player.health = cls.wrk_player.max_health
                    cls.wrk_player.goto((0, 0))
                    cls.wrk_player.shoot_fomula_x = 0
                    cls.wrk_player.set_shootdelay()
                    cls.wrk_score["enemy"] = 0
                    cls.gameover_time = 100
                    cls.mode = "main"
        return True

# ================================================== run ==================================================
if __name__ == "__main__":
    Logic.start()
    sys.exit()
