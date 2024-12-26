from parser import parse_code
def compile_draw_code(code, grammar):
    """Analyse et compile le code Draw++ en code C, et retourne le code généré."""
    
    instructions, errors = parse_code(code, grammar)  # Analyse et récupère les instructions

    if errors:
        raise ValueError("Des erreurs de syntaxe ont été trouvées. Compilation annulée.")
    
    # Liste pour stocker le code C généré
    c_code = [
        "#include <stdio.h>",
        "#include <string.h>",
        "#include \"graphic.h\"",
        "",
        "",
        "// Fonction pour créer un curseur",
        "Cursor create_cursor(const char* color, int x, int y) {",
        "    Cursor c;",
        "    strcpy(c.color, color);",
        "    c.x = x;",
        "    c.y = y;",
        "    return c;",
        "}",
        "",
        "int WinMain(int argc, char **argv) {",
        "    init_graphics();  // Initialisation du système graphique",
    ]
    declared_variables = {}

    # Fonction pour gérer l'indentation
    def indent(level):
        return '    ' * level

    # Fonction pour déduire le type d'une valeur
    def deduce_type(value):
        try:
            int(value)  # Test si c'est un entier
            return "int"
        except ValueError:
            try:
                float(value)  # Test si c'est un flottant
                return "float"
            except ValueError:
                return None  # Si ce n'est ni un entier ni un flottant

    # Fonction pour générer le code C à partir des instructions
    def generate_c_code(instructions, indent_level=1):  # Le corps du main commence au niveau 1
        nonlocal c_code, declared_variables

        for instruction in instructions:
            command = instruction[0]
            
            if command == "move_to":
                var_name = instruction[1]
                x, y = instruction[2], instruction[3]
                c_code.append(f"{indent(indent_level)}move_to({var_name},{x}, {y});")
            elif command == "line_to":
                var_name = instruction[1]
                x, y = instruction[2], instruction[3]
                c_code.append(f"{indent(indent_level)}line_to({var_name},{x}, {y});")
            elif command == "line_by":
                var_name = instruction[1]
                x, y = instruction[2], instruction[3]
                c_code.append(f"{indent(indent_level)}line_by({var_name},{x}, {y});")
            elif command == "move_by":
                var_name = instruction[1]
                x, y = instruction[2], instruction[3]
                c_code.append(f"{indent(indent_level)}move_by({var_name},{x}, {y});")
            elif command == "set_color":
                var_name = instruction[1]
                color = instruction[2]
                c_code.append(f"{indent(indent_level)}set_color({var_name},\"{color}\");")
            elif command == "circle":
                var_name = instruction[1]
                radius = instruction[2]
                c_code.append(f"{indent(indent_level)}circle({var_name},{radius});")
            elif command == "cursor":  # Gestion de la commande cursor
                var_name = instruction[1]
                color = instruction[2]
                x = instruction[3]
                y = instruction[4]
                # Vérifier si la variable a déjà été déclarée
                if var_name in declared_variables:
                    raise ValueError(f"Variable '{var_name}' déjà déclarée.")

                declared_variables[var_name] = "Cursor"
                c_code.append(f"{indent(indent_level)}Cursor {var_name} = create_cursor(\"{color}\", {x}, {y});")
                c_code.append(f"{indent(indent_level)}cursor(\"{color}\",{x},{y},10);") 
            elif command == "declare":  # Gestion de l'affectation de variable
                var_name = instruction[1]
                value = instruction[2]
                var_type = deduce_type(value)

                if var_type is None:
                    raise ValueError(f"Type non reconnu pour la valeur : '{value}'")
                
                if var_name in declared_variables:
                    raise ValueError(f"Variable '{var_name}' déjà déclarée.")
                
                declared_variables[var_name] = var_type
                c_code.append(f"{indent(indent_level)}{var_type} {var_name} = {value};")
            elif command == "modify":
                var_name = instruction[1]
                value = instruction[2]

                if var_name not in declared_variables:
                    raise ValueError(f"Variable '{var_name}' non déclarée avant modification.")
                
                c_code.append(f"{indent(indent_level)}{var_name} = {value};")
            else:
                raise ValueError(f"Instruction inconnue : '{command}'")
    
    # Générer le code C pour les instructions
    generate_c_code(instructions)

    # Terminer le code C avec la boucle d'événements SDL
    c_code.append(f"{indent(1)}SDL_Event event;")
    c_code.append(f"{indent(1)}int running = 1;")
    c_code.append(f"{indent(1)}while (running) {{")
    c_code.append(f"{indent(2)}while (SDL_PollEvent(&event)) {{")
    c_code.append(f"{indent(3)}if (event.type == SDL_QUIT) {{")
    c_code.append(f"{indent(4)}running = 0;")
    c_code.append(f"{indent(3)}}}")
    c_code.append(f"{indent(2)}}}")
    c_code.append(f"{indent(1)}}}")
    c_code.append(f"{indent(1)}close_graphics();")
    c_code.append(f"{indent(1)}return 0;")
    c_code.append("}")

    # Retourner le code C généré sous forme de chaîne
    return "\n".join(c_code)
