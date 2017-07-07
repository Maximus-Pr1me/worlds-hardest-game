#!/usr/bin/env python3

import pygame as pg
import entities
from entities import PatrolPoint
import sys

# To start, just begin game at level 1

# Create surfaces for player, blue balls, grid, and map outline (?)

# Load list of entities (player, blue balls)

# Initialize default entities
# Blue circle, black stroke, radius 15
surf_enemy = pg.Surface((29, 29), flags=pg.SRCALPHA)
pg.draw.circle(surf_enemy, pg.color.Color('blue'), (15, 15), 15)
pg.draw.circle(surf_enemy, pg.color.Color('black'), (15, 15), 15, 5)

# yellow circle, black stroke, radius 20
surf_coin = pg.Surface((29, 29), flags=pg.SRCALPHA)
pg.draw.circle(surf_coin, pg.color.Color('yellow'), (15, 15), 15)
pg.draw.circle(surf_coin, pg.color.Color('black'), (15, 15), 15, 4)

# Red square, black stroke
surf_player = pg.Surface((27, 27), flags=pg.SRCALPHA)
surf_player.fill(pg.color.Color('red'))
pg.draw.rect(surf_player,
             pg.color.Color('black'),
             pg.Rect(0, 0, 27, 27),
             7)

surf_boundary = pg.Surface((40, 40))
surf_boundary.fill(pg.color.Color('purple'))

# TODO: Handle Boundary and SafeZone surfaces. Patterns?

############
#   Main   # 
############

if __name__ == '__main__':
    pg.init()
    width, height = 1920, 1080
    screen = pg.display.set_mode((width, height))

    # This code can be used to initialize a level
    player = entities.Player(surf_player, 50, 50, 5)
    enemy = entities.Enemy(surf_enemy,
                           [PatrolPoint(10, 10, 0, 1),
                            PatrolPoint(110, 10, 0, 1)])
    coin = entities.Coin(surf_coin, 600, 100)

    bounds = []
    # Create boundaries around outer border of map
    num_tiles_x = 1920 // 40
    num_tiles_y = 1080 // 40
    for i in range(num_tiles_x):
        for j in range(num_tiles_y):
            if i == 0 or i == num_tiles_x-1 or j == 0 or j == num_tiles_y-1:
                bounds.append(entities.Boundary(surf_boundary, i*40, j*40))

    group_player = pg.sprite.Group(player)
    group_enemies = pg.sprite.Group(enemy)
    group_coins = pg.sprite.Group(coin)
    group_bounds = pg.sprite.Group(bounds)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit(0)

        screen.fill(pg.Color('white'))
        group_player.draw(screen)
        group_enemies.draw(screen)
        group_coins.draw(screen)
        group_bounds.draw(screen)

        pg.display.flip()


        # Check for collision with enemies
        collided_enemy = pg.sprite.groupcollide(group_player,
                                                group_enemies,
                                                False,
                                                False,
                                                entities.collide_rect_circle)

        if collided_enemy:
            # We have a collision -> Respawn the player,
            #                        incrememnt death counter
            print('{} Collided'.format(pg.time.get_ticks()))

        # Check for collision with coins
        collided_coin = pg.sprite.groupcollide(group_player,
                                               group_coins,
                                               False,
                                               True,
                                               entities.collide_rect_circle)

        # Check for collision with spawn points


        
        # Handle user's keyboard input
        # TODO: Isolate this to an interface
        key_state = pg.key.get_pressed()
        vert_direction, horiz_direction = '', ''

        # TODO: Provide better interface for keybindings
        # i.e. support arrow keys, hjkl, etc.
        if key_state[pg.K_w]:
            vert_direction = 'N'
        elif key_state[pg.K_s]:
            vert_direction = 'S'
            
        if key_state[pg.K_a]:
            horiz_direction = 'W'
        elif key_state[pg.K_d]:
            horiz_direction = 'E'

        # Player's position is updated

        group_player.update(vert_direction + horiz_direction)

        # Check for collision with bounds
        collided_bounds = pg.sprite.groupcollide(group_player,
                                                 group_bounds,
                                                 False,
                                                 False)
        # This model is too simple, Instead I should force the
        # player into the nearest in-bounds point. How do I do
        # that? 
        if collided_bounds:
            # Force the player back in bounds

            group_player.update(vert_direction + horiz_direction)

        group_enemies.update()
        group_coins.update()

        pg.time.wait(1000 // 60)
