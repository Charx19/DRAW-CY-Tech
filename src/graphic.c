#include <SDL.h>
#include "graphic.h"
#include <stdio.h>
#include <math.h>
#include <string.h>

// Variables globales pour gérer SDL
static SDL_Window *window = NULL;
static SDL_Renderer *renderer = NULL;
static int current_x = 0, current_y = 0; // Position actuelle du curseur

void init_graphics() {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "Erreur SDL: %s\n", SDL_GetError());
        return;
    }
    window = SDL_CreateWindow("Graphics", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, SDL_WINDOW_SHOWN);
    if (!window) {
        fprintf(stderr, "Erreur création fenêtre: %s\n", SDL_GetError());
        SDL_Quit();
        return;
    }
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        fprintf(stderr, "Erreur création renderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return;
    }
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE); // Fond noir
    SDL_RenderClear(renderer);
    SDL_RenderPresent(renderer);
}

void close_graphics() {
    if (renderer) SDL_DestroyRenderer(renderer);
    if (window) SDL_DestroyWindow(window);
    SDL_Quit();
}

void move_to(Cursor c, int x, int y) {
    // Mettre à jour la position du curseur
    current_x = x;
    current_y = y;
    // Redessiner le curseur à la nouvelle position
    cursor(c.color, current_x, current_y, 10);
}

void line_to(Cursor c, int x, int y) {
    // Utiliser la couleur du curseur pour la ligne
    if (strcmp(c.color, "red") == 0) {
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, SDL_ALPHA_OPAQUE); // Rouge
    } else if (strcmp(c.color, "green") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, SDL_ALPHA_OPAQUE); // Vert
    } else if (strcmp(c.color, "blue") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE); // Bleu
    } else {
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE); // Blanc par défaut
    }

    // Tracer la ligne de la position actuelle à la nouvelle position
    SDL_RenderDrawLine(renderer, current_x, current_y, x, y);
    SDL_RenderPresent(renderer);

    // Mettre à jour la position actuelle après le dessin de la ligne
    current_x = x;
    current_y = y;

    // Afficher le curseur à la nouvelle position avec la couleur courante
    cursor(c.color, current_x, current_y, 10); // Afficher le curseur dans la couleur actuelle
}

void circle(Cursor c, int radius) {
    int x0 = current_x, y0 = current_y;
    int x = radius, y = 0;
    int err = 0;

    // Utiliser la couleur du curseur pour le cercle
    if (strcmp(c.color, "red") == 0) {
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, SDL_ALPHA_OPAQUE); // Rouge
    } else if (strcmp(c.color, "green") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, SDL_ALPHA_OPAQUE); // Vert
    } else if (strcmp(c.color, "blue") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE); // Bleu
    } else {
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE); // Blanc par défaut
    }

    while (x >= y) {
        // Dessiner des lignes horizontales pour remplir le cercle
        SDL_RenderDrawLine(renderer, x0 - x, y0 + y, x0 + x, y0 + y);
        SDL_RenderDrawLine(renderer, x0 - y, y0 + x, x0 + y, y0 + x);
        SDL_RenderDrawLine(renderer, x0 - x, y0 - y, x0 + x, y0 - y);
        SDL_RenderDrawLine(renderer, x0 - y, y0 - x, x0 + y, y0 - x);

        y += 1;
        if (err <= 0) {
            err += 2 * y + 1;
        } else {
            x -= 1;
            err += 2 * (y - x) + 1;
        }
    }

    // Afficher les changements à l'écran
    SDL_RenderPresent(renderer);
}

void cursor(const char* color, int x, int y, int size) {
    // Effacer l'ancien curseur en dessinant avec la couleur de fond
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE); // Couleur de fond noir
    SDL_Rect clear_rect;
    clear_rect.x = current_x - size / 2; // Centrer sur l'ancienne position
    clear_rect.y = current_y - size / 2;
    clear_rect.w = size;
    clear_rect.h = size;
    SDL_RenderFillRect(renderer, &clear_rect);

    // Définir la couleur pour le nouveau curseur
    if (strcmp(color, "red") == 0) {
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, SDL_ALPHA_OPAQUE); // Rouge
    } else if (strcmp(color, "green") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, SDL_ALPHA_OPAQUE); // Vert
    } else if (strcmp(color, "blue") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE); // Bleu
    } else {
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE); // Blanc par défaut
    }

    // Dessiner le nouveau curseur
    SDL_Rect rect;
    rect.x = x - size / 2; // Centrer sur la position (x, y)
    rect.y = y - size / 2;
    rect.w = size;
    rect.h = size;
    SDL_RenderFillRect(renderer, &rect);

    // Mettre à jour la position actuelle du curseur
    current_x = x;
    current_y = y;

    // Rafraîchir l'écran
    SDL_RenderPresent(renderer);
}

void move_by(Cursor c, int angle, int distance) {
    // Convertir l'angle en radians
    double rad = angle * (M_PI / 180.0); // Angle en degrés -> radians

    // Calculer les nouvelles coordonnées du curseur
    current_x += (int)(distance * cos(rad));
    current_y += (int)(distance * sin(rad));
    
    // Mettre à jour la position du curseur
    c.x = current_x;
    c.y = current_y;
    cursor(c.color, current_x, current_y, 10);
}

void line_by(Cursor c, int angle, int distance) {
    // Utiliser la couleur du curseur pour la ligne
    if (strcmp(c.color, "red") == 0) {
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, SDL_ALPHA_OPAQUE); // Rouge
    } else if (strcmp(c.color, "green") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, SDL_ALPHA_OPAQUE); // Vert
    } else if (strcmp(c.color, "blue") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE); // Bleu
    } else {
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE); // Blanc par défaut
    }
    // Convertir l'angle en radians
    double rad = angle * (M_PI / 180.0); // Angle en degrés -> radians

    // Calculer la nouvelle position à atteindre
    int new_x = current_x + (int)(distance * cos(rad));
    int new_y = current_y + (int)(distance * sin(rad));

    // Tracer la ligne
    SDL_RenderDrawLine(renderer, current_x, current_y, new_x, new_y);
    SDL_RenderPresent(renderer);

    // Mettre à jour la position du curseur
    current_x = new_x;
    current_y = new_y;
}
