from __future__ import annotations

import dataclass.AST as AST
from dataclass.symbol import Symbol, SymbolTable
from enums.symbols_enum import NameCategory


class ASTSymbolIncorporator:
    """Functionality to incoporate symbol table into
        the abstract syntax tree.

    The API exposes build_symbol_table, which takes 
        an AST as parameter.
    """

    def __init__(self) -> ASTSymbolIncorporator:
        self._current_scope = SymbolTable(None)
        self.variable_offset = None
        self.parameter_offset = None

    def _reduce_variable_list(self, var_lst: AST.DeclarationVariableList, acc: list = None) -> list(str):
        if acc is None:
            acc = []

        if var_lst is None:
            return acc

        return self._reduce_variable_list(
            var_lst.next, acc + [var_lst.name]
        )

    def build_symbol_table(self, ast_node: AST.AstNode) -> None:
        """Incorporate symbol table into the provided AST.
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
                symval = Symbol(type, NameCategory.FUNCTION, func)
                self._current_scope.insert(func.name, symval, lineno)
                self._current_scope = SymbolTable(self._current_scope)
                self.build_symbol_table(func)
            case AST.DeclarationVariableList(type, var_lst, lineno):
                for i in self._reduce_variable_list(var_lst):
                    symval = Symbol(type, NameCategory.VARIABLE,
                                    self.variable_offset)
                    self._current_scope.insert(i, symval, lineno)
                    self.variable_offset += 1
            case AST.DeclarationVariableInit(type, name, _, lineno):
                symval = Symbol(type, NameCategory.VARIABLE,
                                self.variable_offset)
                self._current_scope.insert(name, symval, lineno)
                self.variable_offset += 1
            case AST.Function(name, par_list, body):
                ast_node.symbol_table = self._current_scope
                self.parameter_offset = 0
                self.build_symbol_table(par_list)
                ast_node.number_of_parameters = self.parameter_offset
                self.build_symbol_table(body)
                self._current_scope = self._current_scope.parent
            case AST.Parameter(type, name, lineno):
                symval = Symbol(type, NameCategory.PARAMETER,
                                self.parameter_offset)
                self._current_scope.insert(name, symval, lineno)
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
            case AST.StatementFor(iter, _, _, body, lineno):
                self._current_scope = SymbolTable(self._current_scope)
                ast_node.symbol_table = self._current_scope
                ast_node.number_of_parameters = 1
                symval = Symbol(iter.type, NameCategory.PARAMETER, 0)
                self._current_scope.insert(iter.name, symval, lineno)
                self.build_symbol_table(body)
                self._current_scope = self._current_scope.parent
