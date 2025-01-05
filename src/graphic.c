#include <SDL.h>
#include "graphic.h"
#include <stdio.h>
#include <math.h>
#include <string.h>
#define MAX_OBJECTS 100

// Variables globales pour gérer SDL
static SDL_Window *window = NULL;
static SDL_Renderer *renderer = NULL;
static int current_x = 0, current_y = 0; // Position actuelle du curseur


Object objects[MAX_OBJECTS];
int object_count = 0;
Object* dragged_object = NULL;  // L'objet en cours de déplacement
int offset_x, offset_y;         // Décalage par rapport à la position de la souris au moment du clic

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
// Vérifier si un objet est dans le rectangle de sélection
int is_object_in_selection(const SDL_Rect* selection, const Object* obj) {
    SDL_Rect intersection;
    return SDL_IntersectRect(selection, &obj->bounding_box, &intersection);
}

void highlight_selected_objects() {
    for (int i = 0; i < object_count; i++) {
        // Dessiner l'objet avec sa couleur d'origine
        if (objects[i].type == CURSOR) {
            SDL_SetRenderDrawColor(renderer, 
                                   strcmp(objects[i].color, "red") == 0 ? 255 : 0,
                                   strcmp(objects[i].color, "green") == 0 ? 255 : 0,
                                   strcmp(objects[i].color, "blue") == 0 ? 255 : 0,
                                   SDL_ALPHA_OPAQUE);
            SDL_RenderFillRect(renderer, &objects[i].bounding_box);
        } else if (objects[i].type == LINE) {
            SDL_SetRenderDrawColor(renderer, 
                                   strcmp(objects[i].color, "red") == 0 ? 255 : 0,
                                   strcmp(objects[i].color, "green") == 0 ? 255 : 0,
                                   strcmp(objects[i].color, "blue") == 0 ? 255 : 0,
                                   SDL_ALPHA_OPAQUE);
            // Dessiner la ligne entre (x1, y1) et (x2, y2)
            SDL_RenderDrawLine(renderer, 
                               objects[i].x1, objects[i].y1, 
                               objects[i].x2, objects[i].y2);
        } else if (objects[i].type == CIRCLE) {
            circle(objects[i]); // Passer l'objet directement à la fonction `circle`
        }

        // Si l'objet est sélectionné, dessiner le contour bleu
        if (objects[i].is_selected) {
            SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE); // Bleu

            if (objects[i].type == LINE) {
                // Appliquer un contour autour de la ligne en augmentant son épaisseur temporairement
                SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE);  // Choisir la couleur pour la sélection

                // Vous pouvez dessiner la ligne avec une certaine largeur ici
                SDL_RenderDrawLine(renderer, 
                                   objects[i].x1 - 2, objects[i].y1 - 2,  // Décalage pour "halo"
                                   objects[i].x2 - 2, objects[i].y2 - 2); // Décalage pour "halo"

                SDL_RenderDrawLine(renderer, 
                                   objects[i].x1 + 2, objects[i].y1 + 2,  // Décalage pour "halo"
                                   objects[i].x2 + 2, objects[i].y2 + 2); // Décalage pour "halo"

                // Dessiner la ligne d'origine
                SDL_SetRenderDrawColor(renderer, 
                                       strcmp(objects[i].color, "red") == 0 ? 255 : 0,
                                       strcmp(objects[i].color, "green") == 0 ? 255 : 0,
                                       strcmp(objects[i].color, "blue") == 0 ? 255 : 0,
                                       SDL_ALPHA_OPAQUE);
                SDL_RenderDrawLine(renderer, 
                                   objects[i].x1, objects[i].y1, 
                                   objects[i].x2, objects[i].y2);
            } else {
                SDL_RenderDrawRect(renderer, &objects[i].bounding_box); // Pour les autres objets
            }
        }
    }
    SDL_RenderPresent(renderer);
}
// Désélectionner tous les objets
void deselect_all_objects() {
    for (int i = 0; i < object_count; i++) {
        objects[i].is_selected = 0;
    }
}
void handle_mouse_selection(SDL_Event* event) {
    static int start_x = 0, start_y = 0;
    static int selecting = 0;
    SDL_Rect selection_rect;

    switch (event->type) {
        case SDL_MOUSEBUTTONDOWN:
            if (event->button.button == SDL_BUTTON_LEFT) {
                int clicked_on_object = 0;
                for (int i = 0; i < object_count; i++) {
                    if (objects[i].is_selected && 
                        event->button.x >= objects[i].bounding_box.x &&
                        event->button.x <= objects[i].bounding_box.x + objects[i].bounding_box.w &&
                        event->button.y >= objects[i].bounding_box.y &&
                        event->button.y <= objects[i].bounding_box.y + objects[i].bounding_box.h) {
                        dragged_object = &objects[i];
                        clicked_on_object = 1;
                        // Ajouter ici les printf pour vérifier l'offset avant le déplacement
                        printf("Sélection de l'objet : x1=%d, y1=%d, offset_x=%d, offset_y=%d\n", 
                       dragged_object->x1, dragged_object->y1, offset_x, offset_y);

                        // Mettre à jour les offsets en fonction du centre du cercle
                        if (dragged_object->type == CIRCLE) {
                            offset_x = event->button.x - dragged_object->x1;
                            offset_y = event->button.y - dragged_object->y1;
                            printf("Après le calcul de l'offset pour le cercle : offset_x=%d, offset_y=%d\n", offset_x, offset_y);
                        } else {
                            offset_x = event->button.x - dragged_object->bounding_box.x;
                            offset_y = event->button.y - dragged_object->bounding_box.y;
                        }
                        break;
                    }
                }

                if (!clicked_on_object) {
                    start_x = event->button.x;
                    start_y = event->button.y;
                    selecting = 1;
                    deselect_all_objects();
                }
            } else if (event->button.button == SDL_BUTTON_RIGHT) {
                deselect_all_objects();
                SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
                SDL_RenderClear(renderer);
                highlight_selected_objects();
            }
            break;

        case SDL_MOUSEMOTION:
            if (selecting) {
                selection_rect.x = (start_x < event->motion.x) ? start_x : event->motion.x;
                selection_rect.y = (start_y < event->motion.y) ? start_y : event->motion.y;
                selection_rect.w = abs(event->motion.x - start_x);
                selection_rect.h = abs(event->motion.y - start_y);

                SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
                SDL_RenderClear(renderer);
                highlight_selected_objects();
                SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE);
                SDL_RenderDrawRect(renderer, &selection_rect);
                SDL_RenderPresent(renderer);
            } else if (dragged_object) {
                if (dragged_object->type == LINE) {
                    int dx = event->motion.x - offset_x - dragged_object->bounding_box.x;
                    int dy = event->motion.y - offset_y - dragged_object->bounding_box.y;
                    dragged_object->x1 += dx;
                    dragged_object->y1 += dy;
                    dragged_object->x2 += dx;
                    dragged_object->y2 += dy;
                    dragged_object->bounding_box.x += dx;
                    dragged_object->bounding_box.y += dy;
                } else if (dragged_object->type == CIRCLE) {
                     printf("Avant déplacement du cercle : x1=%d, y1=%d, offset_x=%d, offset_y=%d\n", 
                   dragged_object->x1, dragged_object->y1, offset_x, offset_y);
                    dragged_object->x1 = event->motion.x - offset_x;
                    dragged_object->y1 = event->motion.y - offset_y;
                    dragged_object->bounding_box.x = dragged_object->x1 - dragged_object->radius;
                    dragged_object->bounding_box.y = dragged_object->y1 - dragged_object->radius;
                    printf("Après déplacement du cercle : x1=%d, y1=%d, bounding_box.x=%d, bounding_box.y=%d\n", 
                   dragged_object->x1, dragged_object->y1, dragged_object->bounding_box.x, dragged_object->bounding_box.y);
                } else {
                    dragged_object->bounding_box.x = event->motion.x - offset_x;
                    dragged_object->bounding_box.y = event->motion.y - offset_y;
                }

                SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
                SDL_RenderClear(renderer);
                highlight_selected_objects();
                SDL_RenderPresent(renderer);
            }
            break;

        case SDL_MOUSEBUTTONUP:
            if (event->button.button == SDL_BUTTON_LEFT) {
                if (selecting) {
                    selection_rect.x = (start_x < event->button.x) ? start_x : event->button.x;
                    selection_rect.y = (start_y < event->button.y) ? start_y : event->button.y;
                    selection_rect.w = abs(event->motion.x - start_x);
                    selection_rect.h = abs(event->motion.y - start_y);

                    for (int i = 0; i < object_count; i++) {
                        if (is_object_in_selection(&selection_rect, &objects[i])) {
                            objects[i].is_selected = 1;
                        }
                    }

                    selecting = 0;

                    SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
                    SDL_RenderClear(renderer);
                    highlight_selected_objects();
                }

                dragged_object = NULL;
            }
            break;
    }
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

