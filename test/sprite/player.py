
import pygame as pg
import sys
from math import hypot
from itertools import cycle

from collections import namedtuple, defaultdict

# Note: I do believe I need to implement some kind of direct elipse
# pathing.  I make compromises when non-integer numbers of the speed

class Entity(pg.sprite.Sprite):
    def __init__(self, surface):
        pg.sprite.Sprite.__init__(self)

        # Need to define image so group.draw will draw it
        self.image = surface

        # Will get an enclosing rectangle
        self.rect = self.image.get_rect()

PatrolPoint = namedtuple('PatrolPoint', ['x', 'y', 'wait', 'speed'])
                         
class Enemy(Entity):
    def __init__(self, surface, path):
        Entity.__init__(self, surface)

        self.target_gen = cycle(path)
        self.target = next(self.target_gen)

        self.rect.x = path[0].x
        self.rect.y = path[0].y

        self.wait_time_remaining = self.target.wait

    def update(self, *args):
        if self.wait_time_remaining:
            self.wait_time_remaining -= 1
            return

        # Use a little bit of geometry to figure out how far we can go
        # at our given speeed.  The right triangles formed between our
        # current location and the target and how far we can go at our
        # current speed are similar.  They have the same angle measures.
        # This means that we can determine the ratio between any two similar
        # sides 
        dx = self.target.x - self.rect.x
        dy = self.target.y - self.rect.y

        # The speed != 0 clause is to stop infinite recursion
        # for stationary Enemies
        if self.target.speed != 0 and dx == dy == 0:
            # We've reached the target
            self.target = next(self.target_gen)

            self.update(*args)

            # Go back to the beginning
            return

        dist_to_target = hypot(dx, dy)

        # This kicks in if there's a non-integer number of "speeds"
        # in the distance to travel.  FIXME: Distribute this number
        # throughout the travel distance rather than at the end
        speed = min(dist_to_target, self.target.speed)

        hypot_ratio = speed / dist_to_target

        tick_dx = hypot_ratio * dx
        tick_dy = hypot_ratio * dy

        self.rect.x += tick_dx
        self.rect.y += tick_dy

class Coin(Entity):
    def __init__(self, surface, coord):
        Entity.__init__(self, surface)
        self.rect.x = coord.x
        self.rect.y = coord.y

    def update(self, *args):
        pass

class Player(Entity):
    directionToVec = {
        '': (0, 0),
        'S': (1, 0),
        'N': (-1, 0),
        'W': (0, -1),
        'E': (0, 1),
        'SW': (0.707, -0.707),
        'SE': (0.707, 0.707),
        'NW': (-0.707, -0.707),
        'NE': (-0.707, 0.707),
    }

    def __init__(self, surface, x, y, speed):
        Entity.__init__(self, surface)
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def update(self, *args):
        direction, *rest = args

        try:
            dy, dx = Player.directionToVec[direction]
        except KeyError:
            print('Invalid direction')
            return
            
        self.rect.x += self.speed * dx
        self.rect.y += self.speed * dy

if __name__ == '__main__':
    pg.init()
    width, height = 1920, 1080
    screen = pg.display.set_mode((width, height))

    surf_enemy= pg.Surface((39, 39), flags=pg.SRCALPHA)
    pg.draw.circle(surf_enemy, pg.color.Color('blue'), (20, 20), 20)
    pg.draw.circle(surf_enemy, pg.color.Color('black'), (20, 20), 20, 5)

    surf_player = pg.Surface((29, 29), flags=pg.SRCALPHA)
    surf_player.fill(pg.color.Color('red'))
    pg.draw.rect(surf_player,
                 pg.color.Color('black'),
                 pg.Rect(0, 0, 29, 29),
                 7)

    player = Player(surf_player, 0, 0, 3)
    group_player = pg.sprite.Group(player)

    path1 = [PatrolPoint(10, 1, 0, 20),
             PatrolPoint(1010, 10, 0, 20),
             PatrolPoint(1010, 1010, 0, 20),
             PatrolPoint(10, 1010, 0, 20)]
                         
    enemy = Enemy(surf_enemy, path1)
    group_enemies = pg.sprite.Group(enemy)

    # Indices of relevant keys
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit(0)

        screen.fill(pg.color.Color('white'))
        group_player.draw(screen)
        group_enemies.draw(screen)

        pg.display.flip()

        # Handle moving the player, need to get keys
        state = pg.key.get_pressed()
        vert_direction = ''
        horiz_direction = ''
        
        # TODO: Provide better interface for keybindings
        if state[pg.K_w]:
            vert_direction = 'N'
        elif state[pg.K_s]:
            vert_direction = 'S'
            
        if state[pg.K_a]:
            horiz_direction = 'W'
        elif state[pg.K_d]:
            horiz_direction = 'E'
            
        group_player.update(vert_direction + horiz_direction)
        group_enemies.update()

        pg.time.wait(1000 // 60)
