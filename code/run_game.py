import pygame
import os
import random
import csv
import button

pygame.init()

screen_width = 1000
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Shooter')
clock = pygame.time.Clock()
time_fps = 60

# trong luc 
GRAVITY = 0.75

ROWS = 16
COLS = 150
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 22
MAX_LEVEL = 3

# Cuon
SCROLL_THRESH = 200
screen_scroll_x = 0
bg_scroll_x = 0
level = 1

# main menu
start_game = False
start_intro = False

# tam dung game
escape_game = False

# tai am thanh
volume = 0.3
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(volume)   # 30% am luong ban dau
pygame.mixer.music.play(-1, 0.0, 5000) # (lap lai bn lan, do tre, am lượng giảm dần {ms})
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(volume)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(volume)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(volume)

# tai hinh anh 
# gate
gate_img = pygame.image.load('img/tile/22.png').convert_alpha()
gate_img = pygame.transform.scale(gate_img, (TILE_SIZE * 2, TILE_SIZE * 2))

# fire 
firel_img = pygame.image.load('img/fire/l.png').convert_alpha()
firel_img = pygame.transform.scale(firel_img, (TILE_SIZE * 3, TILE_SIZE * 1.5))

# escape
continue_img = pygame.image.load('img/continue.png').convert_alpha()
up_img = pygame.image.load('img/up.png').convert_alpha()
down_img = pygame.transform.flip(up_img, False, True)
left_img = pygame.image.load('img/left.png').convert_alpha()
right_img = pygame.transform.flip(left_img, True, False)
tutorial_img = pygame.image.load('img/tutorial.png').convert_alpha()

# main menu
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
bg_img = pygame.image.load('img/bg.png').convert_alpha()
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))

