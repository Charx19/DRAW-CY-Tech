#include <stdio.h>
#include <string.h>
#include "graphic.h"

// Fonction pour créer un curseur
Cursor create_cursor(const char* color, int x, int y) {
    Cursor c;
    strcpy(c.color, color);
    c.x = x;
    c.y = y;
    return c;
}

int WinMain(int argc, char **argv) {
    init_graphics();  // Initialisation du système graphique

    // Créer un curseur rouge à (150, 150)
    Cursor cursor1 = create_cursor("red", 150, 150);
    add_cursor(cursor1.color, cursor1.x, cursor1.y);

    // Dessiner un cercle à partir du curseur (rayon de 50)
    add_circle(cursor1.x, cursor1.y, 50, cursor1.color);

    // Déplacer le curseur à (80, 80)
    Cursor cursor2 = create_cursor("red", 80, 80);
    add_cursor(cursor2.color, cursor2.x, cursor2.y);

    // Dessiner une ligne à partir de ce curseur vers (200, 200)
    add_line(cursor2.x, cursor2.y, 200, 200, "blue");

    SDL_Event event;
    int running = 1;

    // Boucle principale
    while (running) {
        // Gestion des événements
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = 0;
            }
            handle_mouse_selection(&event);
        }

        // Mettre à jour l'affichage
        highlight_selected_objects(); // Montre les objets sélectionnés si nécessaire
    }

    close_graphics();  // Fermer le système graphique
    return 0;
}
