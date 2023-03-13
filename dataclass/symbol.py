from __future__ import annotations

from dataclasses import dataclass

from enums.symbols_enum import NameCategory


@dataclass
class Symbol:
    type: str
    kind: NameCategory
    info: int


@dataclass(init=False)
class SymbolTable:
    """
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

    def insert(self, signature: tuple or str, value: Symbol):
        self._tab[signature] = value

    def lookup(self, signature: tuple or str) -> tuple(Symbol, int):
        if self.parent:
            return (
                self._tab.get(
                    signature,
                    self.lookup(self.parent.lookup(signature))
                ),
                self.level
            )
        return self.lookup_this_scope(signature)

    def lookup_this_scope(self, signature: tuple or str) -> tuple(Symbol, int):
        return (self._tab.get(signature, None), self.level)