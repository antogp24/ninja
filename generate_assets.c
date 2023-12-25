#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#if _WIN32
#    define WIN32_LEAN_AND_MEAN
#    include <windows.h>
#endif

typedef struct {
    char *str;
    int length;
} string;

typedef enum {
    ListingTypeDirectory,
    ListingTypeFile,
}ListingType;

typedef struct SLLnode SLLnode;
struct SLLnode {
    string value;
    ListingType type;
    SLLnode *next;
};

void sll_append(SLLnode **head, char *value, int value_length, ListingType type) {
    SLLnode *temp = malloc(sizeof(SLLnode));
    temp->value.str = malloc(value_length+1);
    temp->value.length = value_length;
    temp->type = type;
    strcpy(temp->value.str, value);
    temp->next = *head;
    *head = temp;
}

void sll_log(SLLnode *head) {
    for (SLLnode *node = head; node != NULL; node = node->next) {
        printf("Listing: %s, Count: %i, Type: %i\n", node->value.str, node->value.length, node->type);
    }
}

void sll_destroy(SLLnode *head) {
    for (SLLnode *node = head, *next = NULL; node != NULL; node = next) {
        next = node->next;
        free(node);
    }
}

typedef struct {
    SLLnode *listings;
    uint32_t count;
} Folder;

Folder get_dir_names(char *path, char *wildcard) {
    Folder folder = {0};

    char name[MAX_PATH] = {0};
    sprintf(name, "%s%s", path, wildcard);

    WIN32_FIND_DATA FindFileData;
    HANDLE hFind = FindFirstFile(name, &FindFileData);
    
    if (hFind == INVALID_HANDLE_VALUE) {
        printf("Path not found: %s\n", path);
        exit(1);
    }
    do {
        if (FindFileData.cFileName[0] == '.') {
            continue;
        }
        ListingType type = 0;
        if (FindFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            type = ListingTypeDirectory;
        }
        else {
            type = ListingTypeFile;
        }
        sll_append(&folder.listings, FindFileData.cFileName, strlen(FindFileData.cFileName), type);
        folder.count++;
    } while(FindNextFile(hFind, &FindFileData));

    FindClose(hFind);

    return folder;
}

typedef struct {
    Folder *folders;
    int count;
} FolderArray;

FolderArray get_tiles(char *path) {
    Folder root = get_dir_names(path, "*");
    FolderArray tiles = {0};
    tiles.folders = malloc(root.count*sizeof(SLLnode));
    tiles.count = 0;

    for (SLLnode *node = root.listings; node != NULL; node = node->next) {
        char name[MAX_PATH] = {0};
        sprintf(name, "%s%s/", path, node->value.str);
        tiles.folders[tiles.count] = get_dir_names(name, "*.png");
        tiles.count++;
    }
    sll_destroy(root.listings);
    return tiles;
}

int main(int argc, char *argv[]) {
    Folder misc = get_dir_names("data/images/", "*.png");
    Folder clouds = get_dir_names("data/images/clouds/", "*.png");
    FolderArray tiles = get_tiles("data/images/tiles/");

    printf("Misc:\n");
    printf("-----------------\n");
    sll_log(misc.listings);
    printf("\nClouds:\n");
    printf("-----------------\n");
    sll_log(clouds.listings);
    printf("\n");

    for (int i = 0; i < tiles.count; i++) {
        printf("Folder %i\n", i);
        for (SLLnode *node = tiles.folders[i].listings; node != NULL; node = node->next) {
            printf("%s\n", node->value.str);
        }
    }


    sll_destroy(misc.listings);
    sll_destroy(clouds.listings);
}
