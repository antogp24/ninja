import json
import pygame

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, tile_size=16):
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        for i in range(10):
            self.tilemap[f'{i+3};10'] = {'type': 'grass', 'variant': 1, 'pos': (i+3, 10)}
            self.tilemap[f'10;{i+5}'] = {'type': 'stone', 'variant': 1, 'pos': (10, i+5)}
    
    def save_to_file(self, path):
        f = open(path, 'w')
        json.dump({'tilemap' : self.tilemap, 'tile_size' : self.tile_size, 'offgrid_tiles' : self.offgrid_tiles}, f)
        f.close()
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap: tiles.append(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self, surf, images, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(images[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        # More efficient way of looking up for tiles
        for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
            for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
                key = f"{x};{y}"
                if key in self.tilemap:
                    tile = self.tilemap[key]
                    folder = images[tile['type']]
                    variant = tile['variant']
                    surf.blit(folder[variant], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

        
        # for loc in self.tilemap:
        #     tile = self.tilemap[loc]
        #     folder = images[tile['type']]
        #     variant = tile['variant']
        #     surf.blit(folder[variant], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))