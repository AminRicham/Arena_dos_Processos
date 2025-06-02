#ifndef SHARED_H
#define SHARED_H

#define WIDTH 40
#define HEIGHT 20
#define SHM_NAME "/arena_dos_robos"

typedef struct {
    char grid[HEIGHT][WIDTH];
    int game_over;
} shared_mem_t;

#endif