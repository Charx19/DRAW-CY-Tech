import ply.lex as lex
import ply.yacc as yacc

def load_grammar_from_bnf(filename):
    grammar_rules = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lhs, rhs = line.split("::=")
            lhs = lhs.strip()
            rhs = rhs.strip().split("|")
            for rule in rhs:
                grammar_rules.append((lhs, rule.strip().split()))
    return grammar_rules

def parse_code(code, grammar_file):
    """Parse le code en utilisant une grammaire BNF chargée dynamiquement."""
    # Charger la grammaire depuis le fichier
    grammar = load_grammar_from_bnf(grammar_file)

    # Définir les tokens
    tokens = [
        'IDENTIFIER', 'NUMBER', 'COLOR', 'MOVE_TO', 'LINE_TO', 'SET_COLOR', 'CIRCLE', 'MOVE_BY', 'IF', 'WHILE', 'EQ', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'ASSIGN', 'CURSOR'
    ]

    # Règles du lexer
    def t_CURSOR(t):
        r'cursor'  # Capture spécifiquement le mot-clé "cursor"
        print(f"Token CURSOR: {t.value}")  # Log pour le token CURSOR
        return t

    def t_COLOR(t):
        r'"(red|blue|green|black|yellow)"'
        print(f"Token COLOR: {t.value}")  # Log pour le token COLOR
        return t

    def t_IDENTIFIER(t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        print(f"Token IDENTIFIER: {t.value}")  # Log pour l'identifiant
        return t
    
    def t_NUMBER(t):
        r'\d+(\.\d+)?'  # Correspond à un nombre entier ou flottant
        print(f"Token NUMBER: {t.value}")  # Log pour afficher le token
        return t

    def t_MOVE_TO(t):
        r'move_to'
        print(f"Token MOVE_TO: {t.value}")  # Log pour MOVE_TO
        return t

    def t_LINE_TO(t):
        r'line_to'
        print(f"Token LINE_TO: {t.value}")  # Log pour LINE_TO
        return t

    def t_SET_COLOR(t):
        r'set_color'
        print(f"Token SET_COLOR: {t.value}")  # Log pour SET_COLOR
        return t

    def t_CIRCLE(t):
        r'circle'
        print(f"Token CIRCLE: {t.value}")  # Log pour CIRCLE
        return t

    def t_MOVE_BY(t):
        r'move_by'
        print(f"Token MOVE_BY: {t.value}")  # Log pour MOVE_BY
        return t

    def t_IF(t):
        r'if'
        print(f"Token IF: {t.value}")  # Log pour IF
        return t

    def t_WHILE(t):
        r'while'
        print(f"Token WHILE: {t.value}")  # Log pour WHILE
        return t

    def t_EQ(t):
        r'=='
        print(f"Token EQ: {t.value}")  # Log pour EQ
        return t

    def t_NEQ(t):
        r'!='
        print(f"Token NEQ: {t.value}")  # Log pour NEQ
        return t

    def t_LT(t):
        r'<'
        print(f"Token LT: {t.value}")  # Log pour LT
        return t

    def t_GT(t):
        r'>'
        print(f"Token GT: {t.value}")  # Log pour GT
        return t

    def t_LEQ(t):
        r'<='
        print(f"Token LEQ: {t.value}")  # Log pour LEQ
        return t

    def t_GEQ(t):
        r'>='
        print(f"Token GEQ: {t.value}")  # Log pour GEQ
        return t

    def t_LPAREN(t):
        r'\('
        print(f"Token LPAREN: {t.value}")  # Log pour LPAREN
        return t

    def t_RPAREN(t):
        r'\)'
        print(f"Token RPAREN: {t.value}")  # Log pour RPAREN
        return t

    def t_LBRACE(t):
        r'\{'
        print(f"Token LBRACE: {t.value}")  # Log pour LBRACE
        return t

    def t_RBRACE(t):
        r'\}'
        print(f"Token RBRACE: {t.value}")  # Log pour RBRACE
        return t

    def t_COMMA(t):
        r','
        print(f"Token COMMA: {t.value}")  # Log pour COMMA
        return t

    def t_ASSIGN(t):
        r'='
        print(f"Token ASSIGN: {t.value}")  # Log pour ASSIGN
        return t
    # Ignorer les espaces et les tabulations
    t_ignore = ' \t\n'

    # Fonction d'erreur pour le lexer
    def t_error(t):
        print(f"Erreur de token: {t.value}")
        t.lexer.skip(1)

    # Initialiser le lexer
    lexer = lex.lex()

    # Définir les règles du parser
    def p_program(p):
        """program : instruction"""
        print(f"Règle appliquée: program")
        p[0] = p[1]

    def p_instruction_declaration(p):
        """instruction : declaration"""
        print(f"Règle appliquée: instruction_declaration")
        p[0] = ('declaration', p[1])

    def p_instruction_action(p):
        """instruction : action"""
        print(f"Règle appliquée: instruction_action")
        p[0] = ('action', p[1])

    def p_declaration(p):
        """declaration : IDENTIFIER ASSIGN NUMBER"""
        print(f"Déclaration de la variable {p[1]} avec la valeur {p[3]}")
        p[0] = ('declaration', p[1], p[3])
    def p_cursor(p):
        """cursor : IDENTIFIER ASSIGN CURSOR COLOR NUMBER COMMA NUMBER"""
        print(f"Curseur: {p[2]}, X: {p[4]}, Y: {p[6]}")
        p[0] = ('cursor', p[2], p[4], p[6])
    def p_action_move_to(p):
        """action : IDENTIFIER ASSIGN MOVE_TO NUMBER COMMA NUMBER"""
        print(f"Action: move_to, Identifiant: {p[1]}, X: {p[4]}, Y: {p[6]}")
        p[0] = ('move_to', p[1], p[4], p[6])

    def p_action_line_to(p):
        """action : IDENTIFIER ASSIGN LINE_TO NUMBER COMMA NUMBER"""
        print(f"Action: line_to, Identifiant: {p[1]}, X: {p[4]}, Y: {p[6]}")
        p[0] = ('line_to', p[1], p[4], p[6])

    def p_action_set_color(p):
        """action : IDENTIFIER ASSIGN SET_COLOR COLOR"""
        print(f"Action: set_color, Identifiant: {p[1]}, Couleur: {p[4]}")
        p[0] = ('set_color', p[1], p[4])

    def p_action_circle(p):
        """action : IDENTIFIER ASSIGN CIRCLE NUMBER"""
        print(f"Action: circle, Identifiant: {p[1]}, Rayon: {p[4]}")
        p[0] = ('circle', p[1], p[4])

    def p_action_move_by(p):
        """action : IDENTIFIER ASSIGN MOVE_BY NUMBER COMMA NUMBER"""
        print(f"Action: move_by, Identifiant: {p[1]}, Delta X: {p[4]}, Delta Y: {p[6]}")
        p[0] = ('move_by', p[1], p[4], p[6])

    def p_error(p):
        if p:
            print(f"Erreur de syntaxe: '{p.value}' à la ligne {p.lineno}")
        else:
            print("Erreur de syntaxe à la fin du fichier.")

    # Créer le parser avec la grammaire chargée
    parser = yacc.yacc()

    # Analyser le code
    errors = []
    try:
        instructions = parser.parse(code, lexer=lexer)
    except SyntaxError as e:
        line_number = e.args[0].split('Ligne')[1].strip().split(',')[0]
        errors.append((int(line_number), e.args[0]))
        instructions = None

    return instructions, errors
