import pygame as pg
import sys
import math

class Entity(pg.sprite.Sprite):
    def __init__(self, surface):
        pg.sprite.Sprite.__init__(self)

        self.image = surface
        self.rect = self.image.get_rect()
        self.orig_x = 0
        self.orig_y = 0
        self.rect.x = self.orig_x
        self.rect.y = self.orig_y

        # Vars for patrol mode
        # FIXME: Group wait_times and patrol points into a datatype
        # FIXME: Support non-linear paths to targets?
        #        - Might not need, can just define more points to follow
        #        - I don't think CPU usage increases with number of
        #          points in path, so this will not be a huge problem
        #          It will consume more RAM though, that's fine
        self.path = [(0, 0), (0, 500), (500, 500), (500, 0), (1000, 1000)]
        self.wait_times = [0, 0, 0, 0, 0]

        self.target = 1 # index to go toward
        self.wait = 0

        self.waiting = False

    def __repr__(self):
        return "Block(image={}, rect={}".format(
            self.image, self.rect)

    # So, we're going to implement pathing.  The idea is we're going to
    # have points that the object will go towards and maybe wait at for a
    # time.  The key is that I want to use a dx and dy, not an absolute function
    # to determine position.  Let's start with a simple 2 point patrol
    
    def patrol(self, *args):
        # I want speed to be constant, need to use some trig to determine
        # the x and y components that need to change

        if self.waiting:
            self.wait += 1

            if self.wait == self.wait_times[self.target]:
                self.waiting = False
                self.target = (self.target + 1) % len(self.path)

            return

        speed = 1
        dx = self.path[self.target][1] - self.rect.x
        dy = self.path[self.target][0] - self.rect.y

        total_dist = math.hypot(dx, dy)

        if total_dist < speed:
            speed = total_dist

        if total_dist == 0:
            # We've reached our target
            self.waiting = True
            self.wait = -1
            return

        ratio = speed / total_dist
            

        tick_dx = ratio * dx
        tick_dy = ratio * dy

        self.rect.x += tick_dx
        self.rect.y += tick_dy

    def update(self, *args):
        self.patrol(args)
        # self.rect.x += 10

if __name__ == '__main__':
    pg.init()
    width, height = 1920, 1080
    screen = pg.display.set_mode((width, height))
    screen.fill((0, 0, 0))

    a_surf = pg.Surface((50, 50))
    a_surf.fill((255, 255, 255))
    a = Entity(a_surf)

    group_a = pg.sprite.Group(a)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit(0)

        group_a.draw(screen)
        pg.display.flip()

        screen.fill((0, 0, 0))
        group_a.update()

        pg.time.wait(1000 // 60)
