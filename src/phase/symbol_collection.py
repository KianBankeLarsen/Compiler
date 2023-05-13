from __future__ import annotations

import copy

import src.dataclass.AST as AST
from src.dataclass.symbol import Symbol, SymbolTable
from src.enums.symbols_enum import NameCategory


class ASTSymbolIncorporator:
    """Functionality to incoporate symbol table into
        the abstract syntax tree.

    The API exposes build_symbol_table, which takes 
        an AST as parameter.
    """

    def __init__(self) -> ASTSymbolIncorporator:
        self._current_scope = SymbolTable(None)
        self._body_scope = []
        self.parameter_offset = None

    def _reduce_variable_list(self, var_lst: AST.DeclarationVariableList, acc: list = None) -> list(str):
        if acc is None:
            acc = []

        if var_lst is None:
            return acc

        return self._reduce_variable_list(
            var_lst.next, acc + [var_lst.name]
        )

    def build_symbol_table(self, ast_node: AST.AstNode) -> AST.AstNode:
        """Incorporate symbol table into the provided AST.
        """

        ast_node = copy.deepcopy(ast_node)
        self._build_symbol_table(ast_node)
        return ast_node

    def _build_symbol_table(self, ast_node: AST.AstNode) -> None:
        match ast_node:
            case AST.Body(decls, stm_list):
                ast_node.variable_offset = 0
                self._body_scope.append(ast_node)
                self._build_symbol_table(decls)
                ast_node.number_of_variables = ast_node.variable_offset
                self._body_scope.pop()
                self._build_symbol_table(stm_list)
            case AST.DeclarationList(decl, next):
                self._build_symbol_table(decl)
                self._build_symbol_table(next)
            case AST.DeclarationFunction(type, func, lineno):
                symval = Symbol(type, NameCategory.FUNCTION, func)
                self._current_scope.insert(func.name, symval, lineno)
                self._current_scope = SymbolTable(self._current_scope)
                self._build_symbol_table(func)
            case AST.DeclarationVariableList(type, var_lst, lineno):
                for i in self._reduce_variable_list(var_lst):
                    symval = Symbol(type, NameCategory.VARIABLE,
                                    self._body_scope[-1].variable_offset)
                    self._current_scope.insert(i, symval, lineno)
                    self._body_scope[-1].variable_offset += 1
            case AST.DeclarationVariableInit(type, name, _, lineno):
                symval = Symbol(type, NameCategory.VARIABLE,
                                self._body_scope[-1].variable_offset)
                self._current_scope.insert(name, symval, lineno)
                self._body_scope[-1].variable_offset += 1
            case AST.Function(_, par_list, body):
                ast_node.symbol_table = self._current_scope
                self.parameter_offset = 0
                self._build_symbol_table(par_list)
                ast_node.number_of_parameters = self.parameter_offset
                self._build_symbol_table(body)
                self._current_scope = self._current_scope.parent
            case AST.Parameter(type, name, lineno):
                symval = Symbol(type, NameCategory.PARAMETER,
                                self.parameter_offset)
                self._current_scope.insert(name, symval, lineno)
                self.parameter_offset += 1
            case AST.ParameterList(param, next):
                self._build_symbol_table(param)
                self._build_symbol_table(next)
            case AST.StatementList(stm, next):
                self._build_symbol_table(stm)
                self._build_symbol_table(next)
            case AST.StatementAssignment(lhs):
                symbol, level = self._current_scope.lookup(lhs)
                level_difference = self._current_scope.level - level
                if level_difference:
                    symbol.escaping = True
            case AST.ExpressionIdentifier(ident):
                symbol, level = self._current_scope.lookup(ident)
                level_difference = self._current_scope.level - level
                if level_difference:
                    symbol.escaping = True
            case AST.StatementIfthenelse(exp, then_part, else_part):
                self._build_symbol_table(exp)
                self._current_scope = SymbolTable(self._current_scope)
                ast_node.symbol_table_then = self._current_scope
                self._build_symbol_table(then_part)
                self._current_scope = self._current_scope.parent
                if else_part:
                    self._current_scope = SymbolTable(self._current_scope)
                    ast_node.symbol_table_else = self._current_scope
                    self._build_symbol_table(else_part)
                    self._current_scope = self._current_scope.parent
            case AST.StatementWhile(exp, body):
                self._build_symbol_table(exp)
                self._current_scope = SymbolTable(self._current_scope)
                ast_node.symbol_table = self._current_scope
                self._build_symbol_table(body)
                self._current_scope = self._current_scope.parent
            case AST.StatementFor(iter, _, _, body, lineno):
                self._build_symbol_table(iter.exp)
                self._current_scope = SymbolTable(self._current_scope)
                ast_node.symbol_table = self._current_scope
                ast_node.number_of_parameters = 1
                symval = Symbol(
                    iter.type, NameCategory.PARAMETER, 0, escaping=True)
                self._current_scope.insert(iter.name, symval, lineno)
                self._build_symbol_table(body)
                self._current_scope = self._current_scope.parent
            case AST.StatementReturn(exp):
                self._build_symbol_table(exp)
            case AST.StatementPrint(exp):
                self._build_symbol_table(exp)
            case AST.ExpressionCall(exp_list=exp_list):
                self._build_symbol_table(exp_list)
            case AST.ExpressionList(exp, next):
                self._build_symbol_table(exp)
                self._build_symbol_table(next)
            case AST.ExpressionBinop(_, lhs, rhs):
                self._build_symbol_table(lhs)
                self._build_symbol_table(rhs)
            case AST.ExpressionInteger():
                pass
            case None:
                pass
            case _:
                raise ValueError(ast_node)
