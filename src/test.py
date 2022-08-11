import pygame
import os
from pygame.locals import *
import random
from time import time
from pygame import mixer
from os import path
import neat

clock = pygame.time.Clock()

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
    for play in players:
        play.dinoDraw(screen)
    for x in objects:
        x.drawObj(screen)
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

def main(genomes, config):
    pygame.time.set_timer(USEREVENT+1, 500)
    pygame.time.set_timer(USEREVENT+2, 750)

    global players
    players = []
    nets = []
    gen = []

    # genome is a tuple like (1, genome) so we have to loop like this
    for _, gene in genomes:
        net = neat.nn.FeedForwardNetwork.create(gene, config)
        nets.append(net)
        players.append(dino(150, 220, 240))
        gene.fitness = 0
        gen.append(gene)

    global objects
    objects = []
    objects.append(cactus(810, 230))

    speed = 60
    # Game Loop
    run = True
    
    pygame.key.set_repeat(1, 25)
    lastTime = time()
    score = 0
    while(run) and len(players) > 0:

        score += 1
        draw()
        
        for x, play in enumerate(players):
            gen[x].fitness += 0.1

            for objec in objects:
                outputs = nets[x].activate((play.y, speed, abs(play.y - objec.height), 
                    abs(play.y - objec.y + objec.height), 
                    objec.width, objec.height))

            if outputs[0] > .75:
                if not play.ducking:
                    play.ducking = True
            elif outputs[1] > .5 and not play.jumping:
                    play.jumping = True
                    play.velocity = 10
                    play.jump()
            else:
                play.ducking = False

        removeList = []

        for i in objects:
            if(i.x < i.width * -1):
                    objects.pop(objects.index(i))
            else:
                i.x -= 3
                if i.x + i.width < 0:
                    removeList.append(i)
            for x, play in enumerate(players):
                offset = (i.x - play.x, i.y - round(play.y))
                result = play.mask.overlap(i.mask, offset)
                if(play.ducking):
                    phit = (play.x, play.y, 40, 15)
                    if phit[0] + phit[2] > i.x and phit[0] < i.x + i.x:
                        if phit[1] < i.width:
                            result = True
                        result = False
                if result:
                    play.dead = True
                    play.jumping = False
                    play.ducking = False
                    gen[x].fitness -= 1
                    players.pop(x)
                    nets.pop(x)
                    gen.pop(x)
                elif not result and i.x < play.x:
                    for genes in gen:
                        genes.fitness += 2

        #make two backgrounds back to back 
        global background_X, background_X2
        background_X -= 3
        background_X2 -= 3
        #when one background reaches the end, go to the next one
        if(background_X < background.get_width() * -1):
            background_X = bg_width
        if(background_X2 < background.get_width() * -1):
            background_X2 = bg_width

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
                for genes in gen:
                    genes.fitness += 1
                r = random.randrange(0, 3)
                j = random.randrange(0, 2)
                if r == 0:
                    objects.append(cactus(810, 230))
                elif r == 1:
                    objects.append(bigCactus(810, 220))
                    objects.append(cloud())
                elif r == 2 and time() - lastTime > 30:
                    x = random.randrange(0, 2)
                    if x == 0: 
                        objects.append(bird(810, 187))
                    elif x == 1:
                        objects.append(bird(810, 220))
                if j == 0 and r == 0:
                    objects.append(cloud())

        for r in removeList:
            objects.remove(r)
            

            # pressing down on key
            for play in players:
                keystate = pygame.key.get_pressed()
                if not(play.jumping):
                    if keystate[K_SPACE] or keystate[K_UP]:
                        play.jumping = True
                        play.velocity = 10
                        play.jump()
                    if keystate[K_DOWN]:
                        play.ducking = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        play.ducking = False
        clock.tick(speed)

def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation,
            config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_file = os.path.join(local_dir,  "config.txt")
    run(config_file)


