def parse_code(code):
    """Analyse le code Draw++ et renvoie une liste d'instructions."""
    instructions = []
    lines = code.splitlines()
    
    for line in lines:
        tokens = line.split()
        if not tokens:
            continue

        command = tokens[0].lower()
        
        if command == "move_to":
            x = int(tokens[1])
            y = int(tokens[2])
            instructions.append((command, x, y))
        elif command == "line_to":
            x = int(tokens[1])
            y = int(tokens[2])
            instructions.append((command, x, y))
        elif command == "set_color":
            color = tokens[1]
            instructions.append((command, color))
        elif command == "circle":
            radius = int(tokens[1])
            instructions.append((command, radius))
        else:
            raise ValueError(f"Instruction inconnue : '{command}'")
    
    return instructions
