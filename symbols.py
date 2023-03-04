from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import AST


class NameCategory(Enum):
    VARIABLE = auto()
    PARAMETER = auto()
    FUNCTION = auto()


@dataclass
class Symbol:
    type: object
    kind: NameCategory
    info: int


class SymbolTable:
    """
    """

    def __init__(self, parent: SymbolTable) -> SymbolTable:
        self._tab = {}
        self.level = parent.level + 1 if parent else 0
        self.parent = parent

    def insert(self, signature: tuple or str, value: Symbol):
        self._tab[signature] = value

    def lookup(self, signature: tuple or str) -> tuple(Symbol, int):
        if self.parent:
            return tuple(self._tab.get(
                signature, self.lookup(self.parent.lookup(signature))
            ), self.level)
        return self.lookup_this_scope(signature)

    def lookup_this_scope(self, signature: tuple or str) -> tuple(Symbol, int):
        return tuple(self._tab.get(signature, None), self.level)


class ASTSymbolIncorporator:
    """
    """

    def __init__(self) -> ASTSymbolIncorporator:
        self._current_scope = SymbolTable(None)
        self._current_level = -1
        self.variable_offset = None
        self.parameter_offset = None

    def build_symbol_table(self, ast_node: AST.AstNode) -> None:
        """
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                self.build_symbol_table(decls)
                self.build_symbol_table(stm_list)
            case AST.DeclarationList(decl, next):
                self.build_symbol_table(decl)
                if next:
                    self.build_symbol_table(next)
            case AST.DeclarationFunction(type, func):
                self.build_symbol_table(func)
            case AST.DeclarationVariableList(type, var_lst):
                self.build_symbol_table(var_lst)
            case AST.DeclarationVariableInit(type, name, _):
                pass
            case AST.VariableList(name, next):
                if next:
                    self.build_symbol_table(next)
            case AST.Function(name, par_list, body):
                if par_list:
                    self.build_symbol_table(par_list)
                self.build_symbol_table(body)
            case AST.Parameter(type, name):
                pass
            case AST.ParameterList(param, next):
                self.build_symbol_table(param)
                if next:
                    self.build_symbol_table(next)
            case AST.StatementList(stm, next):
                self.build_symbol_table(stm)
                if next:
                    self.build_symbol_table(stm)
            case AST.StatementIfthenelse(_, then_part, else_part):
                self.build_symbol_table(then_part)
                if else_part:
                    self.build_symbol_table(else_part)
            case AST.StatementWhile(_, body):
                self.build_symbol_table(body)
            case AST.StatementFor(iter, _, _, body):
                self.build_symbol_table(iter)
                self.build_symbol_table(body)
