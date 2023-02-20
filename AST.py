from __future__ import annotations

from dataclasses import dataclass

import ply.lex as lex


class AstNode:
    pass


@dataclass
class StatementList(AstNode):
    stm: StatementList
    next: StatementList
    lineno: int


@dataclass
class Body(AstNode):
    variables_decl: object
    functions_decl: object
    stm_list: StatementList
    lineno: int


@dataclass
class Function(AstNode):
    name: ExpressionIdentifier
    par_list: object
    body: Body
    lineno: int


@dataclass
class StatementAssignment(AstNode):
    lhs: ExpressionIdentifier
    rhs: Expression
    lineno: int


@dataclass
class StatementIfthenelse:
    exp: Expression
    then_part: StatementList
    else_part: StatementList
    lineno: int


@dataclass
class StatementWhile:
    exp: Expression
    while_part: StatementList
    lineno: int


# @dataclass
# class StatementFor:
#     assign: StatementAssignment
#     exp: Expression
#     do: StatementList


@dataclass
class StatementPrint:
    exp: Expression
    lineno: int


@dataclass
class StatementReturn:
    exp: Expression
    lineno: int


class Expression(AstNode):
    pass


@dataclass
class ExpressionIdentifier(Expression):
    identifier: lex.LexToken
    lineno: int


@dataclass
class ExpressionInteger(Expression):
    integer: lex.LexToken
    lineno: int


@dataclass
class ExpressionBinop(Expression):
    op: lex.LexToken
    lhs: Expression
    rhs: Expression
    lineno: int
