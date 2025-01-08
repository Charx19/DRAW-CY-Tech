#include <stdio.h>
#include <string.h>
#include "graphic.h"


// Fonction pour cr�er un curseur
Cursor create_cursor(const char* color, int x, int y) {
    Cursor c;
    strcpy(c.color, color);
    c.x = x;
    c.y = y;
    return c;
}

int WinMain(int argc, char **argv) {
    init_graphics();  // Initialisation du syst�me graphique
    int current_x, current_y;
    char current_color[20] = "";
    int a = 0;
    SDL_Event event;
    int running = 1;
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = 0;
            }
            handle_mouse_selection(&event);
        }
    }
    close_graphics();
    return 0;
}