import sys
import ply.lex as lex
import ply.yacc as yacc

import AST


####################### LEXER #######################
reserved = {
}

tokens = (
    'IDENT', 'INT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN',
    'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    'ASSIGN', 'SEMICOL',
) + tuple(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_SEMICOL = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQ = r'=='
t_NEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='

def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENT')    # Check for reserved words
    return t

def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Lexical Analysis",
                f"Integer value too large.",
                t.lexer.lineno)
        t.value = 0
    if t.value > int('0x7FFFFFFFFFFFFFFF', base=16):
        print("Lexical Analysis",
                f"Integer value too large.",
                t.lexer.lineno)
        t.value = 0
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore = " \t\r"  # \r included for the sake of windows users

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_COMMENT(t):
    r'\#.*'
    pass

# TODO do right
def t_error(t):
    print("Lexical Analysis",
        f"Illegal character '{t.value[0]}'.",
        t.lexer.lineno)
    sys.exit(1)


####################### PARSER #######################
# First production identifies the start symbol
the_program = None
def p_program(t):
    'program : body'
    the_program = AST.function(
        "main", None, t[1], t.lexer.lineno)

def p_body(t):
    'body : statement_list'
    t[0] = AST.body(None, None, t[1], t.lexer.lineno)

def p_statement_list(t):
    '''statement_list : statement
                    | statement statement_list'''
    if len(t) == 2:
        t[0] = AST.statement_list(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.statement_list(t[1], t[2], t.lexer.lineno)

def p_statement(t):
    '''statement : statement_assignment'''
    t[0] = t[1]

def p_statement_assignment(t):
    'statement_assignment : IDENT ASSIGN expression SEMICOL'
    t[0] = AST.statement_assignment(t[1], t[3], t.lexer.lineno)

def p_expression(t):
    '''expression : expression_integer
                | expression_identifier
                | expression_binop
                | expression_group'''
    t[0] = t[1]

def p_expression_integer(t):
    'expression_integer : INT'
    t[0] = AST.expression_integer(t[1], t.lexer.lineno)

def p_expression_identifier(t):
    'expression_identifier : IDENT'
    t[0] = AST.expression_identifier(t[1], t.lexer.lineno)

def p_expression_binop(t):
    '''expression_binop : expression PLUS expression
                        | expression MINUS expression
                        | expression TIMES expression
                        | expression DIVIDE expression
                        | expression EQ expression
                        | expression NEQ expression
                        | expression LT expression
                        | expression GT expression
                        | expression LTE expression
                        | expression GTE expression'''
    t[0] = AST.expression_binop(t[2], t[1], t[3], t.lexer.lineno)

def p_expression_group(t):
    'expression_group : LPAREN expression RPAREN'
    t[0] = t[2]


def p_error(t):
    try:
        cause = f" at '{t.value}'"
        location = t.lexer.lineno
    except AttributeError:
        cause = " - check for missing closing braces"
        location = "unknown"
    print("Syntax Analysis",
                  f"Problem detected{cause}.",
                  location)

# Build the lexer
lexer = lex.lex()

# Build the parser
parser = yacc.yacc()
    

class LexerParser:
    def __init__(self):
        parser.parse(input("Write something: \n"), lexer=lexer)
        self.the_program = the_program