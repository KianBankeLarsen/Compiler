import sys

import ply.lex as lex
import ply.yacc as yacc

import AST
import interfacing_parser

############################################## LEXER ##############################################
reserved = {
    'print': 'PRINT',
    'return': 'RETURN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'int': 'INT_TYPE',
    'float': 'FLOAT_TYPE',
    'bool': 'BOOL_TYPE',
    'for': 'FOR'
}

tokens = (
    'IDENT', 'INT',
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

precedence = (
    ('right', 'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


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
        sys.exit(1)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_COMMENT(t):
    r'\#.*'
    pass


def t_error(t):
    print("Lexical Analysis",
          f"Illegal character '{t.value[0]}'.",
          t.lexer.lineno)
    sys.exit(1)


############################################## PARSER ##############################################
# First production identifies the start symbol
def p_program(t):
    'program : body'
    interfacing_parser.the_program = AST.Function(
        ".main", None, t[1], t.lexer.lineno)


def p_empty(t):
    'empty :'
    t[0] = None


def p_body(t):
    'body : optional_declarations optional_statement_list'
    t[0] = AST.Body(t[1], t[2], t.lexer.lineno)


def p_optional_declaration(t):
    '''optional_declarations : empty
                            | declaration_list'''
    t[0] = t[1]


def p_declaration_list(t):
    '''declaration_list : declaration
                        | declaration declaration_list'''
    if len(t) == 2:
        t[0] = AST.DeclarationList(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.DeclarationList(t[1], t[2], t.lexer.lineno)


def p_declaration(t):
    '''declaration : type function
                | type variables_list SEMICOL'''
    t[0] = AST.Declaration(t[1], t[2], t.lexer.lineno)


def p_variables_list(t):
    '''variables_list : IDENT
                      | IDENT COMMA variables_list'''
    if len(t) == 2:
        t[0] = AST.VariableList(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.VariableList(t[1], t[3], t.lexer.lineno)


def p_function(t):
    'function : IDENT LPAREN optional_parameter_list RPAREN LCURL body RCURL'
    t[0] = AST.Function(t[1], t[3], t[6], t.lexer.lineno)


def p_optional_parameter_list(t):
    '''optional_parameter_list : empty
                               | parameter_list'''
    t[0] = t[1]


def p_parameter_list(t):
    '''parameter_list : param
                      | param COMMA parameter_list'''
    if len(t) == 2:
        t[0] = AST.ParameterList(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.ParameterList(t[1], t[3], t.lexer.lineno)


def p_param(t):
    '''param : type IDENT'''
    t[0] = AST.Parameter(t[1], t[2], t.lexer.lineno)


def p_type(t):
    '''type : INT_TYPE
            | FLOAT_TYPE
            | BOOL_TYPE'''
    t[0] = t[1]


def p_optional_statement_list(t):
    '''optional_statement_list : empty
                            | statement_list'''
    t[0] = t[1]


def p_statement_list(t):
    '''statement_list : statement
                    | statement statement_list'''
    if len(t) == 2:
        t[0] = AST.StatementList(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.StatementList(t[1], t[2], t.lexer.lineno)


def p_statement(t):
    '''statement : statement_return  
                | statement_assignment
                | statement_ifthenelse
                | statement_print
                | statement_while
                | statement_for
                | statement_compound
                | statement_call'''
    t[0] = t[1]


def p_statement_return(t):
    'statement_return : RETURN expression SEMICOL'
    t[0] = AST.StatementReturn(t[2], t.lexer.lineno)


def p_statement_print(t):
    'statement_print : PRINT LPAREN expression RPAREN SEMICOL'
    t[0] = AST.StatementPrint(t[3], t.lexer.lineno)


def p_statement_assignment(t):
    'statement_assignment : IDENT ASSIGN expression SEMICOL'
    t[0] = AST.StatementAssignment(t[1], t[3], t.lexer.lineno)


def p_statement_ifthenelse(t):
    '''statement_ifthenelse : IF LPAREN expression RPAREN statement_compound
                            | IF LPAREN expression RPAREN statement_compound ELSE statement_compound'''
    if len(t) == 6:
        t[0] = AST.StatementIfthenelse(t[3], t[5], None, t.lexer.lineno)
    else:
        t[0] = AST.StatementIfthenelse(t[3], t[5], t[7], t.lexer.lineno)


def p_statement_call(t):
    '''statement_call : expression_call SEMICOL'''
    t[0] = t[1]


def p_statement_while(t):
    'statement_while :  WHILE LPAREN expression RPAREN statement_compound'
    t[0] = AST.StatementWhile(t[3], t[5], t.lexer.lineno)


# TODO for-loop
def p_statement_for(t):
    '''statement_for :  FOR LPAREN type IDENT ASSIGN expression SEMICOL expression SEMICOL IDENT ASSIGN expression RPAREN statement_compound'''
    t[0] = AST.StatementFor(t[3], t[4], t[5], t[7], t.lexer.lineno)


def p_statement_compound(t):
    'statement_compound : LCURL statement_list RCURL'
    t[0] = t[2]


def p_expression(t):
    '''expression : expression_integer
                | expression_identifier
                | expression_call
                | expression_binop
                | expression_group'''
    t[0] = t[1]


def p_expression_integer(t):
    'expression_integer : INT'
    t[0] = AST.ExpressionInteger(t[1], t.lexer.lineno)


def p_expression_identifier(t):
    'expression_identifier : IDENT'
    t[0] = AST.ExpressionIdentifier(t[1], t.lexer.lineno)


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
    t[0] = AST.ExpressionBinop(t[2], t[1], t[3], t.lexer.lineno)


def p_expression_group(t):
    'expression_group : LPAREN expression RPAREN'
    t[0] = t[2]


def p_expression_call(t):
    'expression_call : IDENT LPAREN optional_expression_list RPAREN'
    t[0] = AST.ExpressionCall(t[1], t[3], t.lexer.lineno)


def p_optional_expression_list(t):
    '''optional_expression_list : empty
                                | expression_list'''
    t[0] = t[1]


def p_expression_list(t):
    '''expression_list : expression
                       | expression COMMA expression_list'''
    if len(t) == 2:
        t[0] = AST.ExpressionList(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.ExpressionList(t[1], t[3], t.lexer.lineno)


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
    sys.exit(1)


# Build the lexer
lexer = lex.lex()

# Build the parser
parser = yacc.yacc()
