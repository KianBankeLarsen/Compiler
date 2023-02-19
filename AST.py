from __future__ import annotations

from dataclasses import dataclass

import ply.lex as lex


@dataclass
class StatementList:
    stm: StatementList
    next: StatementList
    lineno: object


@dataclass
class Body:
    variables_decl: object
    functions_decl: object
    stm_list: StatementList
    lineno: object


@dataclass
class Function:
    name: ExpressionIdentifier
    par_list: object
    body: Body
    lineno: lex.LexToken


@dataclass
class StatementAssignment:
    lhs: ExpressionIdentifier
    rhs: Expression
    lineno: lex.LexToken


class Expression:
    pass


@dataclass
class ExpressionIdentifier(Expression):
    identifier: lex.LexToken
    lineno: lex.LexToken


@dataclass
class ExpressionInteger(Expression):
    integer: lex.LexToken
    lineno: lex.LexToken


@dataclass
class ExpressionBinop(Expression):
    op: lex.LexToken
    lhs: Expression
    rhs: Expression
    lineno: lex.LexToken
