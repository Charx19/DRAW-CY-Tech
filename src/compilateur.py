from parser import parse_code
def compile_draw_code_to_c(code, grammar):
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
        "    int current_x, current_y;",
        "    char current_color[20] = \"\";",

    ]
    declared_variables = {}

    # Fonction pour gérer l'indentation
    def indent(level):
        return '    ' * level

    # Fonction that determines which type is the value
    def deduce_type(value):
        try:
            int(value)  # Test if int
            return "int"
        except ValueError:
            try:
                float(value)  # Test if float
                return "float"
            except ValueError:
                return None  # if neither, return None

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
                # Supposons que vous ayez des variables current_x et current_y qui représentent
                # les coordonnées actuelles du point de départ de la ligne.
                c_code.append(f"{indent(indent_level)}line_to({var_name}, {x}, {y});")
                c_code.append(f"{indent(indent_level)}add_line(current_x, current_y, {x}, {y}, \"{color}\");")
                c_code.append(f"{indent(indent_level)}current_x = {x};")
                c_code.append(f"{indent(indent_level)}current_y = {y};")
            elif command == "line_by":
                var_name = instruction[1]
                x, y = instruction[2], instruction[3]
                c_code.append(f"{indent(indent_level)}line_by({var_name},{x}, {y});")
                c_code.append(f"{indent(indent_level)}add_line({x}, {y}, {radius}, \"{color}\");")
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
                x = instruction[2]
                y = instruction[3]
                radius = instruction[4]
                color = instruction[5]

                # Créez un objet avec les propriétés du cercle
                c_code.append(f"{indent(indent_level)}Object circle_{var_name};")
                c_code.append(f"{indent(indent_level)}circle_{var_name}.type = CIRCLE;")
                c_code.append(f"{indent(indent_level)}circle_{var_name}.x1 = current_x;")
                c_code.append(f"{indent(indent_level)}circle_{var_name}.y1 = current_y;")
                c_code.append(f"{indent(indent_level)}circle_{var_name}.radius = {radius};")
                c_code.append(f"{indent(indent_level)}strcpy(circle_{var_name}.color, current_color);")
                c_code.append(f"{indent(indent_level)}add_circle(current_x, current_y, {radius}, current_color);")

                # Appelez la fonction circle avec l'objet
                c_code.append(f"{indent(indent_level)}circle(circle_{var_name});")

                # Ajoutez le cercle à la liste des objets
                

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
                c_code.append(f"{indent(indent_level)}add_cursor(\"{color}\", {x}, {y});")  # Ajout au tableau d'objets
                c_code.append(f"{indent(indent_level)}current_x = {x};")
                c_code.append(f"{indent(indent_level)}current_y = {y};")
                c_code.append(f"{indent(indent_level)}strcpy(current_color, \"{color}\");")
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
    c_code.append(f"{indent(3)}handle_mouse_selection(&event);")
    c_code.append(f"{indent(2)}}}")
    c_code.append(f"{indent(1)}}}")
    c_code.append(f"{indent(1)}close_graphics();")
    c_code.append(f"{indent(1)}return 0;")
    c_code.append("}")

    # Retourner le code C généré sous forme de chaîne
    return "\n".join(c_code)
