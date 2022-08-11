import pygame
import os
from pygame.locals import *
import random
from time import time
from pygame import mixer
from os import path

clock = pygame.time.Clock()
highscore_file = 'highscore.txt'
dir = path.dirname(__file__)
with open(path.join(dir, highscore_file), 'w') as f:
    try:
        high = int(f.read())
    except:
        high = 0
    

# center the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'
# Initialize pygame
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()   

# create the screen
screen = pygame.display.set_mode((800, 300))
pygame.display.set_caption("Dino Game")
background = pygame.image.load('ground.png')
# two backgrounds back to back for moving effect
background_X = 0
bg_width = background.get_width()
background_X2 = bg_width

class dino:
    jump_img = pygame.image.load('dino.png')
    run_img = [pygame.image.load('dino_run1.png'), pygame.image.load('dino_run2.png')]
    duck_img = [pygame.image.load('dino_duck1.png'), pygame.image.load('dino_duck2.png')]
    dead_img = pygame.image.load('dino_dead.png')

    def __init__(self, x, y, duck_y):
        self.x = x
        self.y = y
        self.duck_y = duck_y
        self.jumping = False
        self.velocity = 0
        self.gravity = 10
        self.onGround = True
        self.ducking = False
        self.runCount = 0
        self.mask = pygame.mask.from_surface(self.jump_img)
        self.dead = False
    def dinoDraw(self, screen):
        self.runCount += 1
        if(self.runCount + 1 >= 12):
            self.runCount = 0

        if self.dead:
            screen.blit(self.dead_img, (self.x, self.y))
        elif(not(self.ducking) and not(self.jumping)):
            screen.blit(self.run_img[self.runCount // 6], (self.x, self.y))
            self.mask = pygame.mask.from_surface(self.run_img[self.runCount // 6])
        elif(not(self.ducking)):
            screen.blit(self.jump_img, ((self.x, self.y)))
            self.mask = pygame.mask.from_surface(self.jump_img)
        else:
            screen.blit(self.duck_img[self.runCount // 6], (self.x, self.duck_y))
            self.mask = pygame.mask.from_surface(pygame.image.load('dino_duck1.png'))
        self.jump()

    def jump(self):
        if self.jumping:
            self.velocity -= self.gravity * .05
        self.y -= self.velocity
        if self.y > 220:
            self.y = 220
            self.jumping = False
            self.velocity = 0

class bird:
    bird_img = [pygame.image.load('bird_up.png'), pygame.image.load('bird_down.png')]
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.flyCount = 0
        self.width = 0
        self.height = 0
        self.mask = pygame.mask.from_surface(self.bird_img[0])
        self.img = self.bird_img[0]
    def drawObj(self, screen):
        if not(self.flyCount % 2 == 0):
            self.img = self.bird_img[1]
            self.mask = pygame.mask.from_surface(self.bird_img[1])
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        if(self.flyCount + 1 >= 24):
            self.flyCount = 0
        screen.blit(self.bird_img[self.flyCount // 12], (self.x, self.y))
        self.flyCount += 1

class cactus:
    cacti = [pygame.image.load('small1.png'), pygame.image.load('small2.png'), pygame.image.load('small3.png'), 
            pygame.image.load('small4.png'), pygame.image.load('small5.png'), pygame.image.load('small6.png'),
            pygame.image.load('small_merge1.png'), pygame.image.load('small_merge2.png'), 
            pygame.image.load('small_merge1.png'), pygame.image.load('small_merge2.png')]
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0
        self.img = self.cacti[random.randrange(0, 10)]
        self.mask = pygame.mask.from_surface(self.img)
        self.height = 0
    def drawObj(self, screen):
        self.width = self.img.get_width()   
        screen.blit(self.img, (self.x, self.y))
            

class bigCactus(cactus):
    cacti = [pygame.image.load('big1.png'), pygame.image.load('big2.png'), pygame.image.load('big3.png'),
            pygame.image.load('big4.png'), pygame.image.load('big5.png'),pygame.image.load('big6.png'), 
            pygame.image.load('big_merge1.png'), pygame.image.load('big_merge2.png'), 
            pygame.image.load('big_merge1.png'), pygame.image.load('big_merge2.png')]
    def drawObj(self, screen):
        super().drawObj(screen)



class cloud:
    img = pygame.image.load('cloud.png')
    def __init__(self):
        self.x = random.randrange(810, bg_width)
        self.y = 100
        self.width = self.img.get_width()
        self.mask = pygame.mask.from_surface(self.img)
        self.height = 0
    def drawObj(self, screen):
        screen.blit(self.img, (self.x, self.y))

#draw window
def draw():
    #make background white
    screen.fill((255, 255, 255))
    #draw background
    screen.blit(background, (background_X, 250))
    screen.blit(background, (background_X2, 250))
    #draw player
    player.dinoDraw(screen)
    for x in objects:
        x.drawObj(screen)

    font = pygame.font.Font('DisposableDroidBB.ttf', 22)
    prevScore = font.render(str(score).zfill(5), 1, (128, 128, 128))
    screen.blit(prevScore, (700, 10))
    if not(high == 0):
        highScore = font.render('HI ' + str(high).zfill(5), 1, (128, 128, 128))
        screen.blit(highScore, (600, 10))
    pygame.display.update()

class retry:
    button = pygame.image.load('retry.png')
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = self.button.get_width()
        self.height = self.button.get_height()
    def draw(self, screen):
        screen.blit(self.button, ((0.5 * 800) - (0.5 * retry.button.get_width()), 
            (0.5 * 300) - (0.5 * retry.button.get_height())))
    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False
button = retry((0.5 * 800) - (0.5 * retry.button.get_width()), (0.5 * 300) - (0.5 * retry.button.get_height()))

def end():
    screen.fill((255, 255, 255))
    screen.blit(background, (0, 250))
    global score, objects, speed
    player.dinoDraw(screen)
    for x in objects:
        screen.blit(x.img, (x.x, x.y))
    font = pygame.font.Font('DisposableDroidBB.ttf', 22)
    prevScore = font.render(str(score).zfill(5), 1, (128, 128, 128))
    screen.blit(prevScore, (700, 10))
    
    highScore = font.render("HI " + str(high).zfill(5), 1, (128, 128, 128))
    screen.blit(highScore, (600, 10))
    button.draw(screen)
    run = True
    while(run): 
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if(event.type == pygame.QUIT):
                run = False
                pygame.quit()
                quit()
            if(event.type == pygame.MOUSEBUTTONDOWN):
                if button.isOver(pos):
                    lastTime = time()
                    player.dead = False
                    objects = []
                    speed = 60
                    screen.blit(background, (0, 0))
                    run = False
        img = pygame.image.load('game_over.png')
        screen.blit(img, ((0.5 * 800) - (0.5 * img.get_width()), (0.5 * 300) - (0.5 * img.get_height() + 35)))
        pygame.display.update()
    score = 0

pygame.time.set_timer(USEREVENT+1, 500)
pygame.time.set_timer(USEREVENT+2, random.randrange(500, 2000))

objects = []

speed = 60
# Game Loop
run = True
player = dino(150, 220, 240)
pygame.key.set_repeat(1, 25)
lastTime = time()
score = 0
while(run):
    score += 1
    draw()
    for i in objects:
        i.x -= 3
        if(i.x < i.width * -1):
            objects.pop(objects.index(i))
        offset = (i.x - player.x, i.y - round(player.y))
        result = player.mask.overlap(i.mask, offset)
        if(player.ducking):
            phit = (player.x, player.y, 40, 15)
            if phit[0] + phit[2] > i.x and phit[0] < i.x + i.x:
                if phit[1] < i.width:
                    result = True
                result = False
        if result:
            if score > high:
                high = score
                with open(path.join(dir, highscore_file), 'w') as f:
                    f.write(str(score).zfill(5))
            dead_sound = mixer.Sound('die.wav')
            dead_sound.play()
            player.dead = True
            player.jumping = False
            player.ducking = False
            end()

    #make two backgrounds back to back 
    background_X -= 3
    background_X2 -= 3
    #when one background reaches the end, go to the next one
    if(background_X < background.get_width() * -1):
        background_X = bg_width
    if(background_X2 < background.get_width() * -1):
        background_X2 = bg_width
    
    if score % 1000 == 0:
        checkp_sound = mixer.Sound('checkPoint.wav')
        checkp_sound.play()

    # gets all the running events
    for event in pygame.event.get():
        # if the event is a quit event(close the screen), exit program
        if(event.type == pygame.QUIT):
            run = False
            pygame.quit()
            quit()
        if(event.type == USEREVENT+1):
            speed += .5
        if(event.type == USEREVENT+2):
            r = random.randrange(0, 3)
            j = random.randrange(0, 2)
            if r == 0:
                objects.append(cactus(810, 230))
            elif r == 1:
                objects.append(bigCactus(810, 220))
                objects.append(cloud())
            elif r == 2 and score > 2000:
                x = random.randrange(0, 2)
                if x == 0: 
                    objects.append(bird(810, 187))
                elif x == 1:
                    objects.append(bird(810, 220))
            if j == 0 and r == 0:
                objects.append(cloud())

        # pressing down on key
        keystate = pygame.key.get_pressed()
        if not(player.jumping):
            if keystate[K_SPACE] or keystate[K_UP]:
                player.jumping = True
                player.velocity = 10
                jump_sound = mixer.Sound('jump.wav')
                jump_sound.play()
                player.jump()
            if keystate[K_DOWN]:
                player.ducking = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player.ducking = False
    clock.tick(speed)
            

