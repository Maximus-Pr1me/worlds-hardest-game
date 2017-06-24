#!/usr/bin/env python3

import pygame as pg
import sys
import math

class Block(pg.sprite.Sprite):
    def __init__(self, color, width, height):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.orig_x = 550
        self.orig_y = 450
        self.rect.x = self.orig_x + 200
        self.rect.y = self.orig_y

    def __repr__(self):
        return "Block(image={}, rect={}".format(
            self.image, self.rect)

    def update(self, *args):
        self.rect.x += 10

class ABlock(Block):
    def update(self, *args):
        # This function takes a tick count as an argument, ticks are in ms
        # so we can do some math to get a velocity, but for now let's see
        # if we can get a parametric funtion to work. Let's move pi/2 rad
        # per sec to start
        self.rect.x = self.orig_x + 500 * math.cos(args[0] / 500)
        self.rect.y = self.orig_y + 100 * math.sin(args[0] / 500)
        

class BBlock(Block):
    def update(self, *args):
        self.rect.x = self.orig_x + 100 * math.cos(args[0] / 200)
        self.rect.y = self.orig_y + 500 * math.sin(args[0] / 200)

pg.init()
width, height = 1920, 1080
screen = pg.display.set_mode((width, height))
screen.fill((0, 0, 0))

a = ABlock((255, 0, 0), 300, 200)
b = BBlock((0, 0, 255), 100, 100)


groupa = pg.sprite.Group(a)
groupb = pg.sprite.Group(b)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit(0)

    groupa.draw(screen)
    groupb.draw(screen)
    pg.display.flip()

    collided = pg.sprite.spritecollide(a, groupb, False)
    for collision in collided:
        print(collision)

    screen.fill((0, 0, 0))
    groupa.update(pg.time.get_ticks())
    groupb.update(pg.time.get_ticks())
        
    
    pg.time.wait(1000 // 60)
