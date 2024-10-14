from lexer import lexer
from parser import parse_code

def compile_draw_code(code):
    """Analyse et compile le code Draw++ en code C."""
    
    # Utiliser le lexer et parser
    instructions = parse_code(code)  # Récupérer les instructions

    # Écrire le code C dans un fichier
    c_code = []
    for instruction in instructions:
        command = instruction[0]
        if command == "move_to":
            x = instruction[1]
            y = instruction[2]
            c_code.append(f"move_to({x}, {y});")
        elif command == "line_to":
            x = instruction[1]
            y = instruction[2]
            c_code.append(f"line_to({x}, {y});")
        elif command == "set_color":
            color = instruction[1]
            c_code.append(f"set_color(\"{color}\");")
        elif command == "circle":
            radius = instruction[1]
            c_code.append(f"circle({radius});")
        else:
            raise ValueError(f"Instruction inconnue : '{command}'")

    # Écrire le code C dans un fichier
    with open("output.c", "w") as f:
        f.write("\n".join(c_code))
