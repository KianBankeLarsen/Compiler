from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import AST
import error


class NameCategory(Enum):
    VARIABLE = auto()
    PARAMETER = auto()
    FUNCTION = auto()


@dataclass
class Symbol:
    type: str
    kind: NameCategory
    info: int


class SymbolTable:
    """
    """

    def __init__(self, parent: SymbolTable) -> SymbolTable:
        self._tab = {}
        self.level = parent.level + 1 if parent else 0
        self.parent = parent

    def __str__(self):
        return ", ".join(map(str, self._tab.keys()))

    def __repr__(self):
        return str(self)

    def insert(self, signature: tuple or str, value: Symbol):
        self._tab[signature] = value

    def lookup(self, signature: tuple or str) -> tuple(Symbol, int):
        if self.parent:
            return tuple(
                self._tab.get(
                    signature, self.lookup(self.parent.lookup(signature))
                ), self.level)
        return self.lookup_this_scope(signature)

    def lookup_this_scope(self, signature: tuple or str) -> tuple(Symbol, int):
        return (self._tab.get(signature, None), self.level)


class ASTSymbolIncorporator:
    """
    """

    def __init__(self) -> ASTSymbolIncorporator:
        self._current_scope = SymbolTable(None)
        self.variable_offset = None
        self.parameter_offset = None

    def _reduce_variable_list(self, var_lst, acc=None):
        if acc is None:
            acc = []
        acc.append(var_lst.name)
        if var_lst.next:
            self._reduce_variable_list(var_lst.next, acc)
        return acc

    def _error_message(self, name: str, lineno: int) -> None:
        error.error_message(
            "Symbol Collection",
            f"Redeclaration of function '{name}' in the same scope.",
            lineno)

    def build_symbol_table(self, ast_node: AST.AstNode) -> None:
        """
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                self.variable_offset = 0
                self.build_symbol_table(decls)
                ast_node.number_of_variables = self.variable_offset
                self.build_symbol_table(stm_list)
            case AST.DeclarationList(decl, next):
                self.build_symbol_table(decl)
                self.build_symbol_table(next)
            case AST.DeclarationFunction(type, func, lineno):
                if self._current_scope.lookup_this_scope(func.name)[0]:
                    self._error_message(func.name, lineno)
                symval = Symbol(type, NameCategory.FUNCTION, func)
                self._current_scope.insert(func.name, symval)
                self._current_scope = SymbolTable(self._current_scope)
                self.build_symbol_table(func)
            case AST.DeclarationVariableList(type, var_lst, lineno):
                for i in self._reduce_variable_list(var_lst):
                    if self._current_scope.lookup_this_scope(i)[0]:
                        self._error_message(i, lineno)
                    symval = Symbol(type, NameCategory.VARIABLE,
                                    self.variable_offset)
                    self._current_scope.insert(i, symval)
                    self.variable_offset += 1
            case AST.DeclarationVariableInit(type, name, _, lineno):
                if self._current_scope.lookup_this_scope(name)[0]:
                    self._error_message(name, lineno)
                symval = Symbol(type, NameCategory.VARIABLE,
                                self.variable_offset)
                self._current_scope.insert(name, symval)
                self.variable_offset += 1
            case AST.Function(name, par_list, body):
                ast_node.symbol_table = self._current_scope
                self.parameter_offset = 0
                self.build_symbol_table(par_list)
                ast_node.number_of_parameters = self.parameter_offset
                self.build_symbol_table(body)
                self._current_scope = self._current_scope.parent
            case AST.Parameter(type, name, lineno):
                if self._current_scope.lookup_this_scope(name)[0]:
                    self._error_message(name, lineno)
                symval = Symbol(type, NameCategory.PARAMETER,
                                self.parameter_offset)
                self._current_scope.insert(name, symval)
                self.parameter_offset += 1
            case AST.ParameterList(param, next):
                self.build_symbol_table(param)
                self.build_symbol_table(next)
            case AST.StatementList(stm, next):
                self.build_symbol_table(stm)
                self.build_symbol_table(next)
            case AST.StatementIfthenelse(_, then_part, else_part):
                self._current_scope = SymbolTable(self._current_scope)
                ast_node.symbol_table_then = self._current_scope
                self.build_symbol_table(then_part)
                self._current_scope = self._current_scope.parent
                if else_part:
                    self._current_scope = SymbolTable(self._current_scope)
                    ast_node.symbol_table_else = self._current_scope
                    self.build_symbol_table(else_part)
                    self._current_scope = self._current_scope.parent
            case AST.StatementWhile(_, body):
                self._current_scope = SymbolTable(self._current_scope)
                ast_node.symbol_table = self._current_scope
                self.build_symbol_table(body)
                self._current_scope = self._current_scope.parent
            case AST.StatementFor(iter, _, _, body):
                self._current_scope = SymbolTable(self._current_scope)
                ast_node.symbol_table = self._current_scope
                self.build_symbol_table(body)
                self.build_symbol_table(iter)
                self._current_scope = self._current_scope.parent
