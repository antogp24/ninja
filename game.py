import sys

import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds

pygame.init()

pygame.display.set_caption('ninja game')
screen = pygame.display.set_mode((640, 480))
display = pygame.Surface((320, 240))

clock = pygame.time.Clock()

movement = [False, False]

images = {
    'decor': load_images('tiles/decor'),
    'grass': load_images('tiles/grass'),
    'large_decor': load_images('tiles/large_decor'),
    'stone': load_images('tiles/stone'),
    'player': load_image('entities/player.png'),
    'background': load_image('background.png'),
    'clouds': load_images('clouds'),
}

animations = {
    'entities/player/idle' : Animation(load_images('entities/player/idle'), image_duration=6, loop=True),
    'entities/player/run' : Animation(load_images('entities/player/run'), image_duration=4, loop=True),
    'entities/player/jump' : Animation(load_images('entities/player/jump')),
    'entities/player/slide' : Animation(load_images('entities/player/slide')),
    'entities/player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
}

clouds = Clouds(images['clouds'], count=16)
tilemap = Tilemap(tile_size=16)
player = Player((50, 50), (8, 15), animations)

scroll = [0, 0]

while True:
    display.blit(images['background'], (0, 0))
    
    scroll[0] += (player.rect().centerx - display.get_width() / 2 - scroll[0]) / 30
    scroll[1] += (player.rect().centery - display.get_height() / 2 - scroll[1]) / 30
    render_scroll = (int(scroll[0]), int(scroll[1]))
    
    clouds.update()
    clouds.render(display, offset=render_scroll)
    
    tilemap.render(display, images, offset=render_scroll)
    
    player.update(tilemap, (movement[1] - movement[0], 0))
    player.render(display, images, offset=render_scroll)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                movement[0] = True
            if event.key == pygame.K_RIGHT:
                movement[1] = True
            if event.key == pygame.K_UP:
                player.velocity[1] = -3
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                movement[0] = False
            if event.key == pygame.K_RIGHT:
                movement[1] = False
    
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.update()
    clock.tick(60)