#end 
newgame_img = pygame.image.load('img/new_game.png').convert_alpha()
defeat_img = pygame.image.load('img/defeat.png').convert_alpha()
defeat_img = pygame.transform.scale(defeat_img, (screen_width // 2, screen_height // 4))
victory_img = pygame.transform.scale(pygame.image.load('img/victory.png').convert_alpha(), (screen_width // 2, screen_height // 4))

#tai map
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
cloud_img = pygame.image.load('img/background/cloud.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_cloud_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky.png').convert_alpha()

sky_img = pygame.transform.scale(sky_img, (1300, 400))

# tao tile
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) # (hình anh càn thay doi, (dài, rộng))
    img_list.append(img) 

# tao vien dan
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# tao bom
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

# vat pham duoc nhat
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
item_boxs = {
    'Health'   : health_box_img,
    'Grenade'  : grenade_box_img,
    'Ammo'     : ammo_box_img
}

# di chuyen nhan vat
shoot_key = False 
grenade_key = False
grenade_throw = False
moving_left = False
moving_right = False

# xac dinh phong chu
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# background
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (235, 65, 54)
def draw_bg():
    screen.fill(BLACK)
    width = sky_img.get_width()
    for x in range(4):
        screen.blit(sky_img, ((x * width) - bg_scroll_x * 0.5, 0))
        screen.blit(sky_cloud_img, ((x * width) - bg_scroll_x * 0.4, screen_height - mountain_img.get_height() - 500))
        screen.blit(mountain_img, ((x * width) - bg_scroll_x * 0.6, screen_height - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll_x * 0.8, screen_height - mountain_img.get_height() - 200))
        screen.blit(pine2_img, ((x * width) - bg_scroll_x * 0.9, screen_height - mountain_img.get_height() - 140))

stay = [0] * 3 # giu dat nade mau

# ham reset level
def reset_level():
    enemy_group.empty()
    item_box_group.empty()
    water_group.empty()
    grass_group.empty()
    exit_group.empty()
    dragon_group.empty()
    fire_group.empty()
    gate_group.empty()
    bullet_box_group.empty()

    # tao ra tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

# class 
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades, health) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.alived = True
        self.speed = speed # toc do nhan vat
        self.flip = False
        self.char_type = char_type
        self.direction = 1 # huong nhan van

        #ban sung
        self.shoot_cooldown = 0
        self.ammo = ammo
        self.start_ammo = ammo

        # bom
        self.grenades = grenades
        self.grenade_cooldown = 0

        # mau nhan vat
        self.health = health
        self.max_health = self.health
        
        # hinh anh chuyen dong
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.vel_y = 0
        self.in_air = True
        self.jump_cnt = 2
        self.jump= False
        self.ANIMATION_COOLDOWN = 100

        # ai 
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0 , 150, 20) # toa do (0, 0) , rong , cao 
        self.vision_dragon = pygame.Rect(0, 0 , screen_height // 2, 130)
        self.vision_dragon_close = pygame.Rect(0, 0 , 150, 70)

        # dragon
        self.ammo_fire = 1000
        self.fire_cooldown = 0
        self.first_fire = 0

        # previous

        # load tat ca hinh anh cho nhan vat
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            # dem so hinh anh
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))

            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        if self.char_type == 'dragon':
            # self.rect.size = (self.width, self.height)
            pass

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.grenade_cooldown > 0:
            self.grenade_cooldown -= 1
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0 :
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # giam dan so dan
            self.ammo -= 1 
            shot_fx.play()

    def grenade(self):
        if self.grenade_cooldown == 0 and self.grenades > 0:
            self.grenade_cooldown = 200
            grenade = Grenade(enemy.rect.centerx + (0.5 * enemy.rect.size[0] * enemy.direction), enemy.rect.top, enemy.direction)
            grenade_group.add(grenade)
            self.grenades -= 1
    
    def update_animation(self):
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > self.ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
                if self.char_type == 'dragon' and self.frame_index == len(self.animation_list[self.action]) - 1:
                    explosion = Explosion(self.rect.x + 100, self.rect.y + 50, 4)
                    explosion_group.add(explosion)
                    
                    if pygame.sprite.spritecollide(player, explosion_group, False):
                        if player.alive:
                            player.health -= 100
                            self.kill()
                self.kill()
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # ktra hd moi giong voi hd truoc 
        if new_action != self.action:
            self.action = new_action
            # cap nhap chuyen dong moi
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def fire(self, speed):
        if self.fire_cooldown == 0 and self.ammo_fire > 0 :
            self.fire_cooldown = 300
            fire = Fire(self.rect.centerx + 0.35 * self.rect.size[0] * self.direction, self.rect.centery + 26, self.direction, speed)
            fire_group.add(fire)
            # giam dan so dan
            self.ammo_fire -= 1 

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if self.jump == True and self.jump_cnt > 0:
            self.jump_cnt -= 1
            self.vel_y = -12
            self.jump = False
            self.in_air = True
        

        #trong luc
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y 
        dy += self.vel_y

        #ktra su va cham
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx , self.rect.y - 10, self.width, self.height):
                dx = 0
                # ai va vao tuong se quay lai
                if self.char_type == 'enemy' or self.char_type == 'dragon':
                    self.direction *= -1
                    self.move_counter = 0 # hinh anh bat dau lai

            if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width, self.height):
                # check nv ben duoi dat
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check nv ben tren mat dat
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    self.jump_cnt = 2
                    dy = tile[1].top - self.rect.bottom

        # check nv cham vao nuoc
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check va cham voi exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False) and len(enemy_group) <= 0:
            stay[0] = self.ammo
            stay[1] = self.grenades
            stay[2] = self.health
            level_complete = True

        # check nv roi khoi map
        if self.rect.bottom > screen_height:
            self.health = 0

        if self.char_type == 'player':
            if self.rect.left + dx <= 0 or self.rect.right + dx > screen_width:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        #update do cuon dua tren vi tri player
        if self.char_type == 'player':
            if (self.rect.right > screen_width - SCROLL_THRESH and bg_scroll_x < world.level_length * TILE_SIZE - screen_width)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll_x > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def dragon_ai(self, speed):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1: #self.frame_index == len(self.animation_list[self.action]) - 1:  
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50

            #check khi ke dich nhin thay nv
            if self.vision_dragon.colliderect(player.rect) and self.fire_cooldown < 50:  # and self.fire_cooldown == 0
                self.first_fire += 1
                self.update_action(2)
                if self.frame_index == len(self.animation_list[self.action]) - 2:
                    self.fire(speed)  


            elif self.vision_dragon_close.colliderect(player.rect) and self.fire_cooldown != 0:
                self.update_action(2)
                if self.frame_index > len(self.animation_list[self.action]) - 3:
                    if pygame.sprite.spritecollide(player, dragon_group, False):
                        if player.alive:
                            player.health -= 100
                            pass

            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision_dragon.center = (self.rect.centerx + 220 * self.direction, self.rect.centery + 30)
                    self.vision_dragon_close.center = (self.rect.centerx + 100 * self.direction, self.rect.centery + 30)
                    # pygame.draw.rect(screen, RED, self.vision_dragon, 1)
                    # pygame.draw.rect(screen, RED, self.vision_dragon_close, 4)                    
                    # pygame.draw.rect(screen, RED, self.rect, 1)
                    if self.move_counter > 400:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0: 
                        self.idling = False

        elif self.alive == False and level == 3 and player.alive:
            gate = Decoration(gate_img, self.rect.centerx , self.rect.centery + 20)
            gate_group.add(gate) 

        self.rect.x += screen_scroll_x

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50

            #check khi ke dich nhin thay nv
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
                if level >= 2:
                    self.grenade()
            
            else:
                if self.idling == False:
                    if self.direction == 1:
                            ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen, RED, self.vision)
                    if self.move_counter > 40:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0: 
                        self.idling = False

        self.rect.x += screen_scroll_x
        
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        # pygame.draw.rect(screen, RED, self.rect, 1)

