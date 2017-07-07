#!/usr/bin/env python3

import pygame as pg
import sys
from math import hypot
from itertools import cycle

from collections import namedtuple, defaultdict

#########################
#  Enitity Definitions  #
#########################
class Entity(pg.sprite.Sprite):
    """
    Generic entity class that all entities inherit from
    """

    def __init__(self, surface):
        pg.sprite.Sprite.__init__(self)

        # Need to define image so group.draw will draw it
        self.image = surface

        # Will get an enclosing rectangle
        self.rect = self.image.get_rect()

PatrolPoint = namedtuple('PatrolPoint', ['x', 'y', 'wait', 'speed'])
class Enemy(Entity):
    """
    An enemy in the game.  It looks like a blue ball and will follow a path
    given to it.  When the player collides with an enemy they die.
    """

    def __init__(self, surface, path):
        Entity.__init__(self, surface)

        self.target_gen = cycle(path)
        self.target = next(self.target_gen)

        self.rect.x = path[0].x
        self.rect.y = path[0].y

        self._rad = self.rect.width // 2

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
    """
    A coin that the player must collect.  They cannot beat the level until
    they collect every coin in the level.  When the player dies all of the
    coins respawn and must be collected again.  These are stationary.
    """
    
    def __init__(self, surface, x, y):
        Entity.__init__(self, surface)
        self.rect.x = x
        self.rect.y = y
        self._rad = self.rect.width // 2

    def update(self, *args):
        pass

class Player(Entity):
    """
    The player's character.  The player has full control over it and can move
    it in 8 directions using the appropriate keys.
    """
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

        if rest:
            location_update_x, location_update_y, *rest = rest
            self.rect.x = location_update_x
            self.rect.y = location_update_y
            return

        try:
            dy, dx = Player.directionToVec[direction]
        except KeyError:
            print('Invalid direction')
            return
            
        self.rect.x += self.speed * dx
        self.rect.y += self.speed * dy

class SafeZone(Entity):
    """
    A rectangle on the map.  When the player enters this area their spawn point
    will be reset to this location, unless it's the final one for the level.
    In that case, if the player enters /and/ they've collected all the coins,
    then the level ends.  Otherwise nothing happens.

    Note: enemies should /never/ enter a safe zone.  The engine will not enforce
          this, but that's the way it should be.
    """

    def __init__(self, surface, x, y):
        Entity.__init__(self, surface)
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        pass

class Boundary(Entity):
    """
    Out of bounds part of the map.  The player will not be allowed to enter
    this area.  This will be a single rectangle, all of out of bounds will
    usually be a collection of these rectangles.
    """
    def __init__(self, surface, x, y):
        Entity.__init__(self, surface)
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        pass

# Okay, there are entities that are locked to a grid.  I'm making a
# container class for these things because the complexity's getting
# a little too great in the scripts
class Tile(Entity):
    """
    Entities that are aligned to a grid in each of the levels.
    """

    def __init__(self, surface, x, y, side_length):
        Entity.__init__(self, surface)
        self.rect.x = x * side_length
        self.rect.y = y * side_length
        self.rect.width = side_length
        self.rect.height = side_length

    def update(self, *args):
        pass

class Wall(Tile):
    """
    Out of bounds.  Player should never be able to enter this area
    """

    def __init__(self, surface, x, y, side_length):
        Tile.__init__(surface, x, y, side_length)

class SafeZone(Tile):
    """
    Zone the player can enter.  The highest priority SafeZone that the
    player has visited will be the player's spawn point should they die
    """
    
    def __init__(self, surface, x, y, side_length, priority):
        Tile.__init__(surface, x, y, side_length)
        self.priority = priority

class LevelGrid:
    """
    Container class for the grid layout of a level
    """

#########################
#  Collision Detection  # 
#########################
# TODO: These should be members of the Entity class

def clamp(x, a, b):
    return min(max(x, a), b)

def collide_circle_rect(circle_sprite, rect_sprite):
    # Find closest point to the circle in the rectangle
    circle = circle_sprite.rect
    circle_rad = circle_sprite._rad
    rect = rect_sprite.rect

    closest_x = clamp(circle.centerx, rect.left, rect.right)
    closest_y = clamp(circle.centery, rect.top, rect.bottom)

    # Calculate distance between circle's center and closest point
    distance_x = circle.centerx - closest_x
    distance_y = circle.centery - closest_y

    # If distance is less than the circle's radius, there's an intersection
    distance_squared = distance_x**2 + distance_y**2

    return distance_squared < circle_rad**2

def collide_rect_circle(rect, circle):
    return collide_circle_rect(circle, rect)
