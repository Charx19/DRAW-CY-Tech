import re

token_specifications = [
    ('NUMBER', r'\d+(\.\d+)?'),
    ('CURSOR', r'cursor'),
    ('MOVE_TO', r'move_to'),
    ('LINE_TO', r'line_to'),
    ('CIRCLE', r'circle'),
    ('IF', r'if'),
    ('END', r'end'),
    ('THEN', r'then'),
    ('COLOR', r'"(red|blue|green|black|yellow)"'),
    ('EQUALS', r'=='),
    ('ASSIGN', r'='),
    ('NEQ', r'!='),
    ('GREATER_THAN', r'>'),
    ('LOWER_THAN', r'<'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('COMMA', r','),
    ('SKIP', r'[ \t\n]+'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
]

class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.tokens = []
        self.line = 1
        self.column = 1

    def get_tokens(self):
        while self.position < len(self.code):
            match = None
            for token_type, regex in token_specifications:
                regex_match = re.match(regex, self.code[self.position:])
                if regex_match:
                    match = regex_match.group(0)
                    if token_type != 'SKIP':
                        # Ajouter ligne et colonne dans les tokens
                        self.tokens.append((token_type, match, self.line, self.column))
                    # Mise à jour de la position et de la colonne
                    if token_type == 'SKIP' and '\n' in match:
                        # Gérer les retours à la ligne pour `SKIP`
                        self.line += match.count('\n')
                        self.column = 1
                    else:
                        self.column += len(match)
                    break
            if not match:
                raise RuntimeError(f"Illegal character at line {self.line}, column {self.column}")
            else:
                self.position += len(match)
        return self.tokens
