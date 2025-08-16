import pygame
import button_test
import csv
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

# cua so game
screen_width = 800
screen_height = 640
lower_margin = 100
side_margin = 300

screen = pygame.display.set_mode((screen_width + side_margin, screen_height + lower_margin))
pygame.display.set_caption('MAP EDITOR')


# chia hang cot
ROWS =  16
MAX_COLS = 150
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 22
current_tile = 0
level = 1

#cuon map
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 2

#load hinh anh
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img) 

save_img = pygame.image.load('img/save_btn.png').convert_alpha()
load_img = pygame.image.load('img/load_btn.png').convert_alpha()
create_img = pygame.image.load('img/create.png').convert_alpha()
delete_img = pygame.image.load('img/delete.png').convert_alpha()


#load hinh anh
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
cloud_img = pygame.image.load('img/background/cloud.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_cloud_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky.png').convert_alpha()

sky_img = pygame.transform.scale(sky_img, (1300, 400))

GREEN = (144,201,120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
BLUE = (0, 0, 255)

#tao ra 1 tile_list trong
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

font = pygame.font.SysFont('Futura', 30)
#ham de luu lai ban do
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# tao nen
def draw_bg():
    screen.fill(GREEN)
    width = sky_img.get_width()
    for x in range(4):
        screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
        screen.blit(sky_cloud_img, ((x * width) - scroll * 0.4, screen_height - mountain_img.get_height() - 500))
        screen.blit(mountain_img, ((x * width) - scroll * 0.6, screen_height - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - scroll * 0.8, screen_height - mountain_img.get_height() - 200))
        screen.blit(pine2_img, ((x * width) - scroll * 0.9, screen_height - mountain_img.get_height() - 140))

# ve luoi
def draw_grid():
    for x in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (x * TILE_SIZE - scroll, 0), (x * TILE_SIZE - scroll, screen_height))  # noi hai toa do lai voi nhau
    for x in range(ROWS):
        pygame.draw.line(screen, WHITE, (0, x * TILE_SIZE), (screen_width, x * TILE_SIZE))

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))
            
#file csv
csv_files = []
def csv_file():
    all_files = os.listdir('E:\code_game')
    for file in all_files:
        if file.endswith('.csv'):
            csv_files.append(file)

# tao nut an
save_button = button_test.Button(screen_width // 2, screen_height + lower_margin - 50, save_img, 1)
load_button = button_test.Button(screen_width // 2 + 200, screen_height + lower_margin - 50, load_img, 1)
create_button = button_test.Button((screen_width + side_margin) // 2, screen_height + lower_margin - 70, create_img, 0.1)
delete_button = button_test.Button(screen_width + side_margin - 200, screen_height + lower_margin - 70, delete_img, 0.2)


button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button_test.Button(screen_width + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

run = True
while run:
    clock.tick(fps) 

    draw_bg()
    draw_grid()
    draw_world()

    # ve 1 nen may xanh chua van phat
    pygame.draw.rect(screen, GREEN, (screen_width, 0, side_margin, screen_height))
    pygame.draw.rect(screen, BLUE, (0, screen_height, screen_width + side_margin, screen_height))
    csv_file()
    str = f'level{level}_data.csv'
    if str in csv_files:
        if save_button.draw(screen):
            with open(f'level{level}_data.csv', 'w', newline = '') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for row in world_data:
                    writer.writerow(row)
                    
        if load_button.draw(screen):
            scroll = 0
            with open(f'level{level}_data.csv', newline = '') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)

    else:
        scroll = 0
        if create_button.draw(screen):
            with open(f'level{level}_data.csv', 'w', newline = '') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for row in world_data:
                    writer.writerow(row)
    
    if delete_button.draw(screen):
        scroll = 0
        with open(f'demo.csv', newline = '') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)     
        if str in csv_files:
            os.remove(str)


    draw_text(f'Map: {level}', font,  WHITE, 10, screen_height + lower_margin - 90)
    draw_text(f'Press Up or Down to change Map', font,  WHITE, 10, screen_height + lower_margin - 50)


    #chon 1 tile
    button_cnt = 0
    for button_cnt, i in enumerate(button_list):
        if(i.draw(screen)):
            current_tile = button_cnt

    #highlight
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    # cuon map
    if scroll_left and scroll > 0:
        scroll -=  5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE) - screen_width:
        scroll += 5 * scroll_speed

    #them 1 tile moi
    # nhan vi tri con chuot
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = (pos[1] // TILE_SIZE)

    #click chuot
    if pos[0] < screen_width and pos[1] < screen_height:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and level > 0 :
                level += 1
            if event.key == pygame.K_DOWN and level > 1:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 2

    pygame.display.update()
pygame.quit()