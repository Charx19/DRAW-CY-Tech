import os
import subprocess
from lexer import lexer
from parser import parse_code


def generate_c_code(instructions):
    """Génère le code C à partir des instructions analysées"""
    # Votre implémentation précédente pour générer le code C
    c_code = [
        '#include <stdio.h>',
        '#include <SDL2/SDL.h>',
        '',
        'int main(int argc, char* argv[]) {',
        '    SDL_Init(SDL_INIT_VIDEO);',
        '    SDL_Window* window = SDL_CreateWindow("Draw++", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, 0);',
        '    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);',
        '    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);',
        '    SDL_RenderClear(renderer);',
        '    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);',
        '',
        '    // Variables pour suivre la position actuelle',
        '    int current_x = 0;',
        '    int current_y = 0;',
        ''
    ]
    for instruction in instructions:
        command = instruction[0]

        if command == "move_to":
            x,y=instruction[1], instruction[2]
            c_code.append(f' current_x= {x};')
            c_code.append(f' current_y= {y};')
        elif command == "line_to":
            x,y = instruction[1], instruction[2]
            c_code.append(f'    SDL_RenderDrawLine(renderer, current_x, current_y, {x}, {y});')
            c_code.append(f'    current_x = {x};')
            c_code.append(f'    current_y = {y};')
        elif command == "set_color":
            color = instruction[1]
            # Assume color is in RGB format like "255,0,0"
            r, g, b = map(int, color.split(","))
            c_code.append(f'    SDL_SetRenderDrawColor(renderer, {r}, {g}, {b}, 255);')
        #Need to test if SDL is able to draw cirlce or need to do it manually
        elif command == "circle":
            radius = instruction[1]
            c_code.append(f'    // Code pour dessiner un cercle ici avec un rayon de {radius}.')
        
    c_code.append('    SDL_RenderPresent(renderer);')
    c_code.append('    SDL_Delay(5000);')  # Attendre 5 secondes pour voir le dessin
    c_code.append('    SDL_DestroyRenderer(renderer);')
    c_code.append('    SDL_DestroyWindow(window);')
    c_code.append('    SDL_Quit();')
    c_code.append('    return 0;')
    c_code.append('}')
    return '\n'.join(c_code)

def compile_draw_code(code):
    """Compile le code Draw++ en code C et l'exécute"""
    try:
        # 1. Analyse lexicale et syntaxique
        lexer.input(code)
        instructions = parse_code(code)
        
        # 2. Génération du code C
        c_code = generate_c_code(instructions)
        
        # 3. Écriture dans un fichier
        output_file = "output.c"
        with open(output_file, "w") as f:
            f.write(c_code)
        
        # 4. Compilation et exécution du code C
        exe_file = output_file.replace(".c", ".exe")
        subprocess.run(["gcc", "-o", exe_file, output_file, "-lSDL2"], check=True)
        subprocess.run(["./" + exe_file], check=True)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Erreur de compilation : {str(e)}")