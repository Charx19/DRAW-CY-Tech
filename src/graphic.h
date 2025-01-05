#ifndef GRAPHIC
#define GRAPHIC

#include <SDL.h>

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
    int x2, y2;    
    int x1, y1;                   
    char color[20];                   // Couleur de l'objet
} Object;

// Initialisation et fermeture
void init_graphics();
void close_graphics();
//gestion de la souris
void handle_mouse_selection(SDL_Event* event);
void handle_object_drag(SDL_Event* event);
void handle_mouse_button_down(SDL_Event* event);
void handle_mouse_button_up(SDL_Event* event);
void deselect_all_objects();
int is_object_in_selection(const SDL_Rect* selection, const Object* obj);
void highlight_selected_objects();
// Fonctions graphiques
void move_to(Cursor a, int x, int y);
void line_to(Cursor a, int x, int y);
void circle(Object obj);
void cursor(const char* color, int x, int y, int size);
void move_by(Cursor a, int x, int y);
void line_by(Cursor a, int x, int y);
void add_cursor(const char* color, int x, int y);
void add_line(int x1, int y1, int x2, int y2, const char* color);
void add_circle(int x, int y, int radius, const char* color);

#endif
