from __future__ import annotations

from enum import Enum, auto

import AST


class NameCategory(Enum):
    """
    """

    VARIABLE = auto()
    PARAMETER = auto()
    FUNCTION = auto()


class Symbol():
    """
    """

    def __init__(self, cat: NameCategory, info: int) -> Symbol:
        self.cat = cat
        self.info = info


class SymbolTable:
    """
    """

    def __init__(self, parent: SymbolTable) -> SymbolTable:
        self._tab = {}
        self.level = 0 if parent else parent.level + 1
        self.parent = parent

    def insert(self, signature: tuple or str, value: Symbol):
        self._tab[signature] = value

    def lookup(self, signature: tuple or str) -> Symbol:
        if self.parent:
            return self._tab.get(
                signature, self.lookup(self.parent.lookup(signature))
            )
        return self.lookup_this_scope(signature)

    def lookup_this_scope(self, signature: tuple or str) -> Symbol:
        return self._tab.get(signature, None)


class ASTSymbolIncorporator:
    """
    """
    
    def __init__(self) -> ASTSymbolIncorporator:
        self._current_scope = None
        self._variable_offset = None
        self._current_level = -1

    def incorporate_symbol_table(self, ast_node: AST.AstNode) -> None:
        """
        """
        
        match ast_node:
            case _:
                pass
