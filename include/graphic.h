#ifndef GRAPHIC
#define GRAPHIC

#include <SDL.h>
#include <stdbool.h>

typedef struct {
    SDL_Rect bounding_box; // Coordonnées et taille de l'objet
    char color[10];        // Couleur du dessin
} Drawing;

typedef struct {
    char color[20];
    int x;
    int y;
} Cursor;

typedef struct {
    enum {CURSOR, LINE, CIRCLE} type; // Type d'objet
    SDL_Rect bounding_box;            // Zone de l'objet
    int is_selected;                  // Indicateur de sélection
    int radius;                       // Rayon (pour les cercles)
    int x2, y2;    // position actuelle
    int x1, y1;           // position désirée        
    char color[20];                   // Couleur de l'objet
    int target_x;
    bool is_animating;
    int animation_step;
} Object;

// Initialisation et fermeture
void init_graphics();
void close_graphics();
//gestion de la souris
void handle_mouse_selection(SDL_Event* event);
void deselect_all_objects();
int is_object_in_selection(const SDL_Rect* selection, const Object* obj);
void highlight_selected_objects();
// Fonctions graphiques
void move_to(Cursor* a, int x, int y);
void line_to(Cursor a, int x, int y);
void circle(Object obj);
void cursor(const char* color, int x, int y, int size);
void add_cursor(const char* color, int x, int y);
void add_line(int x1, int y1, int x2, int y2, const char* color);
void add_circle(int x, int y, int radius, const char* color);
void update_moving_objects();
void handle_key_event(SDL_Event* event);
void remove_selected_object();
#endif
