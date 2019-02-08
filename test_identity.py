# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 20:59:04 2018

@author: Jatin Pal Singh
"""

import pygame
import random
from os import path
import neat
import pickle


img_dir = path.join(path.dirname(__file__), 'img')

WIDTH = 480
HEIGHT = 720
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GENERATION = 0
MAX_FITNESS = 0
BEST_GENOME = 0

pygame.init()
time_1 = pygame.time.get_ticks()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteride")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')
background = pygame.image.load(path.join(img_dir, "bg.jpg")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange.png")).convert()
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorBrown_med1.png',
               'meteorBrown_med3.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        #self.radius = 25
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self,action):
        self.speedx = action
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH 
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        time_2 = pygame.time.get_ticks()
        global time_1
        if (time_2-time_1>300):
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            time_1 = time_2

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        #self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-60, -50)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self,action):
        #self.rotate()
        #self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-20, -10)
            self.speedy = random.randrange(1, 10)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -20

    def update(self,action):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)


for i in range(5):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def game(net):

    score = 0
    fitness = 0
    time = 0
    running = True

    while running:
        # keep loop running at the right speed
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_rect)
        
        if hits:
            running = False
            for i in mobs:
                i.rect.x = random.randrange(50,250)
                i.rect.y = random.randrange(-20, -10)
                
        time+= 1
        
        inp = [-1,-1]

        for mb in mobs:
            if mb.rect.right in range(player.rect.left-50,player.rect.right+50):
                inp[0] = 1
                
                
            if mb.rect.left in range(player.rect.left-50,player.rect.right+50):
                inp[1] = 1
                
                
            if ((mb.rect.x+mb.rect.right)/2 >= player.rect.left and (mb.rect.x+mb.rect.right)/2 <= player.rect.right):
                player.shoot()
                

        output = net.activate(inp)
        
        # Update
        all_sprites.update(output[0])
        

        # check to see if a bullet hit a mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 500 - hit.rect.width
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)

        fitness = score+time
        # Draw / render
        screen.fill(BLACK)
        screen.blit(background, background_rect)
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        pygame.display.flip()



    return fitness



config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config')

genomeFile = 'D:/NEAT/Shmup/bestGenomes/model14308.sav'
genome = pickle.load(open(genomeFile,'rb'))
net = neat.nn.FeedForwardNetwork.create(genome, config)
for i in range(5):
    fitness = game(net)
    print('Fitness is %f'% fitness)
pygame.quit()