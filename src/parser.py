import re

def load_grammar(filename):
    """Charge la grammaire à partir d'un fichier."""
    grammar = {}
    with open(filename, 'r') as file:
        rules = file.read().strip().splitlines()
        for rule in rules:
            if '::=' in rule:
                lhs, rhs = rule.split('::=')
                lhs = lhs.strip()
                rhs = rhs.strip().split('|')
                grammar[lhs] = [r.strip() for r in rhs]
    return grammar

def resolve_variable_or_value(value, variables, line_number, errors):
    """
    Résout une valeur soit comme un entier littéral, soit comme une variable déclarée.
    """
    if isinstance(value, int):  # Si c'est déjà un entier, le retourner directement
        return value
    elif value.isdigit():  # Si c'est une chaîne qui représente un entier
        return int(value)
    elif value in variables and variables[value]["type"] == "int":  # Si c'est une variable valide
        return variables[value]["value"]
    else:  # Sinon, c'est une erreur
        errors.append((line_number, f"Invalid value: '{value}'"))
        return None

def analyze_if_statement(line, line_number, instructions, errors, context):
    """
    Analyse une ligne de type 'if', évalue la condition et exécute l'instruction correspondante.
    """
    # Vérifie la structure de base de l'if
    match = re.match(r'^if\s*\((.*?)\)\s*\{', line)
    if not match:
        errors.append((line_number, f"Invalid 'if' syntax: {line}"))
        return
    
    # Extraire la condition entre les parenthèses
    condition = match.group(1).strip()
    try:
        # Évaluer la condition dans un contexte sécurisé
        condition_result = eval(condition, {}, context)
    except Exception as e:
        errors.append((line_number, f"Erreur dans la condition '{condition}': {str(e)}"))
        return
    
    # Extraire le bloc de code entre les accolades
    block_match = re.search(r'\{(.*)\}', line, re.DOTALL)
    if not block_match:
        errors.append((line_number, "Le bloc de code '{}' est manquant ou incorrect."))
        return
    
    block_code = block_match.group(1).strip()
    
    if condition_result:
        # Si la condition est vraie, ajouter le code à exécuter
        instructions.append(("execute", block_code))
    else:
        # Si la condition est fausse, ignorer le bloc
        instructions.append(("skip", line))

