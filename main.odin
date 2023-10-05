package game

import "core:fmt"
import "core:math"
import rl "vendor:raylib"
import "core:path/filepath"

FPS :: 60
GAME_SCREEN_WIDTH  :: 640
GAME_SCREEN_HEIGHT :: 480
RENDER_SCALE :: 2

FolderName  :: distinct string
ImageFolder :: distinct [dynamic]rl.Texture2D

main :: proc() {
    rl.SetConfigFlags({.WINDOW_RESIZABLE, .VSYNC_HINT})

    rl.InitWindow(860, 480, "Ninja")
    defer rl.CloseWindow()

    rl.SetWindowMinSize(GAME_SCREEN_WIDTH/2, GAME_SCREEN_HEIGHT/2)
    rl.SetTargetFPS(FPS)

    images := map[FolderName]ImageFolder {
        "grass" = load_images("tiles/grass"),
        "stone" = load_images("tiles/stone"),
        "clouds" = load_images("clouds"),
        "decor" = load_images("tiles/decor"),
        "large_decor" = load_images("tiles/large_decor"),
    }
    animations := map[FolderName]Animation {
        "entities/player/idle" = animation_load("entities/player/idle", image_duration=6, loop=true),
        "entities/player/run" = animation_load("entities/player/run", image_duration=4, loop=true),
        "entities/player/jump" = animation_load("entities/player/jump"),
        "entities/player/slide" = animation_load("entities/player/slide"),
        "entities/player/wall_slide" = animation_load("entities/player/wall_slide"),
        "particles/leaf" = animation_load("particles/leaf", image_duration=20, loop=true),
    }
    background_image := rl.LoadTexture("data/images/background.png")

    target := rl.LoadRenderTexture(GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT)

    variant: int = 0
    timer:   f32 = 0

    for !rl.WindowShouldClose() {
        dt := rl.GetFrameTime()
        screen_width, screen_height := cast(f32)rl.GetScreenWidth(), cast(f32)rl.GetScreenHeight()
        scale := math.min(screen_width/GAME_SCREEN_WIDTH, screen_height/GAME_SCREEN_HEIGHT)
        leftover_width, leftover_height := (screen_width - GAME_SCREEN_WIDTH*scale)/2, (screen_height - GAME_SCREEN_HEIGHT*scale)/2

        mouse := rl.GetMousePosition()
        virtual_mouse := rl.Vector2{
            ( mouse.x - leftover_width  ) / scale,
            ( mouse.y - leftover_height ) / scale,
        }
        virtual_mouse.x = math.clamp(virtual_mouse.x, 0, GAME_SCREEN_WIDTH)
        virtual_mouse.y = math.clamp(virtual_mouse.y, 0, GAME_SCREEN_HEIGHT)

        timer += dt 
        if timer > 1 do timer = 0
        if timer == 0 do variant = (variant+1) % len(images["grass"])

        rl.BeginTextureMode(target)
        {
            rl.ClearBackground(rl.BLACK)
            rl.DrawTexture(background_image, 0, 0, rl.WHITE)
            // now 
            rl.DrawTexture(images["grass"][variant],
                          cast(i32)(virtual_mouse.x/RENDER_SCALE - cast(f32)images["grass"][variant].width/2),
                          cast(i32)(virtual_mouse.y/RENDER_SCALE - cast(f32)images["grass"][variant].height/2),
                          rl.WHITE)
            rl.DrawCircle(cast(i32)(virtual_mouse.x/RENDER_SCALE), cast(i32)(virtual_mouse.y/RENDER_SCALE), 1, rl.RED)
        }
        rl.EndTextureMode()

        // Actual Window.
        rl.BeginDrawing()
        {
            rl.ClearBackground(rl.BLACK)

            // HUD.
            {
               rl.DrawFPS(cast(i32)screen_width-100, 0)
            }
            // Scaling and adjusting borders.
            src := rl.Rectangle{0, cast(f32)target.texture.height/RENDER_SCALE, cast(f32)target.texture.width/RENDER_SCALE, cast(f32)-target.texture.height/RENDER_SCALE}
            dst := rl.Rectangle{leftover_width, leftover_height, GAME_SCREEN_WIDTH*scale, GAME_SCREEN_HEIGHT*scale}
            rl.DrawTexturePro(target.texture, src, dst, {0,0}, 0, rl.WHITE)
        }
        rl.EndDrawing()
    }
}
