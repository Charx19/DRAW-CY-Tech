#ifndef GRAPHIC
#define GRAPHIC

#include <SDL.h>
typedef struct {
    char color[20];
    int x;
    int y;
} Cursor;


// Initialisation et fermeture
void init_graphics();
void close_graphics();

// Fonctions graphiques
void move_to(Cursor a, int x, int y);
void line_to(Cursor a, int x, int y);
void circle(Cursor a, int radius);
void cursor(const char* color, int x, int y, int size);
void move_by(Cursor a, int x, int y);
void line_by(Cursor a, int x, int y);

#endif
