package game

import "core:slice"
import "core:strings"
import "core:strconv"
import "core:encoding/json"
import rl "vendor:raylib"

PHYSICS_TILES :=  map[string]int{"grass" = 0, "stone" = 1}
AUTOTILE_TYPES := map[string]int{"grass" = 0, "stone" = 1}

Offset :: distinct [2]int
ABOVE :: Offset{ 0, -1}
BELOW :: Offset{ 0,  1}
LEFT  :: Offset{-1,  0}
RIGHT :: Offset{ 1,  0}
NEIGHBOR_OFFSETS :: []Offset{LEFT, RIGHT, ABOVE, BELOW, {0, 0}, {-1, -1}, {1, -1}, {-1, 1}, {1, 1}} // includes diagonals and (0, 0)

TileVariant :: enum {
    TOP_LEFT,
    TOP_MIDDLE,
    TOP_RIGHT,
    MIDDLE_RIGHT,
    BOTTOM_RIGHT,
    MIDDLE_MIDDLE0,
    BOTTOM_LEFT,
    MIDDLE_LEFT,
    MIDDLE_MIDDLE1,
}

AUTOTILE_RULES := map[string][]Offset{
    "TOP_LEFT"       = []Offset{BELOW, RIGHT},
    "TOP_MIDDLE"     = []Offset{LEFT,  BELOW, RIGHT},
    "TOP_RIGHT"      = []Offset{LEFT,  BELOW},
    "MIDDLE_RIGHT"   = []Offset{LEFT,  ABOVE, BELOW},
    "BOTTOM_RIGHT"   = []Offset{LEFT,  ABOVE},
    "MIDDLE_MIDDLE0" = []Offset{LEFT,  ABOVE, RIGHT},
    "BOTTOM_LEFT"    = []Offset{ABOVE, RIGHT},
    "MIDDLE_LEFT"    = []Offset{ABOVE, BELOW, RIGHT},
    "MIDDLE_MIDDLE1" = []Offset{LEFT,  ABOVE, BELOW, RIGHT},
}

TileData :: struct { type: string, variant: int, pos: [2]int }
Tilemap  :: struct {
    tile_size: int,
    tilemap_data: map[string]TileData,
    offgrid_tiles: [dynamic]TileData,
}

tilemap_get_key :: proc(x, y: int) -> string {
    buf1, buf2: [4]byte
    x_s := strconv.itoa(buf1[:], x)
    y_s := strconv.itoa(buf2[:], y)
    s, _ := strings.concatenate({x_s, ";", y_s})
    return s
}

tilemap_init :: proc(using tilemap: ^Tilemap, _tile_size := 16) {
    tile_size = _tile_size

    for i in 0..<10 {
        tilemap_data[tilemap_get_key(i+3, 10)] = {"grass", 1, {i+3, 10}}
        tilemap_data[tilemap_get_key(10, i+5)] = {"stone", 1, {10, i+5}}
    }
}

// tilemap_save_to_file :: proc(using tilemap: ^Tilemap, path: string) {
//     f = open(path, 'w')
//     json.dump(struct{tilemap_data, tile_size, offgrid_tiles}, f)
//     f.close()
// }
//
// tilemap_load_from_file :: proc(using tilemap: ^Tilemap, path: string) {
//     f = open(path, 'r')
//     map_data = json.load(f)
//     f.close()
//
//     tilemap_data = map_data["tilemap_data"]
//     tile_size = map_data["tile_size"]
//     offgrid_tiles = map_data["offgrid"]
// }

tilemap_autotile :: proc(using tilemap: ^Tilemap) {

    neighbors_in_autotile_rules :: proc(neighbors: ^[dynamic]Offset) -> bool {
        result := false
        i := 0
        for _, rule in AUTOTILE_RULES {
            if slice.equal(rule, neighbors^) do result = true
            i += 1
        }
        return result
    }

    for key in tilemap_data {
        tile := tilemap_data[key]
        neighbors: [dynamic]Offset

        offsets :: [4]Offset{LEFT, RIGHT, ABOVE, BELOW}
        for shift in offsets {
            neighbor_key := tilemap_get_key(tile.pos.x + shift.x, tile.pos.y + shift.y)
            if neighbor_key in tilemap_data {
                if tilemap_data[neighbor_key].type == tile.type {
                    append(&neighbors, shift)
                }
            }
        }
        // slice.sort(neighbors)
        if (tile.type in AUTOTILE_TYPES) && neighbors_in_autotile_rules(&neighbors) {
            tile.variant = AUTOTILE_RULES[neighbors]
        }
    }
}

