class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []  #  list to accumulate errors

    def parse(self):
        return self.program()
    def peek_token(self, offset):
        """
        Regarde un token à une position relative sans le consommer.
        """
        peek_position = self.position + offset
        if peek_position < len(self.tokens):
            return self.tokens[peek_position]
        else:
            return None, None
        
    def expression(self):
        left = self.current_token()
        if left[0] not in ['IDENTIFIER', 'NUMBER']:
            line, column = left[2], left[3]
            raise SyntaxError(f"Unexpected token in expression: {left[0]} at line {line}, column {column}")
        self.position += 1

        operator = self.current_token()
        if operator[0] not in ['GREATER_THAN', 'LOWER_THAN', 'EQUALS']:
            line, column = operator[2], operator[3]
            raise SyntaxError(f"Unexpected operator in expression: {operator[0]} at line {line}, column {column}")
        self.position += 1

        right = self.current_token()
        if right[0] not in ['IDENTIFIER', 'NUMBER']:
            line, column = right[2], right[3]
            raise SyntaxError(f"Unexpected token in expression: {right[0]} at line {line}, column {column}")
        self.position += 1

        return ('expression', [left, operator, right])
    
    def block(self):
        instructions = []
        while self.current_token()[0] not in ['END', 'ELSE', 'ELSE_IF']:
            instructions.append(self.instruction())
        return instructions
    
    def program(self):
        instructions = []
        instructions.append(self.instruction())
        instructions.append(self.program_rest())
        return ('program', instructions)

    def program_rest(self):
        instructions = []
        while self.current_token()[0] in ['CURSOR', 'MOVE_TO', 'IDENTIFIER', 'MOVE_TO', 'LINE_TO', 'CIRCLE', 'IF']:
            instructions.append(self.instruction())
        return ('program_rest', instructions)

    def instruction(self):
        token = self.current_token()
        line, column = token[2], token[3]
        if token[0] == 'CURSOR':  # if token is 'Cursor', analyse as a declaration of a cursor
            return self.cursor_stmt()
        elif token[0] == 'MOVE_TO':  # if token is 'MOVE_TO', analyse like a movement
            return self.move_stmt()
        elif token[0] == 'IF':
            return self.if_stmt()
        elif token[0] == 'IDENTIFIER':  # if it's an identifiant, verify the nature of the instruction
            next_token = self.peek_token(1)  # check the next token
            if not next_token:
                self.errors.append(f"Unexpected end of input after IDENTIFIER at line {line}, column {column}")
                return None
            if next_token[0] == 'EQUALS':  
                return self.equals_stmt()
            elif next_token[0] == 'ASSIGN':  #  if next token is '=', its a assignation
                return self.assign_stmt()
            elif next_token[0] == 'CURSOR':  # if next token is 'CURSOR', its declareted in cursor               
                return self.cursor_stmt()
            elif next_token[0] == 'MOVE_TO':  # if next token is 'MOVE_TO', it's a movement 
                return self.move_stmt()
            elif next_token[0] == 'LINE_TO':  # if next token is  'LINE_TO', it's a line
                return self.line_to()
            elif next_token[0] == 'CIRCLE':  # if next token is a cercle, then circle
                return self.circle()
            else:
                self.errors.append(f"Unexpected token after IDENTIFIER: {next_token[0]} at line {line}, column {column}")
                self.position += 1  
                return None
        else:
            self.errors.append(f"Unexpected token: {token[0]} at line {line}, column {column}")
            self.position += 1  
            return None

    def cursor_stmt(self):
        identifier = self.consume('IDENTIFIER')  # Identifier pour la variable
        self.consume('CURSOR')  # Mot-clé 'cursor'
        color = self.consume('COLOR')  # Couleur du curseur
        x = self.consume('NUMBER')  # Coordonnée x
        y = self.consume('NUMBER')  # Coordonnée y
        return ('cursor_stmt', [identifier, color, x, y])

    def move_stmt(self):
        identifier = self.consume('IDENTIFIER')  # Identifier pour la variable
        self.consume('MOVE_TO')
        x = self.consume('NUMBER')
        y = self.consume('NUMBER')
        return ('move_stmt', [identifier, x, y])

    def line_to(self):
        identifier = self.consume('IDENTIFIER')  # Identifier pour la variable
        self.consume('LINE_TO')
        x = self.consume('NUMBER')
        y = self.consume('NUMBER')
        return ('line_to', [identifier, x, y])
    
    def circle(self):
        identifier = self.consume('IDENTIFIER')  # Identifier pour la variable
        self.consume('CIRCLE')
        x = self.consume('NUMBER')
        return ('circle', [identifier, x])
    
    def if_stmt(self):
        self.consume('IF')  # Consommer le token 'IF'
        condition = self.expression()  # Analyser l'expression conditionnelle
        self.consume('THEN')  # Consommer le token 'THEN'
        body = self.block()  # Analyser le bloc d'instructions du corps du 'if'
        # Assurez-vous que chaque instruction dans le corps est bien sous la forme (node_type, children)
        body_formatted = []
        for stmt in body:
            if isinstance(stmt, tuple):  # Si l'instruction est déjà formatée sous forme de tuple
                body_formatted.append(stmt)
            else:
                # Si l'instruction n'est pas encore formatée, on l'entoure avec un tuple
                body_formatted.append(('instruction', stmt))

        # Retourner l'AST du 'if_stmt' avec le corps formaté
        return ('if_stmt', [condition, body])
    
    def assign_stmt(self):
        identifier = self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        value = self.consume('NUMBER')
        return ('assign_stmt', [identifier, value])
    
    def equals_stmt(self):
        identifier = self.consume('IDENTIFIER')
        self.consume('EQUALS')
        value = self.consume('NUMBER')
        return ('equals_stmt', [identifier, value])

    def consume(self, expected_type):
        token = self.current_token()
        if token[0] == expected_type:
            self.position += 1
            return token[1]
        else:
            line, column = token[2], token[3]
            # Ajouter l'erreur dans la liste, mais ne pas lever une exception
            self.errors.append(f"Expected {expected_type} but found {token[0]} at line {line}, column {column}")
            # Passer au prochain token pour éviter une boucle infinie
            self.position += 1
            return None

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        else:
            return None, None
