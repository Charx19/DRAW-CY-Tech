def ast_to_c(ast, declared_vars=None, indent_level=0):
    """
    Translation from AST to C.

    Parameters:
    - ast :  Abstract syntaxical tree to represent the program
    - declared_vars : All the declared values
    - indent_level : The indentation for the generated code

    Return:
    - str : the generated C code
    """
    if declared_vars is None:
        declared_vars = set()  # All declared

    if not ast:
        print("Ce n'est pas un AST valide")
        return ""

    # Checking if tuple with at least 2 elements
    if not isinstance(ast, tuple) or len(ast) != 2:
        raise ValueError(f"AST mal formé, doit être un tuple de type (node_type, children), mais reçu : {ast}")

    # Decomposing of the AST
    node_type, children = ast

    # Function to add the indentation
    def indent(code, level):
        return "    " * level + code

    print(f"Type de nœud : {node_type}, Enfants : {children}")

    # Which node type for each function
    if node_type == 'program':
        # For the program, we generate the beginning of the code with our biblio
        code = "#include <stdio.h>\n#include <string.h>\n#include \"graphic.h\"\n\n"  # Ajout des bibliothèques
        
        #  Function to create our cursor
        code += "Cursor create_cursor(const char* color, int x, int y) {\n"
        code += "    Cursor c;\n"
        code += "    strcpy(c.color, color);\n"
        code += "    c.x = x;\n"
        code += "    c.y = y;\n"
        code += "    return c;\n"
        code += "}\n\n"

        # Generate the WinMain function
        code += "int WinMain(int argc, char **argv) {\n"
        code += "    init_graphics();  // Initialisation du système graphique\n"
        code += "    int current_y, current_x;\n"
        code += "    char current_color[20];  \n"
        # Generate the child 
        for child in children:
            # Recursive function for each child with a new level of indentation
            code += ast_to_c(child, declared_vars, indent_level + 1)
        
         # Add primairy loop  SDL
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

        # End of the graphical system and end of WinMain
        code += indent("close_graphics();  // Fermer le système graphique\n", indent_level + 1)
        code += indent("return 0;\n", indent_level + 1)
        code += "}\n"
        return code

    elif node_type == 'assign_stmt':
        # For assignments, children must be a list containing exactly 2 elements
        if not isinstance(children, list) or len(children) != 2:
            raise ValueError(f"Nœud d'assignation mal formé : {children}")
        identifier = children[0]
        value = children[1]

        #  If the value isn't declared, we call it 'int'
        if identifier not in declared_vars:
            declared_vars.add(identifier)
            code = indent(f"int {identifier} = {value};\n", indent_level)
        else:
            code = indent(f"{identifier} = {value};\n", indent_level)

        return code

    elif node_type == 'cursor_stmt':
        #  For the cursor, we are expecting an identificant, color , two coordinates and a size
        if len(children) != 4:
            raise ValueError(f"Nœud de curseur mal formé : {children}")
        identifier = children[0]
        color = children[1]
        x = children[2]
        y = children[3]
        # Declaration of the variable and initialization with the arguments passed
        code = indent(f"Cursor {identifier} = create_cursor({color}, {x}, {y});\n", indent_level)
        code += indent(f"add_cursor({identifier}.color, {identifier}.x, {identifier}.y);\n", indent_level)
        code += indent(f"cursor({color}, {x}, {y}, 10);\n", indent_level)
        code += indent(f"current_x = {x};\n", indent_level)
        code += indent(f"current_y = {y};\n", indent_level)
        code += indent(f"strcpy(current_color, {color});\n", indent_level)
        return code
    
    elif node_type == 'move_stmt':
        # For the movement, we expect an identifier and two coordinates
        if len(children) != 3:
            raise ValueError(f"Nœud de mouvement mal formé : {children}")
        identifier = children[0]
        x = children[1]
        y = children[2]
        # Code to move the cursor to the new position
        code = indent(f"move_to(&{identifier}, {x}, {y});\n", indent_level)
        code += indent(f"current_x = {x};\n", indent_level)
        code += indent(f"current_y = {y};\n", indent_level)
        
        return code
    
    elif node_type == 'line_to':
        # For the movement, we expect an identifier and two coordinates
        if len(children) != 3:
            raise ValueError(f"Nœud de mouvement mal formé : {children}")
        identifier = children[0]
        x = children[1]
        y = children[2]
        # Code to move the cursor to the new position
        code = indent(f"line_to({identifier}, {x}, {y});\n", indent_level)
        code+= indent(f"add_line(current_x, current_y, {x}, {y}, current_color);\n", indent_level)
        return code
    
    elif node_type == 'circle':
        # For the movement, we expect an identifier and two coordinates
        if len(children) != 2:
            raise ValueError(f"Nœud de mouvement mal formé : {children}")
        identifier = children[0]
        x = children[1]
        # Code to move the cursor to the new position
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
        # Handle expressions as a == 8, x > 10, etc.
        if len(children) != 3:
            raise ValueError(f"Nœud 'expression' mal formé : {children}")
        left, operator, right = children
        return f"{left[1]} {operator[1]} {right[1]}"

    elif node_type == 'if_stmt':
        # Processing for 'if_stmt'
        if len(children) != 2:
            raise ValueError(f"Nœud 'if_stmt' mal formé : {children}")
        condition = children[0]
        body = children[1]
        
        # Code for condition
        condition_code = ast_to_c(condition, declared_vars, indent_level)
        
        # Code for the body of the 'if'
        body_code = ""
        for stmt in body:
            body_code += ast_to_c(stmt, declared_vars, indent_level + 1)

        # Code for the instruction 'if'
        code = indent(f"if ({condition_code}) {{\n", indent_level)
        code += body_code
        code += indent("}\n", indent_level)
        return code

    elif node_type == 'body':
        # If it is the body of the `if`, it is treated as a list of instructions
        code = ""
        for stmt in children:
            code += ast_to_c(stmt, declared_vars, indent_level)
        return code
    
    elif node_type == 'program_rest':
        # For the remaining part of the program (further instructions)
        code = ""
        for child in children:
            # Recursive call for each child, with an appropriate level of indentation
            code += ast_to_c(child, declared_vars, indent_level)
        return code

    else:
        raise ValueError(f"Type de nœud non supporté : {node_type}")