void circle(Object obj) {
    int x0 = obj.x1, y0 = obj.y1; // Coordonnées du centre
    int radius = obj.radius;     // Rayon du cercle
    int x = radius, y = 0;
    int err = 0;

    // Définir la couleur de l'objet
    if (strcmp(obj.color, "red") == 0) {
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, SDL_ALPHA_OPAQUE);
    } else if (strcmp(obj.color, "green") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, SDL_ALPHA_OPAQUE);
    } else if (strcmp(obj.color, "blue") == 0) {
        SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE);
    } else {
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE);
    }

    while (x >= y) {
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
void add_cursor(const char* color, int x, int y) {
    if (object_count < MAX_OBJECTS) {
        objects[object_count].type = CURSOR;
        objects[object_count].bounding_box = (SDL_Rect){x - 5, y - 5, 10, 10}; // Définir la taille du curseur
        objects[object_count].is_selected = 0;
        objects[object_count].radius = 0; // Pas de rayon pour le curseur
        objects[object_count].x2 = 0; // Non utilisé
        objects[object_count].y2 = 0; // Non utilisé
        strcpy(objects[object_count].color, color);
        printf("Added cursor: color=%s, x=%d, y=%d\n", color, x, y); // Débogage
        object_count++;
    }
}
void add_line(int x1, int y1, int x2, int y2, const char* color) {
    if (object_count < MAX_OBJECTS) {
        // Réordonner les coordonnées pour toujours commencer en haut à gauche
        int start_x = (x1 < x2) ? x1 : x2; // Plus petit des deux
        int start_y = (y1 < y2) ? y1 : y2; // Plus petit des deux
        int end_x = (x1 > x2) ? x1 : x2;   // Plus grand des deux
        int end_y = (y1 > y2) ? y1 : y2;   // Plus grand des deux

        // Définir les coordonnées x1, y1 pour la ligne
        objects[object_count].x1 = x1;  // Ajouter x1
        objects[object_count].y1 = y1;  // Ajouter y1

        // Définir la boîte englobante correctement
        objects[object_count].bounding_box = (SDL_Rect){
            start_x, start_y, abs(x2 - x1), abs(y2 - y1)
        };

        // Définir les autres attributs
        objects[object_count].type = LINE;
        objects[object_count].is_selected = 0;
        objects[object_count].radius = 0; // Pas de rayon pour une ligne
        objects[object_count].x2 = x2;    // Conserver les coordonnées originales
        objects[object_count].y2 = y2;
        strcpy(objects[object_count].color, color);

        // Incrémenter le compteur d'objets
        object_count++;
    }
}

void add_circle(int x, int y, int radius, const char* color) {
    if (object_count < MAX_OBJECTS) {
        objects[object_count].type = CIRCLE;
        objects[object_count].bounding_box = (SDL_Rect){x - radius, y - radius, 2 * radius, 2 * radius}; // Définir la boîte englobante
        objects[object_count].is_selected = 0;
        objects[object_count].radius = radius;
        objects[object_count].x2 = 0; // Non utilisé
        objects[object_count].y2 = 0; // Non utilisé
        strcpy(objects[object_count].color, color);
        printf("Added circle: x=%d, y=%d, radius=%d, color=%s\n", x, y, radius, color); // Débogage
        object_count++;
    }
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
