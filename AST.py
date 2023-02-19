from __future__ import annotations

from dataclasses import dataclass

import ply.lex as lex


class AstNode:
    pass


@dataclass
class StatementList(AstNode):
    stm: StatementList
    next: StatementList
    lineno: lex.LexToken


@dataclass
class Body(AstNode):
    variables_decl: object
    functions_decl: object
    stm_list: StatementList
    lineno: lex.LexToken


@dataclass
class Function(AstNode):
    name: ExpressionIdentifier
    par_list: object
    body: Body
    lineno: lex.LexToken


@dataclass
class StatementAssignment(AstNode):
    lhs: ExpressionIdentifier
    rhs: Expression
    lineno: lex.LexToken


class Expression(AstNode):
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
