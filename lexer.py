import ply.lex as lex

# List of tokens
tokens = [
    'MOVE_TO',
    'LINE_TO',
    'SET_COLOR',
    'CIRCLE',
    'NUMBER',
    'STRING',
    'NEWLINE',
    'RECTANGLE', 
    'TRIANGLE', 
    'COLOR', 
    'SINGLELINE_COMMENT',
    'MULTILINE_COMMENT',
]

# Definition of regular expressions for the tokens
t_MOVE_TO = r'move_to'
t_LINE_TO = r'line_to'
t_SET_COLOR = r'set_color'
t_CIRCLE = r'circle'
t_RECTANGLE = r'rectangle'
t_TRIANGLE = r'triangle'
t_NUMBER = r'\d+'
t_STRING = r'\".*?\"'  # Strings enclosed in quotes

# Colors
def t_COLOR(t):
    r'red|blue|green|black|yellow'
    return t

# Ignore spaces and tabs
t_ignore = ' \t'

# Handling newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_SINGLELINE_COMMENT(t):
    r'//.*'
    pass  #  Ignore single-line comments

def t_MULTILINE_COMMENT(t):
    r'/\*.*?\*/'
    pass  # Ignore multi-line comments

# Error handling
def t_error(t):
    print(f"Erreur de lexing à la ligne {t.lineno}: {t.value}")
    t.lexer.skip(1)

# Creating the lexer
lexer = lex.lex()