def parse_code(code, grammar):
    """Analyse le code Draw++ en fonction de la grammaire et renvoie une liste d'instructions et les erreurs."""
    instructions = []
    errors = []
    lines = code.splitlines()
    stack = []  # Pile pour suivre les blocs imprimés
    variables = {}

    for line_number, line in enumerate(lines, start=1):
        # Supprimer les espaces en trop
        line = line.strip()
        if not line:
            continue
         # Gérer les déclarations de variables (par exemple: int x = 0)
        match = re.match(r'^(int|float)\s+([a-zA-Z_]\w*)\s*=\s*(\d+(\.\d*)?)$', line)
        if match:
            var_type = match.group(1)  # 'int' ou 'float'
            var_name = match.group(2)  # Nom de la variable
            value = float(match.group(3))  # La valeur (entier ou flottant)
            if var_name in variables:
                errors.append((line_number, f"Variable '{var_name}' already declared"))
            else:
                # Vérification du type et ajout dans le dictionnaire des variables
                if var_type == 'int' and not value.is_integer():
                    errors.append((line_number, f"Expected integer value for '{var_name}'"))
                else:
                    variables[var_name] = {"type": var_type, "value": int(value) if var_type == 'int' else float(value)}
                instructions.append(("declare", var_name, value))  # Enregistrer la déclaration
            continue
        
        # Modifier une variable déjà déclarée
        match = re.match(r'([a-zA-Z_]\w*)\s*=\s*(\d+(\.\d*)?)$', line)
        if match:
            var_name = match.group(1)
            new_value = float(match.group(2))

            if var_name in variables:
                var_type = variables[var_name]["type"]
                # Si la variable est de type 'int', on s'assure que la valeur est un entier
                if (var_type == 'int' and new_value.is_integer()) or (var_type == 'float' and isinstance(new_value, float)):
                    variables[var_name]["value"] = int(new_value) if var_type == 'int' else new_value
                    instructions.append(("modify", var_name, new_value))  # Enregistrer la modification
                else:
                    errors.append((line_number, f"Value type mismatch for '{var_name}'"))  # Erreur de type
            else:
                errors.append((line_number, f"Variable '{var_name}' not declared"))  # Erreur de variable non déclarée

        # Détecter les affectations de curseurs avec des commandes
        if re.match(r'^([a-zA-Z_]\w*)\s*=\s*move_to\s+([a-zA-Z_]\w*|\d+)\s+([a-zA-Z_]\w*|\d+)$', line):
            match = re.match(r'^([a-zA-Z_]\w*)\s*=\s*move_to\s+([a-zA-Z_]\w*|\d+)\s+([a-zA-Z_]\w*|\d+)', line)
            var_name, x_var, y_var = match.group(1), (match.group(2)), (match.group(3))

            # Résoudre les variables ou valeurs numériques
            x = resolve_variable_or_value(x_var, variables, line_number, errors)
            y = resolve_variable_or_value(y_var, variables, line_number, errors)

            if x is not None and y is not None:
                instructions.append(("move_to", var_name, x, y))

        if line.startswith("if"):
            # Vérification basique pour reconnaître un 'if'
            match = re.match(r'^if\s*\((.*?)\)', line)
            if match:
                instructions.append(("if_detected", line))
            else:
                errors.append((line_number, f"Invalid 'if' syntax: {line}"))
            continue

        if re.match(r'^([a-zA-Z_]\w*)\s*=\s*move_by\s+([a-zA-Z_]\w*|\d+)\s+([a-zA-Z_]\w*|\d+)$', line):
            match = re.match(r'^([a-zA-Z_]\w*)\s*=\s*move_by\s+([a-zA-Z_]\w*|\d+)\s+([a-zA-Z_]\w*|\d+)', line)
            var_name = match.group(1)  # Nom du curseur
            angle_var = (match.group(2))  # Angle en degrés
            distance_var = (match.group(3))  # Distance en pixels
            # Résoudre les variables ou valeurs numériques
            angle = resolve_variable_or_value(angle_var, variables, line_number, errors)
            distance = resolve_variable_or_value(distance_var, variables, line_number, errors)

            if angle is not None and distance is not None:
                instructions.append(("move_by", var_name, angle, distance))

        if re.match(r'^([a-zA-Z_]\w*)\s*=\s*line_by\s+(.+)\s+(.+)$', line):
            match = re.match(r'^([a-zA-Z_]\w*)\s*=\s*line_by\s+(.+)\s+(.+)', line)
            var_name = match.group(1)  # Nom du curseur
            angle_var = (match.group(2))  # Angle en degrés
            distance_var = (match.group(3))  # Distance en pixels

            # Résoudre les variables ou valeurs numériques
            angle = resolve_variable_or_value(angle_var, variables, line_number, errors)
            distance = resolve_variable_or_value(distance_var, variables, line_number, errors)

            if angle is not None and distance is not None:
                instructions.append(("line_by", var_name, angle, distance))

        if re.match(r'^([a-zA-Z_]\w*)\s*=\s*line_to\s+(.+)\s+(.+)$', line):
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*line_to\s+(.+)\s+(.+)', line)
            var_name, x_var, y_var = match.group(1), (match.group(2)), (match.group(3))
            # Résoudre les variables ou valeurs numériques
            x = resolve_variable_or_value(x_var, variables, line_number, errors)
            y = resolve_variable_or_value(y_var, variables, line_number, errors)

            if x is not None and y is not None:
                instructions.append(("line_to", var_name, x, y))

        if re.match(r'^([a-zA-Z_]\w*)\s*=\s*set_color\s+"(red|blue|green|black|yellow)"$', line):
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*set_color\s+"(.*?)"', line)
            var_name, color = match.group(1), match.group(2)
            instructions.append(("set_color", var_name, color))

        if re.match(r'^([a-zA-Z_]\w*)\s*=\s*circle\s+(.+)$', line):  # Accepter une variable ou une valeur numérique
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*circle\s+(.+)$', line)
            var_name, radius_var = match.group(1), (match.group(2))

            # Résoudre les variables ou valeurs numériques
            radius = resolve_variable_or_value(radius_var, variables, line_number, errors)

            if radius is not None:
                instructions.append(("circle", var_name, radius))

        if re.match(r'^[a-zA-Z_]\w*\s*=\s*cursor\s+"(red|blue|green|black|yellow)"\s+([a-zA-Z_]\w*|\d+)\s+([a-zA-Z_]\w*|\d+)$', line):
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*cursor\s+"(red|blue|green|black|yellow)"\s+([a-zA-Z_]\w*|\d+)\s+([a-zA-Z_]\w*|\d+)', line)
            var_name, color, x_var, y_var = match.group(1), match.group(2), match.group(3), match.group(4)

            # Résoudre les variables ou valeurs numériques
            x = resolve_variable_or_value(x_var, variables, line_number, errors)
            y = resolve_variable_or_value(y_var, variables, line_number, errors)

            if x is not None and y is not None:  # Ajouter l'instruction seulement si tout est valide
                instructions.append(("cursor", var_name, color, x, y))
        else:
            errors.append((line_number, line))  # Stocker la ligne d'erreur si la syntaxe n'est pas reconnue

    return instructions, errors