import json
import pygame

PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

ABOVE = (0, -1) 
BELOW = (0, 1) 
LEFT = (-1, 0) 
RIGHT = (1, 0) 
NEIGHBOR_OFFSETS = [LEFT, RIGHT, ABOVE, BELOW, (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)] # The neighbor includes diagonals

TILE_TOP_LEFT       = 0
TILE_TOP_MIDDLE     = 1
TILE_TOP_RIGHT      = 2
TILE_MIDDLE_RIGHT   = 3
TILE_BOTTOM_RIGHT   = 4
TILE_MIDDLE_MIDDLE0 = 5
TILE_BOTTOM_LEFT    = 6
TILE_MIDDLE_LEFT    = 7
TILE_MIDDLE_MIDDLE1 = 8


AUTOTILE_RULES = {
    tuple(sorted([RIGHT, BELOW]))              : TILE_TOP_LEFT,
    tuple(sorted([RIGHT, LEFT, BELOW]))        : TILE_TOP_MIDDLE,
    tuple(sorted([LEFT, BELOW]))               : TILE_TOP_RIGHT,
    tuple(sorted([LEFT, ABOVE, BELOW]))        : TILE_MIDDLE_RIGHT,
    tuple(sorted([LEFT, ABOVE]))               : TILE_BOTTOM_RIGHT,
    tuple(sorted([LEFT, RIGHT, ABOVE]))        : TILE_MIDDLE_MIDDLE0,
    tuple(sorted([RIGHT, ABOVE]))              : TILE_BOTTOM_LEFT,
    tuple(sorted([RIGHT, BELOW, ABOVE]))       : TILE_MIDDLE_LEFT,
    tuple(sorted([LEFT, RIGHT, ABOVE, BELOW])) : TILE_MIDDLE_MIDDLE1,
}

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
        json.dump({'tilemap' : self.tilemap, 'tile_size' : self.tile_size, 'offgrid' : self.offgrid_tiles}, f)
        f.close()

    def load_from_file(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def autotile(self):
        for key in self.tilemap:
            tile = self.tilemap[key]
            neighbors = set()
            for shift in [LEFT, RIGHT, ABOVE, BELOW]:
                neighbor_key = f"{tile['pos'][0] + shift[0]};{tile['pos'][1] + shift[1]}"
                if neighbor_key in self.tilemap:
                    if self.tilemap[neighbor_key]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_RULES):
                tile['variant'] = AUTOTILE_RULES[neighbors]

    def extract(self, id_pairs, search_offgrid=True, search_ongrid=True, keep=False):
        matches = []

        if search_offgrid:
            for tile in self.offgrid_tiles.copy():
                if (tile['type'], tile['variant']) in id_pairs:
                    matches.append(tile.copy())
                    matches[-1]['pos'][0] = int(matches[-1]['pos'][0])
                    matches[-1]['pos'][1] = int(matches[-1]['pos'][1])
                    if not keep:
                        self.offgrid_tiles.remove(tile)
        
        if search_ongrid:
            for key in self.tilemap:
                tile = self.tilemap[key]
                if (tile['type'], tile['variant']) in id_pairs:
                    matches.append(tile.copy())
                    matches[-1]['pos'] = matches[-1]['pos'].copy()
                    matches[-1]['pos'][0] *= self.tile_size
                    matches[-1]['pos'][1] *= self.tile_size
                    matches[-1]['pos'][0] = int(matches[-1]['pos'][0])
                    matches[-1]['pos'][1] = int(matches[-1]['pos'][1])
                    if not keep:
                        del self.tilemap[key]

        return matches
    
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
