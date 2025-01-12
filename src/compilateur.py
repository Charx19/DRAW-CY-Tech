def ast_to_c(ast, declared_vars=None, indent_level=0):
    """
    Traduire un AST en code C.

    Paramètre:
    - ast : Un arbre de syntaxe abstraite (AST) représentant le programme.
    - declared_vars : Un ensemble contenant les noms des variables déjà déclarées.
    - indent_level : Le niveau d'indentation pour le code généré.

    Retourne:
    - str : Le code C généré.
    """
    if declared_vars is None:
        declared_vars = set()  # Ensemble pour garder trace des variables déjà déclarées

    if not ast:
        print("Ce n'est pas un AST valide")
        return ""

    # Vérification que l'AST est bien un tuple avec 2 éléments
    if not isinstance(ast, tuple) or len(ast) != 2:
        raise ValueError(f"AST mal formé, doit être un tuple de type (node_type, children), mais reçu : {ast}")

    # Décomposition de l'AST
    node_type, children = ast

    # Fonction pour ajouter des indentations
    def indent(code, level):
        return "    " * level + code

    print(f"Type de nœud : {node_type}, Enfants : {children}")

    # Traitement en fonction du type de nœud
    if node_type == 'program':
        # Pour le programme, nous générons le code de début avec l'inclusion de bibliothèques
        code = "#include <stdio.h>\n#include <string.h>\n#include \"graphic.h\"\n\n"  # Ajout des bibliothèques
        
        # Fonction pour créer un curseur
        code += "Cursor create_cursor(const char* color, int x, int y) {\n"
        code += "    Cursor c;\n"
        code += "    strcpy(c.color, color);\n"
        code += "    c.x = x;\n"
        code += "    c.y = y;\n"
        code += "    return c;\n"
        code += "}\n\n"

        # Générer la fonction WinMain
        code += "int WinMain(int argc, char **argv) {\n"
        code += "    init_graphics();  // Initialisation du système graphique\n"
        code += "    int current_y, current_x;\n"
        code += "    char current_color[20];  \n"
        # Générer les instructions du programme
        for child in children:
            # Appel récursif pour chaque enfant, avec un niveau d'indentation approprié
            code += ast_to_c(child, declared_vars, indent_level + 1)
        
         # Ajout de la boucle principale SDL
        code += indent("SDL_Event event;\n", indent_level + 1)
        code += indent("int running = 1;\n", indent_level + 1)
        code += indent("// Boucle principale\n", indent_level + 1)
        code += indent("while (running) {\n", indent_level + 1)
        code += indent("    // Gestion des événements\n", indent_level + 2)
        code += indent("    while (SDL_PollEvent(&event)) {\n", indent_level + 2)
        code += indent("        if (event.type == SDL_QUIT) {\n", indent_level + 3)
        code += indent("            running = 0;\n", indent_level + 4)
        code += indent("        }\n", indent_level + 3)
        code += indent("       handle_mouse_selection(&event);\n", indent_level + 3)
        code += indent("       handle_key_event(&event);\n", indent_level + 3)
        code += indent("    }\n", indent_level + 2)
        code += indent("\n", indent_level + 2)
        code += indent("       update_moving_objects();\n", indent_level + 2)
        code += indent("       highlight_selected_objects(&event); // Mettre à jour l'affichage\n", indent_level + 2)
        code += indent("    // Montre les objets sélectionnés si nécessaire\n", indent_level + 2)
        code += indent("}\n", indent_level + 1)

        # Fermeture du système graphique et fin de la fonction WinMain
        code += indent("close_graphics();  // Fermer le système graphique\n", indent_level + 1)
        code += indent("return 0;\n", indent_level + 1)
        code += "}\n"
        return code

    elif node_type == 'assign_stmt':
        # Pour les assignations, les enfants doivent être une liste contenant exactement 2 éléments
        if not isinstance(children, list) or len(children) != 2:
            raise ValueError(f"Nœud d'assignation mal formé : {children}")
        identifier = children[0]
        value = children[1]

        # Si la variable n'est pas encore déclarée, on la déclare en tant qu'int
        if identifier not in declared_vars:
            declared_vars.add(identifier)
            code = indent(f"int {identifier} = {value};\n", indent_level)
        else:
            code = indent(f"{identifier} = {value};\n", indent_level)

        return code

    elif node_type == 'cursor_stmt':
        # Pour le curseur, nous attendons un identifiant, une couleur, deux coordonnées et une taille
        if len(children) != 4:
            raise ValueError(f"Nœud de curseur mal formé : {children}")
        identifier = children[0]
        color = children[1]
        x = children[2]
        y = children[3]
        # Déclaration de la variable et initialisation avec les arguments passés
        code = indent(f"Cursor {identifier} = create_cursor({color}, {x}, {y});\n", indent_level)
        code += indent(f"add_cursor({identifier}.color, {identifier}.x, {identifier}.y);\n", indent_level)
        code += indent(f"cursor({color}, {x}, {y}, 10);\n", indent_level)
        code += indent(f"current_x = {x};\n", indent_level)
        code += indent(f"current_y = {y};\n", indent_level)
        code += indent(f"strcpy(current_color, {color});\n", indent_level)
        return code
    
    elif node_type == 'move_stmt':
        # Pour le mouvement, nous attendons un identifiant et deux coordonnées
        if len(children) != 3:
            raise ValueError(f"Nœud de mouvement mal formé : {children}")
        identifier = children[0]
        x = children[1]
        y = children[2]
        # Code pour déplacer le curseur à la nouvelle position
        code = indent(f"move_to(&{identifier}, {x}, {y});\n", indent_level)
        code += indent(f"current_x = {x};\n", indent_level)
        code += indent(f"current_y = {y};\n", indent_level)
        
        return code
    
    elif node_type == 'line_to':
        # Pour le mouvement, nous attendons un identifiant et deux coordonnées
        if len(children) != 3:
            raise ValueError(f"Nœud de mouvement mal formé : {children}")
        identifier = children[0]
        x = children[1]
        y = children[2]
        # Code pour déplacer le curseur à la nouvelle position
        code = indent(f"line_to({identifier}, {x}, {y});\n", indent_level)
        code+= indent(f"add_line(current_x, current_y, {x}, {y}, current_color);\n", indent_level)
        return code
    
    elif node_type == 'circle':
        # Pour le mouvement, nous attendons un identifiant et deux coordonnées
        if len(children) != 2:
            raise ValueError(f"Nœud de mouvement mal formé : {children}")
        identifier = children[0]
        x = children[1]
        # Code pour déplacer le curseur à la nouvelle position
        code = indent(f"Object circle_{identifier};\n", indent_level)
        code+= indent(f"circle_{identifier}.type = CIRCLE;\n", indent_level)
        code+= indent(f"circle_{identifier}.radius = {x};\n", indent_level)
        code+= indent(f"strcpy(circle_{identifier}.color, current_color);\n", indent_level)
        code+= indent(f"circle_{identifier}.x1 = current_x;\n", indent_level)
        code+= indent(f"circle_{identifier}.y1 = current_y;\n", indent_level)
        code+= indent(f"add_circle(current_x, current_y, {x}, current_color);\n", indent_level)
        code+= indent(f"circle(circle_{identifier});\n", indent_level)
        return code
    
    elif node_type == 'expression':
        # Gérer les expressions comme a == 8, x > 10, etc.
        if len(children) != 3:
            raise ValueError(f"Nœud 'expression' mal formé : {children}")
        left, operator, right = children
        return f"{left[1]} {operator[1]} {right[1]}"

    elif node_type == 'if_stmt':
        # Traitement pour 'if_stmt'
        if len(children) != 2:
            raise ValueError(f"Nœud 'if_stmt' mal formé : {children}")
        condition = children[0]
        body = children[1]
        
        # Code pour la condition
        condition_code = ast_to_c(condition, declared_vars, indent_level)
        
        # Code pour le corps du 'if'
        body_code = ""
        for stmt in body:
            body_code += ast_to_c(stmt, declared_vars, indent_level + 1)

        # Code pour l'instruction 'if'
        code = indent(f"if ({condition_code}) {{\n", indent_level)
        code += body_code
        code += indent("}\n", indent_level)
        return code

    elif node_type == 'body':
        # Si c'est le corps du `if`, on traite comme une liste d'instructions
        code = ""
        for stmt in children:
            code += ast_to_c(stmt, declared_vars, indent_level)
        return code
    
    elif node_type == 'program_rest':
        # Pour la partie restante du programme (autres instructions)
        code = ""
        for child in children:
            # Appel récursif pour chaque enfant, avec un niveau d'indentation approprié
            code += ast_to_c(child, declared_vars, indent_level)
        return code

    else:
        raise ValueError(f"Type de nœud non supporté : {node_type}")
