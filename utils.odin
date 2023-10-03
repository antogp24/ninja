package game

import "core:fmt"
import "core:slice"
import "core:strings"
import "core:path/filepath"
import rl "vendor:raylib"


load_image :: proc(path: string, concat_base_image_path := true) -> rl.Texture2D {
    if concat_base_image_path {
        full_path, _ := strings.concatenate({"data/images/", path})
        return rl.LoadTexture(strings.clone_to_cstring(full_path))
    }
    return rl.LoadTexture(strings.clone_to_cstring(path))
}

load_images :: proc(path: string) -> ImageFolder {
    images := [dynamic]rl.Texture2D{}

    pattern := strings.concatenate({"data/images/", path, "/*.png"})
    folder_contents, _ := filepath.glob(pattern)

    reserve(&images, len(folder_contents))
    slice.sort(folder_contents[:])

    for image_name in folder_contents {
        when ODIN_OS == .Windows {
            slashed_image_name, _ := filepath.to_slash(image_name)
            append(&images, load_image(slashed_image_name, false))
        } else {
            append(&images, load_image(image_name, false))
        }
    }
    return cast(ImageFolder)images
}

util_test :: proc() {
    folder_contents, _ := filepath.glob("*")
    for path in folder_contents {
        path_slashed, _ := filepath.to_slash(path)
        fmt.println(path_slashed)
    }
}
