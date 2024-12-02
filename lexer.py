import ply.lex as lex

# Liste des tokens
tokens = [
    'MOVE_TO',
    'MOVE_BY',
    'LINE_TO',
    'SET_COLOR',
    'CIRCLE',
    'CURSOR',
    'NUMBER',
    'STRING',
    'NEWLINE',
    'LINE_BY',
]

# Définition des expressions régulières pour les tokens
t_MOVE_TO = r'move_to'
t_MOVE_BY = r'move_by'
t_LINE_TO = r'line_to'
t_SET_COLOR = r'set_color'
t_CIRCLE = r'circle'
t_CURSOR = r'cursor' 
t_NUMBER = r'\d+'
t_LINE_BY = r'line_by'
t_STRING = r'\".*?\"'  # Chaînes entre guillemets

# Ignorer les espaces et tabulations
t_ignore = ' \t'

# Traitement des nouvelles lignes
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Gestion des erreurs
def t_error(t):
    print(f"Erreur de lexing à la ligne {t.lineno}: {t.value}")

# Création du lexer
lexer = lex.lex()
