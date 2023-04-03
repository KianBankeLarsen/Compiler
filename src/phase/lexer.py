import ply.lex as lex

import utils.error as error

reserved = {
    'print': 'PRINT',
    'return': 'RETURN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'int': 'INT_TYPE',
    'float': 'FLOAT_TYPE',
    'bool': 'BOOL_TYPE',
    'void': 'VOID_TYPE',
    'for': 'FOR'
}

tokens = (
    'IDENT', 'INT', 'FLOAT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LCURL', 'RCURL',
    'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    'ASSIGN', 'COMMA', 'SEMICOL'
) + tuple(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_COMMA = r','
t_SEMICOL = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURL = r'{'
t_RCURL = r'}'
t_EQ = r'=='
t_NEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_ignore = " \t\r"


def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENT')    # Check for reserved words
    return t


def t_FLOAT(t):
    r'(0|[1-9][0-9]*)\.[0-9]+'
    try:
        t.value = float(t.value)
    except ValueError:
        error.error_message(
            "Lexical Analysis",
            "Float value too large.",
            t.lexer.lineno)
    return t


def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        error.error_message(
            "Lexical Analysis",
            "Integer value too large.",
            t.lexer.lineno)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_COMMENT(t):
    r'\#.*'
    pass


def t_error(t):
    error.error_message(
        "Lexical Analysis",
        f"Illegal character '{t.value[0]}'.",
        t.lexer.lineno)


lexer = lex.lex()
