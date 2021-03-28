import pygame
import random
import sys
from pygame.locals import *

pygame.init()
pygame.font.init()
pygame.mixer.init()

#Loading Music
pygame.mixer.music.load('sounds/menu.ogg')
laser_sound = pygame.mixer.Sound('sounds/pew.wav')
crash_sound = pygame.mixer.Sound('sounds/expl3.wav')
explode_sound = pygame.mixer.Sound('sounds/expl6.wav')
hit_sound = pygame.mixer.Sound('sounds/rumble1.ogg')

#creating display
height = 750
width = 750
SCREEN = pygame.display.set_mode((height,width))
pygame.display.set_caption('Space Shooter')

#PLAYER SHIP
YELLOW_SPACE_SHIP = pygame.image.load('assets/pixel_ship_yellow.png')
YELLOW_SPACE_SHIP = pygame.transform.scale(YELLOW_SPACE_SHIP,(100,90))
#ENEMIES
BLUE_SPACE_SHIP = pygame.image.load('assets/pixel_ship_blue_small.png')
RED_SPACE_SHIP = pygame.image.load('assets/pixel_ship_red_small.png')
GREEN_SPACE_SHIP = pygame.image.load('assets/pixel_ship_green_small.png')

#LASERS
RED_LASER = pygame.image.load('assets/pixel_laser_red.png')
YELLOW_LASER = pygame.image.load('assets/pixel_laser_yellow.png')
BLUE_LASER = pygame.image.load('assets/pixel_laser_blue.png')
GREEN_LASER = pygame.image.load('assets/pixel_laser_green.png')

# Background
BG = pygame.image.load('assets/background-black.png').convert()
BG = pygame.transform.scale(BG,(height,width)).convert_alpha()


main_menu_img = pygame.image.load('assets/main_menu.png')
main_menu_img = pygame.transform.scale(main_menu_img,(height,width)).convert_alpha()
class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
    def move(self,vel):
        self.y += vel
    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)
    def collision(self,obj):
        return collide(self,obj)



class Ship:
    COOLDOWN = 90
    
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    def shoot(self):
        if self.cool_down_counter == 0:
            laser= Laser(self.x+80,self.y-20,self.laser_img)
            laser2 = Laser(self.x+13,self.y-20,self.laser_img)
            self.lasers.append(laser)
            self.lasers.append(laser2)
            self.cool_down_counter = 1
            pygame.mixer.Sound.play(laser_sound)
    def draw(self,screen):
        screen.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(screen)
    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                pygame.mixer.Sound.play(hit_sound)
                self.lasers.remove(laser)
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()
class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        pygame.mixer.Sound.play(explode_sound)
                        return True

    def healthbar(self,screen):
                
        pygame.draw.rect(screen, (0,255,0), (self.x+2,self.y+95,self.health,10))
        pygame.draw.rect(screen, (255,255,255), (self.x+2,self.y+95,100,10), 2)
class Enemy(Ship):
    COLOR_MAP = {
                    'red':(RED_SPACE_SHIP,RED_LASER),
                    'green':(GREEN_SPACE_SHIP,GREEN_LASER),
                    'blue':(BLUE_SPACE_SHIP,BLUE_LASER)
    }
    def __init__(self,x,y,color,health = 100):
        super().__init__(x,y,health)
        self.ship_img,self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self,vel):
        self.y += vel
    def shoot(self):
        if self.cool_down_counter == 0:
            laser= Laser(self.x-20,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y -obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None
def main():
    run = True
    lost = False
    FPS = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 3
    player = Player(300,635)
    main_font = pygame.font.SysFont('arial', 50, bold=False, italic=False)
    lost_font = pygame.font.SysFont('arial',60,bold = True)
    player_vel = 2
    laser_vel = 4
    enemies_laser_vel = 6
    enemies = []
    wave_length = random.randrange(5,10)
    enemies_vel = 3
    lost_count = 0
    score = 1
    score_font = pygame.font.SysFont('arial',50,bold = True)
    BGY = 0
    lives_img = pygame.image.load('assets/heart1.png')
    lives_img = pygame.transform.scale(lives_img,(50,50)).convert_alpha()
    def redraw_window():

        for enemy in enemies:
            enemy.draw(SCREEN)
        #Drawing Font
        lives_label = main_font.render(f"Lives: {lives}",True, (255,255,255))
        level_label = main_font.render(f"Wave: {level}", True, (255,255,255))
#       SCREEN.blit(lives_label,(10,10))
        SCREEN.blit(level_label, (width - level_label.get_width() - 10,10))
        player.draw(SCREEN)
        player.healthbar(SCREEN)
        score_label = score_font.render(f'Score: {score}',True,(255,255,255))
        SCREEN.blit(score_label,(280,10))
        if lives ==3:
            SCREEN.blit(lives_img,(20,10))
            SCREEN.blit(lives_img,(75,10))
            SCREEN.blit(lives_img,(130,10))
        if lives ==2:
            SCREEN.blit(lives_img,(20,10))
            SCREEN.blit(lives_img,(75,10))
        if lives ==1:
            SCREEN.blit(lives_img,(20,10))
        if lost:
            player.health = 0
            lost_label = lost_font.render('YOU LOST!!!',1,(255,255,255))
            SCREEN.blit(lost_label,(width/2 - lost_label.get_width()/2,350))
        pygame.display.update()

    while run:
        clock.tick()
        if not lost:
            rel_x = BGY % BG.get_height()
            
            SCREEN.blit(BG,(0,rel_x - BG.get_height()))
            if rel_x < height:
                SCREEN.blit(BG, (0,rel_x))
            BGY += 1.5
        redraw_window()
        if score <= 0:
            lost = True
            lost_count += 1
            score = 0
        if lives <= 0:
            lost = True
            lost_count += 1
            player.health = 0
        elif player.health <= 0:
            lives -= 1
            player.health = 100
        if lost:
            if lost_count > 60 * 5:
                run = False
                
            else:
                continue
        if len(enemies) == 0:
            level +=1
            wave_length += random.randrange(5,10)
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,width-100),random.randrange(-1500,-100),random.choice(['red','green','blue']))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y += -player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < height:
            player.y += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x += -player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < width:
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemies_vel)
            enemy.move_lasers(enemies_laser_vel,player)
            if enemy.y + enemy.get_height() > height:
                enemies.remove(enemy)
            if collide(enemy,player):
                player.health -= 10
                enemies.remove(enemy)
                pygame.mixer.Sound.play(crash_sound)
            elif random.randrange(0,120) == 1:
                enemy.shoot()

        player.move_lasers(-laser_vel, enemies)
        if player.move_lasers(-laser_vel,enemies):
            score += random.randrange(50,55)
        if keys[pygame.K_v]:
            player.health = 100
def main_menu():
    run = True
    pygame.mixer.music.play()
    while run:

        SCREEN.blit(main_menu_img,(0,0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.mixer.music.fadeout(500)
                    main()
                if event.key == pygame.K_q:
                    run = False
main_menu()
