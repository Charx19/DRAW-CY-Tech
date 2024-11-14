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
        
        # Analyser la ligne selon les règles de la grammaire
        if re.match(r'^move_to\s+\d+\s*,\s*\d+$', line):
            match = re.match(r'move_to\s+(\d+)\s*,\s*(\d+)', line)
            x, y = int(match.group(1)), int(match.group(2))
            instructions.append(("move_to", x, y))
        elif re.match(r'^line_to\s+\d+\s*,\s*\d+$', line):
            match = re.match(r'line_to\s+(\d+)\s*,\s*(\d+)', line)
            x, y = int(match.group(1)), int(match.group(2))
            instructions.append(("line_to", x, y))
        elif re.match(r'^set_color\s+"(red|blue|green|black|yellow)"$', line):
            match = re.match(r'set_color\s+"(.*?)"', line)
            color = match.group(1)
            instructions.append(("set_color", color))
        elif re.match(r'^circle\s+\d+$', line):
            match = re.match(r'circle\s+(\d+)', line)
            radius = int(match.group(1))
            instructions.append(("circle", radius))
        else:
            errors.append((line_number, line))  # Stocker la ligne d'erreur

    print("Returning:", instructions, errors)  # Debugging line
    return instructions, errors  # Make sure to return both
