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

def parse_code(code, grammar):
    """Analyse le code Draw++ en fonction de la grammaire et renvoie une liste d'instructions et les erreurs."""
    instructions = []
    errors = []
    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        # Supprimer les espaces en trop
        line = line.strip()
        if not line:
            continue
        
        # Détecter les affectations de curseurs avec des commandes
        if re.match(r'^([a-zA-Z_]\w*)\s*=\s*move_to\s+(\d+)\s+(\d+)$', line):
            # Ex: cursor1 = move_to 100 100
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*move_to\s+(\d+)\s+(\d+)', line)
            var_name, x, y = match.group(1), int(match.group(2)), int(match.group(3))
            instructions.append(("move_to", var_name, x, y))
        elif re.match(r'^([a-zA-Z_]\w*)\s*=\s*move_by\s+(\d+)\s+(\d+)$', line):
            match = re.match(r'^([a-zA-Z_]\w*)\s*=\s*move_by\s+(\d+)\s+(\d+)', line)
            var_name = match.group(1)  # Nom du curseur
            angle = int(match.group(2))  # Angle en degrés
            distance = int(match.group(3))  # Distance en pixels
            instructions.append(("move_by", var_name, angle, distance))
        elif re.match(r'^([a-zA-Z_]\w*)\s*=\s*line_by\s+(\d+)\s+(\d+)$', line):
            match = re.match(r'^([a-zA-Z_]\w*)\s*=\s*line_by\s+(\d+)\s+(\d+)', line)
            var_name = match.group(1)  # Nom du curseur
            angle = int(match.group(2))  # Angle en degrés
            distance = int(match.group(3))  # Distance en pixels
            instructions.append(("line_by", var_name, angle, distance))
        elif re.match(r'^([a-zA-Z_]\w*)\s*=\s*line_to\s+(\d+)\s+(\d+)$', line):
            # Ex: cursor1 = line_to 150 150
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*line_to\s+(\d+)\s+(\d+)', line)
            var_name, x, y = match.group(1), int(match.group(2)), int(match.group(3))
            instructions.append(("line_to", var_name, x, y))
        elif re.match(r'^([a-zA-Z_]\w*)\s*=\s*set_color\s+"(red|blue|green|black|yellow)"$', line):
            # Ex: cursor1 = set_color "red"
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*set_color\s+"(.*?)"', line)
            var_name, color = match.group(1), match.group(2)
            instructions.append(("set_color", var_name, color))
        elif re.match(r'^([a-zA-Z_]\w*)\s*=\s*circle\s+\d+$', line):
            # Ex: cursor1 = circle 30
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*circle\s+(\d+)', line)
            var_name, radius = match.group(1), int(match.group(2))
            instructions.append(("circle", var_name, radius))
        elif re.match(r'^[a-zA-Z_]\w*\s*=\s*cursor\s+"(red|blue|green|black|yellow)"\s+\d+\s+\d+$', line):
            # Ex: cursor1 = cursor "red" 100 100
            match = re.match(r'([a-zA-Z_]\w*)\s*=\s*cursor\s+"(red|blue|green|black|yellow)"\s+(\d+)\s+(\d+)', line)
            var_name, color, x, y = match.group(1), match.group(2), int(match.group(3)), int(match.group(4))
            instructions.append(("cursor", var_name, color, x, y))
        else:
            errors.append((line_number, line))  # Stocker la ligne d'erreur

    return instructions, errors
