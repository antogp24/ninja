import sys
import math
import pygame

from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap

pygame.init()

RENDER_SCALE = 2
pygame.display.set_caption('Level Editor')
screen = pygame.display.set_mode((640, 480))
display = pygame.Surface((320, 240))

clock = pygame.time.Clock()

images = {
    'grass': load_images('tiles/grass'),
    'stone': load_images('tiles/stone'),
    'decor': load_images('tiles/decor'),
    'large_decor': load_images('tiles/large_decor'),
}

camera_pos = [0, 0]
scroll = [0, 0]
scroll_lag = 10
camera_speed = [0, 0]
CAMERA_SPEED = 16/RENDER_SCALE
movement = [False, False, False, False]

tilemap = Tilemap(tile_size=16)
tile_list = list(images)
tile_group = 0 
tile_variant = 0
on_grid = True

try:
    tilemap.load_from_file('map.json')
except FileNotFoundError:
    pass

left_clicking = False
middle_clicking = False
right_clicking = False
pressing_shift = False
pressing_alt = False
pressing_ctrl = False
pressing_space = False

while True:
    display.fill((0, 0, 0))

    mouse_position = pygame.mouse.get_pos()
    mx, my = (mouse_position[0] / RENDER_SCALE, mouse_position[1] / RENDER_SCALE)

    # moving the camera with the arrow keys
    camera_pos[0] += (movement[1] - movement[0]) * CAMERA_SPEED
    camera_pos[1] += (movement[3] - movement[2]) * CAMERA_SPEED

    # moving the camera with the mouse
    if middle_clicking:
        camera_pos[0] += (mx - display.get_width()/2) / display.get_width() * RENDER_SCALE * CAMERA_SPEED
        camera_pos[1] += (my - display.get_height()/2) / display.get_height() * RENDER_SCALE * CAMERA_SPEED
    scroll[0] += (camera_pos[0] - scroll[0]) / scroll_lag
    scroll[1] += (camera_pos[1] - scroll[1]) / scroll_lag

    render_scroll = (int(scroll[0]), int(scroll[1]))

    # rendering the tilemap
    tilemap.render(display, images, offset=render_scroll)
    
    # rendering the current tile to place down
    folder = tile_list[tile_group]
    folder_images = images[folder]
    current_tile = folder_images[tile_variant].copy()
    current_tile.set_alpha(100)
    display.blit(current_tile, (5, 5))

    # placing tiles
    tile_pos = (mx + scroll[0], my + scroll[1])
    snapped_tile_pos = (int(tile_pos[0] // tilemap.tile_size), int(tile_pos[1] // tilemap.tile_size))
    offgrid_tile_pos = (tile_pos[0] - current_tile.get_width()/2, tile_pos[1] - current_tile.get_height())

    # adding tiles to the tilemap dictonaries
    if left_clicking and on_grid:
            key = f'{snapped_tile_pos[0]};{snapped_tile_pos[1]}'
            tilemap.tilemap[key] = {'type': folder, 'variant': tile_variant, 'pos': snapped_tile_pos}
    if right_clicking:
        if on_grid:
            key = f'{snapped_tile_pos[0]};{snapped_tile_pos[1]}'
            if key in tilemap.tilemap:
                del tilemap.tilemap[key]
        elif not on_grid:
            for tile in tilemap.offgrid_tiles.copy():
                rect = pygame.Rect(tile['pos'][0] - scroll[0], tile['pos'][1] - scroll[1], current_tile.get_width(), current_tile.get_height())
                if rect.collidepoint(mx, my):
                    tilemap.offgrid_tiles.remove(tile)
    
    # rendering transparent current tile
    if on_grid:
        display.blit(current_tile, (snapped_tile_pos[0] * tilemap.tile_size - render_scroll[0], snapped_tile_pos[1] * tilemap.tile_size - render_scroll[1]))
    elif not on_grid:
        display.blit(current_tile, (offgrid_tile_pos[0] - render_scroll[0], offgrid_tile_pos[1] - render_scroll[1]))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                left_clicking = True
                if not on_grid:
                    tilemap.offgrid_tiles.append({'type': folder, 'variant': tile_variant, 'pos' : offgrid_tile_pos})
            if event.button == 2:
                middle_clicking = True
            if event.button == 3:
                right_clicking = True
            
            # Scrolling up and down
            if pressing_alt:
                if event.button == 4:
                    tile_group -= 1
                    if tile_group < 0: tile_group = len(tile_list)-1
                    tile_variant = 0
                if event.button == 5:
                    tile_group += 1
                    if tile_group > len(tile_list)-1: tile_group = 0
                    tile_variant = 0
            elif pressing_shift or pressing_ctrl:
                if event.button == 4:
                    tile_variant -= 1
                    if tile_variant < 0: tile_variant = len(folder_images)-1
                if event.button == 5:
                    tile_variant += 1
                    if tile_variant > len(folder_images)-1: tile_variant = 0
            else:
                if event.button == 4:
                    tile_group -= 1
                    if on_grid:
                        if tile_group < 0: tile_group = (len(tile_list)-2)-1
                    elif not on_grid:
                        if tile_group < 2: tile_group = len(tile_list)-1
                    tile_variant = 0
                if event.button == 5:
                    tile_group += 1
                    if on_grid:
                        if tile_group > (len(tile_list)-2)-1: tile_group = 0
                    elif not on_grid:
                        if tile_group > len(tile_list)-1: tile_group = 2
                    tile_variant = 0

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                left_clicking = False 
            if event.button == 2:
                middle_clicking = False
            if event.button == 3:
                right_clicking = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                movement[0] = True
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                movement[1] = True
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                movement[2] = True
            if event.key == pygame.K_DOWN or event.key == pygame.K_s and not pressing_ctrl:
                movement[3] = True
            if event.key == pygame.K_LSHIFT:
                pressing_shift = True
            if event.key == pygame.K_LCTRL:
                pressing_ctrl = True
            if event.key == pygame.K_LALT:
                pressing_alt = True
            if event.key == pygame.K_SPACE:
                pressing_space = True
            if event.key == pygame.K_s and pressing_ctrl:
                tilemap.save_to_file('map.json')
            if event.key == pygame.K_g:
                on_grid = not on_grid
                if on_grid:
                    tile_group = 0
                elif not on_grid:
                    tile_group = 2
                tile_variant = 0
            if event.key == pygame.K_t:
                tilemap.autotile()
            if event.key == pygame.K_0:
                for i in range(len(scroll)):
                    scroll[i] = 0
                    camera_pos[i] = 0

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                movement[0] = False
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                movement[1] = False
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                movement[2] = False
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                movement[3] = False
            if event.key == pygame.K_LSHIFT:
                pressing_shift = False
            if event.key == pygame.K_LCTRL:
                pressing_ctrl = False
            if event.key == pygame.K_LALT:
                pressing_alt = False
            if event.key == pygame.K_SPACE:
                pressing_space = False
    
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.update()
    clock.tick(60)
