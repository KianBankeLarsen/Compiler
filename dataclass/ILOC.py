from __future__ import annotations

from dataclasses import dataclass

from enums.code_generation_enum import M, Op, T


@dataclass
class Operand:
    """Single operand layout
    """

    target: Target
    addressing: Mode


@dataclass
class Target:
    """Targeted register class
    """

    spec: T
    val: str = None


@dataclass
class Mode:
    """Addressing mode, i.e, direct and indirect relative
    """

    mode: M
    offset: int = None


@dataclass(init=False)
class Instruction:
    """Linear IR ILOC instruction scheme

    Two-address opcode example
    ------------------------------
    | Opcode | Operand | Operand |
    ------------------------------
    """

    opcode: Op
    args: list(Operand)

    def __init__(self, *args) -> Instruction:
        self.opcode = args[0]
        self.args = args[1:]
