from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NoReturn

import src.utils.error as error
from src.enums.symbols_enum import NameCategory


@dataclass
class Symbol:
    type: str
    kind: NameCategory
    info: int


@dataclass(init=False)
class SymbolTable:
    """Symbol table containing symbols.

    The API exposes functionality to lookup and insert symbols.
    """

    level: int
    parent: SymbolTable
    _tab: dict

    def __init__(self, parent: SymbolTable) -> SymbolTable:
        self._tab = {}
        self.level = parent.level + 1 if parent else 0
        self.parent = parent

    def __str__(self):
        return ", ".join(map(str, self._tab.keys()))

    def _error_message(self, name: str, lineno: int) -> NoReturn:
        error.error_message(
            "Symbol Collection",
            f"Redeclaration of function '{name}' in the same scope.",
            lineno)

    def insert(self, signature: Any, value: Symbol, lineno: int) -> None:
        """Insert symbol as key-value pair.
        """

        if self._tab.get(signature):
            self._error_message(signature, lineno)

        self._tab[signature] = value

    def lookup(self, signature: Any) -> tuple(Symbol, int):
        """Retrieves declared symbol from closest accessible lexical scope.

        Returns
        -------
        (Symbol, level) : tuple(Symbol, int)
            This method returns None if the symbol is not available,
            otherwise the located symbol.
        """

        if self.parent:
            symval = (
                self._tab.get(
                    signature,
                    self.parent.lookup(signature)
                ),
                self.level
            )
            
            if isinstance(symval[0], Symbol):
                return symval
            else:
                return symval[0]
            
        return (self._tab.get(signature), self.level)