ID_Pair :: struct {type: string, variant: int}
tilemap_extract :: proc(using tilemap: ^Tilemap, id_pairs: []ID_Pair, search_offgrid := true, search_ongrid := true, keep := false) -> [dynamic]TileData {
    matches: [dynamic]TileData

    if search_offgrid {
        for tile, index in offgrid_tiles {
            if slice.contains(id_pairs, ID_Pair{tile.type, tile.variant}) {
                append(&matches, tile)
                matches[len(matches)-1].pos.x = cast(int)(matches[len(matches)-1].pos.x)
                matches[len(matches)-1].pos.y = cast(int)(matches[len(matches)-1].pos.y)
                if !keep {
                    unordered_remove(&offgrid_tiles, index)
                }
            }
        }
    }
    
    if search_ongrid {
        for key in tilemap_data {
            tile := tilemap_data[key]
            if slice.contains(id_pairs, ID_Pair{tile.type, tile.variant}) {
                append(&matches, tile)
                matches[len(matches)-1].pos = matches[len(matches)-1].pos
                matches[len(matches)-1].pos.x *= tile_size
                matches[len(matches)-1].pos.y *= tile_size
                matches[len(matches)-1].pos.x = cast(int)(matches[len(matches)-1].pos.x)
                matches[len(matches)-1].pos.y = cast(int)(matches[len(matches)-1].pos.y)
                if !keep {
                    delete_key(&tilemap_data, key)
                }
            }
        }
    }

    return matches
}

tilemap_tiles_around :: proc(using tilemap: ^Tilemap, pos := [2]int{0, 0}) -> [dynamic]TileData {
    tiles: [dynamic]TileData
    tile_pos := [2]int{(int)(pos.x / tile_size), (int)(pos.y / tile_size)}

    for offset in NEIGHBOR_OFFSETS {
        key := tilemap_get_key(tile_pos.x + offset.x, tile_pos.y + offset.y)
        if key in tilemap_data do append(&tiles, tilemap_data[key])
    }
    return tiles
}

tilemap_tile_rects_around :: proc(using tilemap: ^Tilemap, pos := [2]int{0, 0}) -> [dynamic]rl.Rectangle {
    rects: [dynamic]rl.Rectangle
    tile_pos := [2]int{(int)(pos.x / tile_size), (int)(pos.y / tile_size)}

    for offset in NEIGHBOR_OFFSETS {
        key := tilemap_get_key(tile_pos.x + offset.x, tile_pos.y + offset.y)
        if key in tilemap_data {
            tile := tilemap_data[key]
            if tile.type in PHYSICS_TILES {
                append(&rects, rl.Rectangle{f32(tile.pos.x * tile_size), f32(tile.pos.y * tile_size), f32(tile_size), f32(tile_size)})
            }
        }
    }
    return rects
}

tilemap_render :: proc(using tilemap: ^Tilemap, images: ^Images, offset := [2]f32{0, 0}, display_width: f32, display_height: f32) {
    for tile in offgrid_tiles {
        pos := [2]i32{
            cast(i32)(cast(f32)tile.pos.x - offset.x),
            cast(i32)(cast(f32)tile.pos.y - offset.y)
        }
        rl.DrawTexture(images^[tile.type][tile.variant], pos.x, pos.y, rl.WHITE)
    }
    
    // Coordinates in pixels
    screen_start := [2]f32{offset.x / f32(tile_size), offset.y / f32(tile_size)}
    screen_end := [2]f32{(offset.x + display_width) / f32(tile_size), (offset.y + display_height) / f32(tile_size)}
    
    // More efficient way of looking up for tiles
    for y := screen_start.y; y < screen_end.y + 1; y += 1 {
        for x := screen_start.x; x < screen_end.x + 1; x += 1 {
            key := tilemap_get_key(cast(int)x, cast(int)y)
            if key in tilemap_data {
                tile := tilemap_data[key]
                rl.DrawTexture(images^[tile.type][tile.variant],
                               cast(i32)(f32(tile.pos.x * tile_size) - offset.x),
                               cast(i32)(f32(tile.pos.y * tile_size) - offset.y),
                               rl.WHITE)
            }
        }
    }
}

