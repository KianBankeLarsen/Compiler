from __future__ import annotations

from dataclasses import dataclass


class AstNode:
    pass


@dataclass
class Body(AstNode):
    decls: DeclarationList
    stm_list: StatementList
    lineno: int


@dataclass
class DeclarationList:
    decl: Declaration
    next: DeclarationList
    lineno: int


@dataclass
class Declaration(AstNode):
    type: str
    decl: Symbol
    lineno: int


class Symbol(AstNode):
    pass


@dataclass
class VariableList(Symbol):
    name: str
    next: VariableList
    lineno: int


@dataclass
class Function(Symbol):
    name: ExpressionIdentifier
    par_list: ParameterList
    body: Body
    lineno: int


@dataclass
class Parameter(Symbol):
    type: str
    name: str
    lineno: int


@dataclass
class ParameterList(AstNode):
    param: Parameter
    next: ParameterList
    lineno: int


@dataclass
class StatementList(AstNode):
    stm: Statement
    next: StatementList
    lineno: int


class Statement(AstNode):
    pass


@dataclass
class StatementAssignment(Statement):
    lhs: ExpressionIdentifier
    rhs: Expression
    lineno: int


@dataclass
class StatementIfthenelse(Statement):
    exp: Expression
    then_part: StatementList
    else_part: StatementList
    lineno: int


@dataclass
class StatementWhile(Statement):
    exp: Expression
    while_part: StatementList
    lineno: int


# TODO for-loop
@dataclass
class StatementFor(Statement):
    assign: StatementAssignment
    exp: Expression
    assign2: StatementAssignment
    do: StatementList
    lineno: int


@dataclass
class StatementPrint(Statement):
    exp: Expression
    lineno: int


@dataclass
class StatementReturn(Statement):
    exp: Expression
    lineno: int


class Expression(AstNode):
    pass


@dataclass
class ExpressionIdentifier(Expression):
    identifier: str
    lineno: int


@dataclass
class ExpressionInteger(Expression):
    integer: int
    lineno: int


@dataclass
class ExpressionBinop(Expression):
    op: str
    lhs: Expression
    rhs: Expression
    lineno: int


@dataclass
class ExpressionCall(Expression):
    name: ExpressionIdentifier
    exp_list: ExpressionList
    lineno: int


@dataclass
class ExpressionList:
    exp: Expression
    next: ExpressionList
    lineno: int
