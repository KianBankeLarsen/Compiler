from __future__ import annotations

from dataclasses import dataclass

from enums.code_gen_enum import *


@dataclass
class Arg:
    target: Target
    addressing: Mode


@dataclass
class Target:
    spec: T
    val: str = None


@dataclass
class Mode:
    mode: M
    offset: int = None


@dataclass(init=False)
class Ins:
    """Linear IR ILOC instruction scheme
    """

    opcode: Op
    args: list(Arg)

    def __init__(self, *args) -> Ins:
        self.opcode = args[0]
        self.args = args[1:]