class World():
    def __init__(self):
        self.obstacle_list = []
        self.cooldown = 0
    
    def process_data(self, data):
        self.level_length = len(data[0])

        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8: # đất
                        self.obstacle_list.append(tile_data)

                    elif tile >= 9 and tile <= 10: # nuoc
                        water = Decoration(img, x * TILE_SIZE , y * TILE_SIZE)
                        water_group.add(water)

                    elif tile >= 11 and tile < 14: # trang tri
                        self.obstacle_list.append(tile_data)

                    elif tile == 14: # co
                        grass = Decoration(img, x * TILE_SIZE , y * TILE_SIZE)
                        grass_group.add(grass)

                    elif tile == 15: # tao player
                        # player = Soldier('player', x * TILE_SIZE , y * TILE_SIZE, 0.9, 5, 10, 5, 100)
                        # health_bar = HealthBar(10, 10, player.health, 100)
                        if level == 1:
                            player = Soldier('player', x * TILE_SIZE , y * TILE_SIZE, 0.9, 5, 10, 5, 100)
                            health_bar = HealthBar(10, 10, player.health, 100)
                        if level > 1:
                            player = Soldier('player', x * TILE_SIZE , y * TILE_SIZE, 0.9, 5, stay[0], stay[1], stay[2])
                            health_bar = HealthBar(10, 10, player.health, 100)

                    elif tile == 16: # tao enemy
                        enemy = Soldier('enemy', x * TILE_SIZE , y * TILE_SIZE, 1.2, 2, 1000, 1000, 100)
                        enemy_group.add(enemy)

                    elif tile == 19: # tao health_box
                        item_box = ItemBox('Health', x * TILE_SIZE , y * TILE_SIZE)
                        item_box_group.add(item_box)
                        

                    elif tile == 17: # tao ammo_box
                        item_box = ItemBox('Ammo', x * TILE_SIZE , y * TILE_SIZE)
                        bullet_box_group.add(item_box)

                    elif tile == 18: # tao grenade_box
                        item_box = ItemBox('Grenade', x * TILE_SIZE , y * TILE_SIZE)
                        item_box_group.add(item_box)

                    elif tile == 20: # tao loi thoat
                        exit = Decoration(img, x * TILE_SIZE , y * TILE_SIZE)
                        exit_group.add(exit)

                    elif tile == 21: # tao con roog
                        dragon = Soldier('dragon', x * TILE_SIZE , y * TILE_SIZE, 1.3, 2, 1000, 1000, 1500)
                        dragon_group.add(dragon)

        return player, health_bar
    
    def draw_world(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll_x
            screen.blit(tile[0], tile[1])

class Repeat():
    def __init__(self):
        self.ammo_cooldown = 400
        # self.grenade_cooldown == 800
    
    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    
                    if tile == 17: # tao ammo_box
                        if len(bullet_box_group) <= 0:
                            self.ammo_cooldown -= 1
                            if self.ammo_cooldown == 0:
                                item_box = ItemBox('Ammo', x * TILE_SIZE , y * TILE_SIZE)
                                bullet_box_group.add(item_box)
                                self.ammo_cooldown = 400

                    # if tile == 1: # tao ammo_box
                    #     if len(item_box_group) <= 0:
                    #         self.grenade_cooldown -= 1
                    #         if self.grenade_cooldown == 0:
                    #             item_box = ItemBox('Grenade', x * TILE_SIZE , y * TILE_SIZE)
                    #             item_box_group.add(item_box)
                    #             self.grenade_cooldown = 600
                        
class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update (self):
        self.rect.x += screen_scroll_x

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x * TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update (self):
        self.rect.x += screen_scroll_x

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxs[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        self.vel_y = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health = 100
                if player.health >= 100:
                    player.health = 100
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 10
            self.kill()
        self.rect.x += screen_scroll_x

        dy = 0
        # trong luc
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y 
        dy += self.vel_y

        #ktra su va cham
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width, self.height):
                # check nv ben tren mat dat
                if self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
        self.rect.y += dy

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ti_le = self.health / self.max_health
        pygame.draw.rect(screen, (0, 255 , 0), (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, (0, 0 , 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150 * ti_le, 20))
    
    def update(self):
        self.rect.x += screen_scroll_x

class Fire(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.direction = direction
        if direction == 1:
            self.image = pygame.transform.flip(firel_img, True, False)
        else:
            self.image = firel_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 90
        

    def update(self):
        # duong di vien dan
        self.rect.x += (self.direction * self.speed) + screen_scroll_x
        self.rect.y += 0.49
        # pygame.draw.rect(screen, RED, self.rect, 1)

        # ktra vao cham vao dat
        for tile in world.obstacle_list:
            if self.rect.colliderect(tile[1]):
                self.kill()
                if self.direction == -1: 
                    explosion = Explosion(self.rect.x, self.rect.y, 3)
                    explosion_group.add(explosion)
                else:
                    explosion = Explosion(self.rect.x + 100, self.rect.y, 3)
                    explosion_group.add(explosion)
                
                if pygame.sprite.spritecollide(player, explosion_group, False):
                    if player.alive:
                        player.health -= 100
                        self.kill()

        # va cham nhan vat voi dan
        if pygame.sprite.spritecollide(player, fire_group, False):
            if player.alive:
                self.kill()
                if self.direction == -1: 
                    explosion = Explosion(self.rect.x, self.rect.y, 3)
                    explosion_group.add(explosion)
                else:
                    explosion = Explosion(self.rect.x + 100, self.rect.y, 3)
                    explosion_group.add(explosion)

                player.health -= 100

        if self.health <= 0:
            self.kill()
            if self.direction == -1: 
                explosion = Explosion(self.rect.x, self.rect.y, 3)
                explosion_group.add(explosion)
            else:
                explosion = Explosion(self.rect.x + 100, self.rect.y, 3)
                explosion_group.add(explosion)
            
            if pygame.sprite.spritecollide(player, explosion_group, False):
                if player.alive:
                    player.health -= 100
            for dragon in dragon_group:
                if pygame.sprite.spritecollide(dragon, explosion_group, False):
                    if dragon.alive:
                        dragon.health -= 200
            
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # duong di vien dan
        self.rect.x += (self.direction * self.speed) + screen_scroll_x

        # vien dan vien mat
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
            pass

        # ktra vao cham vao dat
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # va cham nhan vat voi dan
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 50
                    self.kill()

        for dragon in dragon_group:
            if pygame.sprite.spritecollide(dragon, bullet_group, False):
                if dragon.alive:
                    dragon.health -= 50
                    self.kill()

        for fire in fire_group:
            if pygame.sprite.spritecollide(fire, bullet_group, False):
                self.kill()
                if fire.health > 0:
                    fire.health -= 30

        # if pygame.sprite.spritecollide(self, bullet_group, False):
        #         self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.speed * self.direction
        dy = self.vel_y

        #kra vacham voi ground
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed

            if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check  ben duoi dat
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check  ben tren mat dat
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx + screen_scroll_x
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)

            # khi phat no se gay sat thuong
            if pygame.sprite.spritecollide(player, explosion_group, False):
                if player.alive:
                    player.health -= 100
                    self.kill()

            for enemy in enemy_group:
                if pygame.sprite.spritecollide(enemy, explosion_group, False):
                    if enemy.alive:
                        enemy.health = 0
                        self.kill()

            for dragon in dragon_group:
                if pygame.sprite.spritecollide(dragon, explosion_group, False):
                    if dragon.alive:
                        dragon.health -= 100
                        self.kill()

            for fire in fire_group:
                if pygame.sprite.spritecollide(fire, explosion_group, False):
                    if fire.health > 0:
                        fire.health -= 100
                        self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # update scroll
        self.rect.x += screen_scroll_x

        EXPLOSION_SPEED = 4

        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_cnt = 0
    
    def fade(self):
        fade_complete = False
        self.fade_cnt += self.speed

        if self.direction == 1:
            pygame.draw.rect(screen, self.color, (0 - self.fade_cnt, 0, screen_width // 2, screen_height))
            pygame.draw.rect(screen, self.color, (screen_width // 2 + self.fade_cnt, 0, screen_width, screen_height))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_cnt, screen_width, screen_height // 2))
            pygame.draw.rect(screen, self.color, (0, screen_height // 2 + self.fade_cnt, screen_width, screen_height))

        if self.direction == 2:
            # pygame.draw.rect(screen, self.color, (0, 0, screen_width, 0 + self.fade_cnt)) # (sceen, mau, (toa do(x, y), (rong cao)))
            pygame.draw.rect(screen, self.color, (0, 0, 0 + self.fade_cnt, screen_height))
            pygame.draw.rect(screen, self.color, (0, 0, screen_width, 0 + self.fade_cnt))
            pygame.draw.rect(screen, self.color, (screen_width - self.fade_cnt, 0, screen_width, screen_height))
            pygame.draw.rect(screen, self.color, (0, screen_height - self.fade_cnt, screen_width, screen_height))
            pass

        if self.fade_cnt >= screen_height:
            fade_complete = True

        return fade_complete
    
class GameEnding():
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.width = screen_width
        self.height = screen_height
        pygame.font.init()
        self.font = pygame.font.Font(None, 100)
        self.small_font = pygame.font.Font(None, 32)
        self.background = pygame.image.load("img/bg.png").convert_alpha()  # Thay đổi tên file ảnh của bạn
        self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
        self.save_status = True

    def read_fastest_time(self, file_name):
        try:
            with open(file_name, "r") as file:
                data = file.read().strip().split()  # Đọc dữ liệu và loại bỏ khoảng trắng
                data = sorted(map(float, data))
                return data[0]
                
        except FileNotFoundError:
            return None  # Nếu tệp không tồn tại

    def show_victory_screen(self, time_taken):
        screen.blit(self.background,(0,0))
        pygame.time.delay(5)
        # Show victory message
        # victory_text = self.font.render("VICTORY!", True, (255, 215, 0))
        time_text = self.small_font.render(f"Time: {format(int(time_taken // 60), '02d')}:{format(int(time_taken - (time_taken // 60) * 60), '02d')}", True, (255, 255, 255))
        # show thoi gian nhanh nhat
        fastest_time = self.read_fastest_time("fastest_time.txt")
        fastest_time_text = self.small_font.render(f"Fastest Time: {format(int(fastest_time // 60), '02d')}:{format(int(fastest_time - (fastest_time // 60) * 60), '02d')}", True, (255, 255, 255))
        
        # Position text
        victory_rect = victory_img.get_rect(center=(self.width // 2, 50))
        time_rect = time_text.get_rect(center=(self.width // 2, self.height // 2))
        fastest_time_rect = fastest_time_text.get_rect(center=(self.width // 2, self.height // 2 + 60))

        # Show ending credits
        self.screen.blit(victory_img, victory_rect)
        self.screen.blit(time_text, time_rect)
        self.screen.blit(fastest_time_text, fastest_time_rect)


    def save_game_stats(self, time_taken):
        try:
            with open("fastest_time.txt", "a") as file:
                file.write(f"{time_taken} ")
        except:
            print("Could not save game stats")
            
    def end_game(self, time_taken):
        if self.save_status:
            self.save_game_stats(time_taken)
            self.save_status = False
        # Show victory screen
        self.show_victory_screen(time_taken)
        
# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, BLACK, 4)
winner_fade = ScreenFade(2, BLACK, 4)

#create group
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
bullet_box_group = pygame.sprite.Group()
grass_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
dragon_group = pygame.sprite.Group()
fire_group = pygame.sprite.Group()
gate_group = pygame.sprite.Group()

# tao map
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

# tao nhan vat
world = World()
player, health_bar = world.process_data(world_data)

# lam lai box
repeat = Repeat()

# crete button
start_button = button.Button(start_img)
exit_button = button.Button(exit_img)
restart_button = button.Button(restart_img)
up_button = button.Button(up_img)
down_button = button.Button(down_img)
continue_button = button.Button(continue_img)
tutorial_button = button.Button(tutorial_img)
newgame_button = button.Button(newgame_img)
left_button = button.Button(left_img)
right_button = button.Button(right_img)

game_ending = GameEnding(screen, screen_width, screen_height)
run = True
AWSD = True
tutorial = False
start_ticks = pygame.time.get_ticks()
start_time = 10**10
elapsed_seconds = 0
pause = True
interval = 5000
fire_speed = 2

while run:
    clock.tick(time_fps)
    if pause == False:
        elapsed_ticks = pygame.time.get_ticks() - start_ticks
        elapsed_seconds = elapsed_ticks / 1000  # Đổi sang giây
    timer_text = font.render(f"Time: {format(int(elapsed_seconds // 60), '02d')}:{format(int(elapsed_seconds - (elapsed_seconds // 60) * 60), '02d')}", True, BLACK)

    if start_game == False:
        if tutorial == False:
            pause = True
            draw_bg()
            # them cac nut 
            if start_button.draw(screen, screen_width // 2 - 130, screen_height // 2 - 150, 0.3):
                start_game = True
                start_intro = True

            if exit_button.draw(screen, screen_width // 2 - 110, screen_height // 2 + 150, 0.3):
                run = False

            if tutorial_button.draw(screen, screen_width // 2 - 150, screen_height // 2 + 25, 0.25):
                tutorial = True
                pass
        else:
            screen.fill(BLACK)
            if tutorial_button.draw(screen, screen_width // 2 - 150, 10, 0.25):
                tutorial = False
                pass
            draw_text(f'DIEU HUONG :    A_W_S_D (LUDR)', font, WHITE, 10, 100)
            draw_text(f'BAN DAN    :    CHUOT PHAI (E)', font, WHITE, 10, 150)
            draw_text(f'NEM BOM    :    R', font, WHITE, 10, 200)
            pass

    else:
        if pygame.sprite.spritecollide(player, gate_group, False): # win game
            pause = True
            start_ticks = pygame.time.get_ticks()

            if winner_fade.fade():
                game_ending.end_game(elapsed_seconds)

                if newgame_button.draw(screen, screen_width // 2 - 140, screen_height // 2 + 140, 0.25):
                    game_ending.save_status = True
                    winner_fade.fade_cnt = 0
                    level = 1
                    start_intro = True
                    bg_scroll_x = 0
                    world_data = reset_level()
                    
                    fire_speed = 2

                    #load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    # tao nhan vat
                    world = World()
                    player, health_bar = world.process_data(world_data)
                
        elif escape_game == True and start_intro == False: # tam dung game
            pause = True
            screen.fill(BLACK)
            draw_text(f'VOLUME:   {round(volume * 100)} %:', font, WHITE, 10, 75)
            

            if up_button.draw(screen, (0 + 200), 50, 0.2) and volume <= 0.99:
                volume += 0.1
            if down_button.draw(screen, 0 + 200, 50 + 50, 0.2) and volume >= 0.01:
                volume -= 0.1

            if AWSD:
                draw_text(f'NAVIGATION:           AWSD', font, WHITE, 10, 200)
            else:
                draw_text(f'NAVIGATION:           LUDR', font, WHITE, 10, 200) 

            if left_button.draw(screen, (0 + 150), 195, 0.2):
                if AWSD:
                    AWSD = False
                else:
                    AWSD = True

            if right_button.draw(screen, (0 + 300), 195, 0.2):
                if AWSD:
                    AWSD = False
                else:
                    AWSD = True

            pygame.mixer.music.set_volume(volume) 
            shot_fx.set_volume(volume)
            grenade_fx.set_volume(volume)
            jump_fx.set_volume(volume)

            if continue_button.draw(screen, (0 + 100), screen_height - 100, 0.2):
                escape_game = False
                start_intro = True
                pause = False
                pass

            if exit_button.draw(screen, (screen_width - 200), screen_height - 100, 0.2):
                run = False
                pass

        else:
            pause = False
            #show nen
            draw_bg()
            #draw world
            world.draw_world()
            # show bao nhieu mau
            health_bar.draw(player.health)
            #show bao nhieu mau dragon
            if len(dragon_group) > 0:
                for dragon in dragon_group:
                    health_bar_dragon = HealthBar(dragon.rect.x + 60, dragon.rect.y - 30, dragon.health, dragon.max_health)
                    health_bar_dragon.draw(dragon.health)
                    pass

            #show bao nhieu vien dan
            draw_text(f'AMMO:', font, WHITE, 10, 75)
            for x in range(player.ammo):
                screen.blit(bullet_img, (90 + (x * 10), 75))

            # show bao nhieu qua bom
            draw_text(f'GRENADE:', font, WHITE, 10, 105)
            for x in range(player.grenades):
                screen.blit(grenade_img, (125 + (x * 10), 105))

            player.update()
            player.draw()
            
            for dragon in dragon_group:
                dragon.dragon_ai(fire_speed)

                if dragon.first_fire == 0:
                    start_time = pygame.time.get_ticks()
                    # print(dragon.first_fire)

                current_time = pygame.time.get_ticks()
                if (current_time - start_time) > interval and dragon.first_fire >= 1:
                    fire_speed += 0.5  # Tăng tốc độ đạn
                    start_time = current_time  # Đặt lại thời gian bắt đầu
                    # print(fire_speed)

                dragon.update()
                dragon.draw()

            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.draw()

            #cap nhap hinh anh cua group
            bullet_group.update()
            grenade_group.update()
            explosion_group.update()
            item_box_group.update()
            grass_group.update()
            water_group.update()
            exit_group.update()
            fire_group.update()
            gate_group.update()
            bullet_box_group.update()

            bullet_group.draw(screen)
            grenade_group.draw(screen)
            explosion_group.draw(screen)
            item_box_group.draw(screen)
            grass_group.draw(screen)
            water_group.draw(screen)
            exit_group.draw(screen)
            fire_group.draw(screen)
            bullet_box_group.draw(screen)

            if len(dragon_group) <= 0 and level == 3:
                pause = True
                gate_group.draw(screen)

            # show intro
            if start_intro == True:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_cnt = 0

            if player.alive:
                # ktra chuyen dong
                if shoot_key:
                    player.shoot()
                elif grenade_key and grenade_throw == False and player.grenades > 0:
                    grenade_key = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
                    grenade_group.add(grenade_key)
                    player.grenades -= 1
                    grenade_throw = True

                if player.in_air:
                    player.update_action(2) # nhay
                elif moving_left or moving_right:
                    player.update_action(1) # chay
                else:
                    player.update_action(0) # dung yen

                screen_scroll_x, level_complete = player.move(moving_left, moving_right)
                bg_scroll_x -= screen_scroll_x

                # khi hoan thanh map  khi cham vao exit
                if level_complete:
                    start_intro = True
                    level += 1
                    bg_scroll_x = 0
                    world_data = reset_level()
                    fire_speed = 2
                    if level <= MAX_LEVEL:
                        #load in level data and create world
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)

                        # tao nhan vat
                        world = World()
                        player, health_bar = world.process_data(world_data)

                if level == 3:
                    repeat.process_data(world_data)

            else :
                pause = True
                screen_scroll_x = 0
                if death_fade.fade():
                    # defeat_img = 
                    screen.blit(defeat_img, (screen_width // 2 - 210, 10))
                    if exit_button.draw(screen, screen_width // 2 - 70, screen_height // 2 + 50, 0.3):
                        run = False
                    if restart_button.draw(screen, (screen_width // 2 - 120), screen_height // 2 - 90, 0.3):
                        death_fade.fade_cnt = 0
                        start_intro = True
                        bg_scroll_x = 0
                        world_data = reset_level()
                        fire_speed = 2
                        #load in level data and create world
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)

                        # tao nhan vat
                        world = World()
                        player, health_bar = world.process_data(world_data)

    screen.blit(timer_text, (screen_width - 130, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        #nhan ban phim
        if event.type == pygame.KEYDOWN:
            if AWSD:
                if (event.key == pygame.K_a) and escape_game == False: #trai
                    moving_left = True

                if (event.key == pygame.K_d) and escape_game == False: #phai
                    moving_right = True

                if (event.key == pygame.K_SPACE or event.key == pygame.K_w) and player.alive and escape_game == False: # nhay
                    player.jump = True
                    jump_fx.play()
            else:
                if (event.key == pygame.K_LEFT) and escape_game == False: #trai
                    moving_left = True

                if (event.key == pygame.K_RIGHT) and escape_game == False: #phai
                    moving_right = True

                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and player.alive and escape_game == False: # nhay
                    player.jump = True
                    jump_fx.play()

            if event.key == pygame.K_ESCAPE and escape_game == False: 
                death_fade
                escape_game = True 
            elif event.key == pygame.K_ESCAPE and escape_game == True:
                escape_game = False
                start_intro = True

            if event.key == pygame.K_r and escape_game == False: 
                grenade_key = True
            
            if event.key == pygame.K_e and escape_game == False: 
                shoot_key = True

        if event.type == pygame.MOUSEBUTTONDOWN and escape_game == False: 
                if event.button == 3:
                    shoot_key = True

        # nha ban phim
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_w or event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                player.jump = False    
            if event.key == pygame.K_r: 
                grenade_key = False
                grenade_throw = False
            if event.key == pygame.K_e: 
                shoot_key = False
        
        if event.type == pygame.MOUSEBUTTONUP: 
                if event.button == 3:
                    shoot_key = False

    pygame.display.update()
    
pygame.quit()