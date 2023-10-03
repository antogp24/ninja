import sys
import math
import random
import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle

pygame.init()

pygame.display.set_caption('ninja game')
screen = pygame.display.set_mode((640, 480))
display = pygame.Surface((320, 240))
RENDER_SCALE = 2

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
    'particles/leaf' : Animation(load_images('particles/leaf'), image_duration=20, loop=True)
}

clouds = Clouds(images['clouds'], count=16)
tilemap = Tilemap(tile_size=16)
player = Player((50, 50), (8, 15), animations)

scroll = [0, 0]

try:
    tilemap.load_from_file('map.json')
except FileNotFoundError:
    pass

leaf_spawners = []
for tree in tilemap.extract([('large_decor', 2)], search_ongrid=False, keep=True):
    width, height = images['large_decor'][2].get_size()
    rect = pygame.Rect(tree['pos'][0], tree['pos'][1] + height//16, width, height//3)
    leaf_spawners.append(rect)
particles = []

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

    for particle in particles.copy():
        kill = particle.update()
        particle.render(display, offset=render_scroll)
        if particle.type == 'leaf':
            particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
        if kill: particles.remove(particle)
    
    for rect in leaf_spawners:
        if random.random() * 49999 < rect.width * rect.height:
            spawn_pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
            particle = Particle(animations, 'leaf', spawn_pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20))
            particles.append(particle)
    
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
                player.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                movement[0] = False
            if event.key == pygame.K_RIGHT:
                movement[1] = False
    
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.update()
    clock.tick(60)
