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
        
        matched = False
        for lhs, rhs_list in grammar.items():
            for rhs in rhs_list:
                # Nous utilisons une expression régulière plus souple pour chaque règle
                pattern = re.compile(rhs)
                match = pattern.match(line)
                
                if match:
                    # Analyser la ligne en fonction de la règle
                    if lhs == "MoveTo":
                        match = re.match(r'move_to\s*(\d+)\s*,\s*(\d+)', line)
                        if match:
                            x, y = int(match.group(1)), int(match.group(2))
                            instructions.append(("move_to", x, y))
                    elif lhs == "LineTo":
                        match = re.match(r'line_to\s*(\d+)\s*,\s*(\d+)', line)
                        if match:
                            x, y = int(match.group(1)), int(match.group(2))
                            instructions.append(("line_to", x, y))
                    elif lhs == "SetColor":
                        match = re.match(r'set_color\s+(red|blue|green|black|yellow)', line)
                        if match:
                            color = match.group(1)
                            instructions.append(("set_color", color))
                    elif lhs == "Circle":
                        match = re.match(r'circle\s*(\d+)', line)
                        if match:
                            radius = int(match.group(1))
                            instructions.append(("circle", radius))
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            errors.append((line_number, line))  # Stocker la ligne d'erreur

    return instructions, errors
