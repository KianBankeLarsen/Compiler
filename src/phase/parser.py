import ply.yacc as yacc

import src.dataclass.AST as AST
import src.phase.lexer
import src.utils.error as error
import src.utils.interfacing_parser as interfacing_parser
from src.enums.code_generation_enum import Op

tokens = src.phase.lexer.tokens

precedence = (
    ('nonassoc', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'), # Requires syntaxtic sugar
    ('right', 'EQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE')
)


def p_program(t):
    'program : body'
    interfacing_parser.the_program = AST.Function(
        "?main", None, t[1], t.lexer.lineno)


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
    '''declaration : function_declaration
                    | variable_list_declaration
                    | variable_init_declaration'''
    t[0] = t[1]


def p_function_declaration(t):
    '''function_declaration : type function
                            | VOID_TYPE function'''
    t[0] = AST.DeclarationFunction(t[1], t[2], t.lexer.lineno)


def p_variable_list_declaration(t):
    '''variable_list_declaration : type variable_list SEMICOL'''
    t[0] = AST.DeclarationVariableList(t[1], t[2], t.lexer.lineno)


def p_variable_init_declaration(t):
    '''variable_init_declaration : type IDENT ASSIGN expression SEMICOL'''
    t[0] = AST.DeclarationVariableInit(t[1], t[2], t[4], t.lexer.lineno)


def p_variables_list(t):
    '''variable_list : IDENT
                      | IDENT COMMA variable_list'''
    if len(t) == 2:
        t[0] = AST.VariableList(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.VariableList(t[1], t[3], t.lexer.lineno)


def p_function(t):
    'function : IDENT LPAREN optional_parameter_list RPAREN new_scope'
    t[0] = AST.Function(t[1], t[3], t[5], t.lexer.lineno)


def p_new_scope(t):
    'new_scope : LCURL body RCURL'
    t[0] = t[2]


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
    'param : type IDENT'
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
    '''statement_ifthenelse : IF LPAREN expression RPAREN new_scope
                            | IF LPAREN expression RPAREN new_scope ELSE new_scope'''
    if len(t) == 6:
        t[0] = AST.StatementIfthenelse(t[3], t[5], None, t.lexer.lineno)
    else:
        t[0] = AST.StatementIfthenelse(t[3], t[5], t[7], t.lexer.lineno)


def p_statement_call(t):
    '''statement_call : expression_call SEMICOL'''
    t[0] = t[1]


def p_statement_while(t):
    'statement_while :  WHILE LPAREN expression RPAREN new_scope'
    t[0] = AST.StatementWhile(t[3], t[5], t.lexer.lineno)


def p_statement_for(t):
    'statement_for : FOR LPAREN variable_init_declaration expression SEMICOL statement_assignment_for RPAREN new_scope'
    t[0] = AST.StatementFor(t[3], t[4], t[6], t[8], t.lexer.lineno)


def p_statement_for_assign(t):
    'statement_assignment_for : IDENT ASSIGN expression'
    t[0] = AST.StatementAssignment(t[1], t[3], t.lexer.lineno)


def p_expression(t):
    '''expression : expression_integer
                | expression_float
                | expression_identifier
                | expression_call
                | expression_binop
                | expression_group'''
    t[0] = t[1]


def p_expression_integer(t):
    'expression_integer : INT'
    t[0] = AST.ExpressionInteger(t[1], t.lexer.lineno)


def p_expression_float(t):
    'expression_float : FLOAT'
    t[0] = AST.ExpressionFloat(t[1], t.lexer.lineno)


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
    # * Not recommended to use hidden methods because of backwards compatibility and semver,
    # *  but it is really usefull in this cases.
    t[0] = AST.ExpressionBinop(Op._value2member_map_[
                               t[2]], t[1], t[3], t.lexer.lineno)


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
    error.error_message(
        "Syntax Analysis",
        f"Problem detected{cause}.",
        location)


parser = yacc.yacc()
