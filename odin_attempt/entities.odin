package game

import "core:strings"
import "core:reflect"
import rl "vendor:raylib"

Dimentions :: struct { width, height: f32 }
Collisions :: struct { up, down, left, right: bool }

AnimationState :: enum {
    idle,
    jump,
    run,
    slide,
    wall_slide,
}

Entity :: struct {
    name:       string,
    pos:        [2]f32,
    size:       Dimentions,
    collisions: Collisions,
    velocity:   [2]f32,

    flip:              bool,
    animation_offset:  [2]f32,
    animation_state:   AnimationState,
    current_animation: ^Animation,

    derived: union {Player}
}

Player :: struct {
    using entity: ^Entity,
    time_in_air:  f32,
}

entity_init :: proc(t: ^Entity, $T: typeid, pos := [2]f32{0, 0}, size := [2]f32{0, 0}, animations: ^Animations) {
    t.pos = pos
    t.size = size
    t.velocity = [2]f32{0, 0}
    t.collisions = Collisions{false, false, false, false} 
    t.flip = false
    t.animation_offset = [2]f32{-3,-3}
    entity_set_animation_state(t, .idle, animations)
    t.derived = T{entity = t}
}

entity_new :: proc($T: typeid, pos := [2]f32{0, 0}, size := [2]f32{0, 0}, animations: ^Animations) -> ^Entity {
    t := new(Entity)
    entity_init(t, T, pos, size, animations)
    return t
}

entity_set_animation_state :: proc(using entity: ^Entity, state: AnimationState, animations: ^Animations) {
    if state != animation_state {
        animation_state = state
        key := strings.concatenate({"entities/", name, "/", reflect.enum_string(state)})
        current_animation = &animations[key]
    }
}

entity_get_rect :: proc(using entity: ^Entity) -> rl.Rectangle {
    return rl.Rectangle{ pos.x, pos.y, size.width, size.height } 
}

entity_update :: proc(using entity: ^Entity, movement := [2]f32{0, 0}) {
    collisions = Collisions{false, false, false, false}
    
    frame_movement := movement + velocity
    pos.x += frame_movement.x
    entity_rect := entity_get_rect(entity)

    pos.y += frame_movement.y
    entity_rect  = entity_get_rect(entity)

    if movement.x < 0 do flip = true
    else if movement.x > 0 && flip do flip = false

    switch e in derived {
        case Player:
    }
}

entity_render :: proc(using entity: ^Entity, offset := [2]f32{0, 0}) {
    image := animation_get_image(current_animation)
    direction: f32 = -1 if flip else 1
    rect := rl.Rectangle{0, 0, cast(f32)image.width * direction, cast(f32)image.height}
    render_pos := rl.Vector2{pos.x - offset.x + animation_offset.x, pos.y - offset.y + animation_offset.y}
    rl.DrawTextureRec(image^, rect, render_pos, rl.WHITE)
}

