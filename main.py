import pygame as pg
from pygame.locals import *
import sys, random, math
    

SCREEN_SIZE = (300, 300)


class Player:
    PLAYER_SIZE = 10
    
    def __init__(self):
        self.surface = pg.Surface((self.PLAYER_SIZE, self.PLAYER_SIZE))
        self.surface.fill("orange")
        # self.surface.set_colorkey((255,0,255))
        self.speed = 10
        self.xpos = 50
        self.ypos = 50
        self.mana = 10
        self.reload = 2000
        
        self.generate_orbs()

    def generate_orbs(self):
        self.mana_orbs = []
        for value in range(self.mana):
            orb = Entity((3, 3), self.xpos, self.ypos, aggresive=False)
            orb.surface.fill("blue")
            self.mana_orbs.append(orb)
    
    def recovery(self, max=False):
        if max:
            self.mana = 10
        elif self.mana < 10:
            self.mana += 1
        self.generate_orbs()
        
    def movement(self, direction):
        if direction == "right":
            if self.xpos > SCREEN_SIZE[0] - 20: return
            self.xpos += self.speed
        if direction == "left":
            if self.xpos < 1: return
            self.xpos -= self.speed
        if direction == "up":
            if self.ypos < 1: return
            self.ypos -= self.speed
        if direction == "down":
            if self.ypos > SCREEN_SIZE[1] - 20: return
            self.ypos += self.speed
            
    def teleport(self, direction):
        for i in range(30):
            self.movement(direction)
    
    def attack(self, direction, entity_list):
        if self.mana == 0: return
        self.mana -= 1
        self.generate_orbs()
        for i in range(12):
            if direction == "up":
                temp = Entity(
                    (4, 4), 
                    self.xpos+random.randint(-3*i, 3*i), 
                    self.ypos-10*i,
                    time=pg.time.get_ticks()
                )
            elif direction == "down":
                temp = Entity(
                    (4, 4), 
                    self.xpos+random.randint(-3*i, 3*i), 
                    self.ypos+10*i,
                    time=pg.time.get_ticks()
                )
            elif direction == "left":
                temp = Entity(
                    (4, 4), 
                    self.xpos-10*i, 
                    self.ypos+random.randint(-3*i, 3*i),
                    time=pg.time.get_ticks()
                )
            elif direction == "right":
                temp = Entity(
                    (4, 4), 
                    self.xpos+10*i, 
                    self.ypos+random.randint(-3*i, 3*i),
                    time=pg.time.get_ticks()
                )
            temp.surface.fill("yellow")
            entity_list.append(temp)
            

class Entity:
    def __init__(self, entity_size, x, y, time=None, speed=4, aggresive=True):
        self.surface = pg.Surface(entity_size)
        self.aggresive = aggresive
        if self.aggresive: self.surface.fill("green")
        self.time = time
        self.speed = speed
        self.xpos = x
        self.ypos = y
        self.dead = False

    def tracking(self, player_xpos, player_ypos): 
        if self.dead: return
        if random.randint(0, 1) >= 1:
            return
        dist_to_player = math.sqrt((player_xpos-self.xpos)**2+\
        (player_ypos-self.ypos)**2)
        if dist_to_player > 120:
            if self.aggresive: self.surface.fill("green")
            xstep = random.randint(-1, 1) * self.speed
            ystep = random.randint(-1, 1) * self.speed
            if self.xpos > SCREEN_SIZE[0] - 20:
                xstep = -abs(xstep)
            elif self.xpos < 1:
                xstep = abs(xstep)
            if self.ypos < 1:
                ystep = abs(ystep)
            elif self.ypos > SCREEN_SIZE[1] - 20:
                ystep = -abs(ystep)
            self.xpos += xstep
            self.ypos += ystep
            return
        if self.aggresive: self.surface.fill("red")
        if self.xpos < player_xpos:
            self.xpos += self.speed
        else:
            self.xpos -= self.speed
        if self.ypos < player_ypos:
            self.ypos += self.speed
        else:
            self.ypos -= self.speed
    
    def stun(self):
        if self.speed != 0:
            self.speed -= 1
        else:
            self.surface.fill("black")
            self.dead = True


def main():
    pg.init()    
    screen = pg.display.set_mode(SCREEN_SIZE, pg.SCALED)
    pg.display.set_caption("Klot")
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill("grey")    
    screen.blit(background, (0, 0))
    pg.display.flip()
        
    you = Player()
    
    reload = pg.USEREVENT + 1
    pg.time.set_timer(reload, you.reload)

    screen.blit(you.surface, (you.xpos, you.ypos))
    
    clock = pg.time.Clock()
    enemies = []
    for a in range(6):
        size = random.randint(6, 20)
        sp = random.randint(2, 8)
        enemies.append(Entity(
                (size, size), 
                200, 
                200, 
                time=clock.get_time(),
                speed=sp
            )
        )
    
    entities = []

    while 1:
        screen.blit(background, (0, 0))
        screen.blit(you.surface, (you.xpos, you.ypos))
        for enemy in enemies:
            screen.blit(enemy.surface, (enemy.xpos, enemy.ypos))
            enemy.tracking(you.xpos, you.ypos)
        for thing in entities:
            screen.blit(thing.surface, (thing.xpos, thing.ypos))
            for enemy in enemies:
                dist = math.sqrt((enemy.xpos-thing.xpos)**2+\
                (enemy.ypos-thing.ypos)**2)
                if dist < 3:
                    enemy.stun()
            time = pg.time.get_ticks()
            if time - thing.time > 500:
                entities.remove(thing)
        for orb in you.mana_orbs:
            screen.blit(orb.surface, (orb.xpos, orb.ypos))
            orb.tracking(you.xpos, you.ypos)
        pg.display.update()
        for enemy in enemies:
            death_dist = math.sqrt((enemy.xpos-you.xpos)**2+\
            (enemy.ypos-you.ypos)**2)
            if death_dist < 6:
                if enemy.dead:
                    you.recovery(max=True)
                    enemies.remove(enemy)
                else:
                    pg.quit()
                    sys.exit()
        for event in pg.event.get():
            for enemy in enemies:
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
            if event.type == reload:
                you.recovery()
            if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT: 
                        you.movement("left")
                    if event.key == pg.K_RIGHT: 
                        you.movement("right")
                    if event.key == pg.K_UP:
                        you.movement("up")
                    if event.key == pg.K_DOWN:
                        you.movement("down")
                    if event.key == pg.K_z:
                        you.teleport("down")
                    if event.key == pg.K_x:
                        you.teleport("up")
                    if event.key == pg.K_w:
                        you.attack("up", entities)
                    if event.key == pg.K_s:
                        you.attack("down", entities)
                    if event.key == pg.K_a:
                        you.attack("left", entities)
                    if event.key == pg.K_d:
                        you.attack("right", entities)
        clock.tick(25)


if __name__ == "__main__":
    main()