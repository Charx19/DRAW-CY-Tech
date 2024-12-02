from lexer import lexer
from parser import parse_code

def compile_draw_code(code, grammar):
    """Analyse et compile le code Draw++ en code C."""
    
    # Utiliser le lexer et parser
    instructions, errors = parse_code(code, grammar)  # Récupérer les instructions

    if errors:
        raise ValueError("Des erreurs de syntaxe ont été trouvées. Compilation annulée.")

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
        elif command == "line_by":
            x = instruction[1]
            y = instruction[2]
            c_code.append(f"line_by({x}, {y});")
        elif command == "move_by":
            x = instruction[1]
            y = instruction[2]
            c_code.append(f"move_by({x}, {y});")
        elif command == "set_color":
            color = instruction[1]
            c_code.append(f"set_color(\"{color}\");")
        elif command == "circle":
            radius = instruction[1]
            c_code.append(f"circle({radius});")
        elif command == "cursor":
            color = instruction[1]  # Couleur (par exemple, "blue")
            x = instruction[2]  # Position x
            y = instruction[3]  # Position y
            c_code.append(f"cursor(\"{color}\", {x}, {y});")
        else:
            raise ValueError(f"Instruction inconnue : '{command}'")

    # Écrire le code C dans un fichier
    with open("output.c", "w") as f:
        f.write("\n".join(c_code))
