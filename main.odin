package game

// https://www.raylib.com/examples.html
// @TODO: Virtual mouse position is wrong still.

import "core:fmt"
import "core:math"
import rl "vendor:raylib"
import "core:path/filepath"

FPS :: 60
GAME_SCREEN_WIDTH  :: 640
GAME_SCREEN_HEIGHT :: 480

FolderName  :: distinct string
ImageFolder :: distinct [dynamic]rl.Texture2D

main :: proc() {
    rl.SetConfigFlags({.WINDOW_RESIZABLE, .VSYNC_HINT})

    rl.InitWindow(860, 480, "Ninja")
    defer rl.CloseWindow()

    rl.SetWindowMinSize(GAME_SCREEN_WIDTH/2, GAME_SCREEN_HEIGHT/2)
    rl.SetTargetFPS(FPS)

    images := map[FolderName]ImageFolder{
        "grass" = load_images("tiles/grass"),
        "stone" = load_images("tiles/stone"),
        "clouds" = load_images("clouds"),
        "decor" = load_images("tiles/decor"),
        "large_decor" = load_images("tiles/large_decor"),
    }
    animations := map[FolderName]ImageFolder{
        "entities/player/idle" = load_images("entities/player/idle"),
        "entities/player/run" = load_images("entities/player/run"),
        "entities/player/jump" = load_images("entities/player/jump"),
        "entities/player/slide" = load_images("entities/player/slide"),
        "entities/player/wall_slide" = load_images("entities/player/wall_slide"),
        "particles/leaf" = load_images("particles/leaf"),
    }
    background_image := rl.LoadTexture("data/images/background.png")

    target := rl.LoadRenderTexture(GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT)

    for !rl.WindowShouldClose() {
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

        // Game screen, to be scaled.
        rl.BeginTextureMode(target)
        {
            rl.ClearBackground(rl.BLACK)
            rl.DrawTexture(background_image, 0, 0, rl.WHITE)
            rl.DrawCircle(cast(i32)virtual_mouse.x, cast(i32)virtual_mouse.y, 1, rl.RED)
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
            src := rl.Rectangle{0, cast(f32)target.texture.height/2, cast(f32)target.texture.width/2, cast(f32)-target.texture.height/2}
            dst := rl.Rectangle{leftover_width, leftover_height, GAME_SCREEN_WIDTH*scale, GAME_SCREEN_HEIGHT*scale}
            rl.DrawTexturePro(target.texture, src, dst, {0,0}, 0, rl.WHITE)
        }
        rl.EndDrawing()
    }
}
