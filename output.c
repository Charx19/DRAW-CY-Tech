#include <stdio.h>
#include <SDL2/SDL.h>

int main(int argc, char* argv[]) {
    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window* window = SDL_CreateWindow("Draw++", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, 0);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    SDL_RenderClear(renderer);
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);

    // Variables pour suivre la position actuelle
    int current_x = 0;
    int current_y = 0;

    SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
 current_x= 100;
 current_y= 100;
    SDL_RenderDrawLine(renderer, current_x, current_y, 200, 200);
    current_x = 200;
    current_y = 200;
    // Code pour dessiner un cercle ici avec un rayon de 50.
 current_x= 300;
 current_y= 300;
    SDL_SetRenderDrawColor(renderer, 0, 0, 255, 255);
    SDL_RenderDrawLine(renderer, current_x, current_y, 400, 400);
    current_x = 400;
    current_y = 400;
    SDL_RenderPresent(renderer);
    SDL_Delay(5000);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}