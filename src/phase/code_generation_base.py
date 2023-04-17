from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import src.dataclass.AST as AST
import src.dataclass.symbol as dataclass_symbol
import src.utils.label_generator as label
from src.dataclass.iloc import Instruction, Mode, Operand, Target
from src.enums.code_generation_enum import M, Meta, Op, T


@dataclass
class GenerateCodeBase(ABC):
    """Abstract code generation base

    ---------------------- <-- RSP
    | Temporary saves    |
    |--------------------|
    | Local data area    | 
    |--------------------| <-- Callee RBP
    | Callee-save area   |
    |--------------------|
    | Return address     |
    |--------------------|
    | Callers ARP        |
    |--------------------|
    | Caller-save area   |
    |--------------------|
    | Parameter area     |
    ----------------------
    """

    _current_scope: dataclass_symbol.SymbolTable = None
    _function_stack: list(AST.AstNode) = field(default_factory=list)
    _body_stack: list(AST.AstNode) = field(default_factory=list)
    _labels: label.Labels = label.Labels()

    @abstractmethod
    def _append_instruction(self, instruction: Instruction) -> None:
        pass

    @abstractmethod
    def _get_code_block_to_extend(self) -> list[Instruction]:
        pass

    @abstractmethod
    def _generate_code(self, ast_node: AST.AstNode) -> None:
        pass

    def _follow_static_link(self, symbol_level: int) -> None:
        level_difference = self._current_scope.level - symbol_level

        self._append_instruction(
            Instruction(Op.MOVE,
                        Operand(Target(T.RBP), Mode(M.DIR)),
                        Operand(Target(T.RSL), Mode(M.DIR)))
        )
        self._get_code_block_to_extend().extend(
            [Instruction(Op.MOVE,
                         Operand(Target(T.RSL), Mode(M.IRL, -7)),
                         Operand(Target(T.RSL), Mode(M.DIR)))
             for _ in range(level_difference)]
        )

    def _ensure_labels(self, ast_node: AST.AstNode) -> None:
        if ast_node.name == "?main":
            ast_node.start_label = "main"
            ast_node.end_label = "end_main"

        if not hasattr(ast_node, 'start_label'):
            ast_node.start_label = self._labels.next(ast_node.name)
            ast_node.end_label = self._labels.next(f"end_{ast_node.name}")

    def _prolog(self, body: AST.Body) -> None:
        self._append_instruction(
            Instruction(Op.META, Meta.PROLOG)
        )
        # Allocate stack space
        self._append_instruction(
            Instruction(Op.SUB,
                        Operand(
                            Target(T.IMI, 8*body.number_of_variables), Mode(M.DIR)),
                        Operand(Target(T.RSP), Mode(M.DIR)))
        )

    def _epilog(self) -> None:
        # Local stack variables are deallocated in epilog
        self._append_instruction(
            Instruction(Op.META, Meta.EPILOG)
        )

    def _precall(self, exp_list: AST.ExpressionList, symbol_level: int) -> None:
        # Push arguments
        self._generate_code(exp_list)

        # Begin call
        self._append_instruction(
            Instruction(Op.META, Meta.PRECALL)
        )

        # Push parents ARP
        self._follow_static_link(symbol_level)

        self._append_instruction(
            Instruction(Op.PUSH,
                        Operand(Target(T.RSL), Mode(M.DIR)))
        )

    def _postreturn(self, number_of_parameters: int) -> None:
        # Remove ARP
        self._append_instruction(
            Instruction(Op.ADD,
                        Operand(Target(T.IMI, 8), Mode(M.DIR)),
                        Operand(Target(T.RSP), Mode(M.DIR)))
        )

        # End call
        self._append_instruction(
            Instruction(Op.META, Meta.POSTRETURN)
        )

        # Remove arguments
        self._append_instruction(
            Instruction(Op.ADD,
                        Operand(Target(T.IMI, 8*number_of_parameters),
                                Mode(M.DIR)),
                        Operand(Target(T.RSP), Mode(M.DIR)))
        )

    def _push_pseudo_return_address(self) -> None:
        self._append_instruction(
            Instruction(Op.SUB,
                        Operand(Target(T.IMI, 8), Mode(M.DIR)),
                        Operand(Target(T.RSP), Mode(M.DIR)))
        )

    def _pop_pseudo_return_address(self) -> None:
        self._append_instruction(
            Instruction(Op.ADD,
                        Operand(Target(T.IMI, 8), Mode(M.DIR)),
                        Operand(Target(T.RSP), Mode(M.DIR)))
        )

    def generate_code(self, ast_node: AST.AstNode) -> AST.AstNode:
        """Generate linear ILOC IR code.
        """

        ast_node = copy.deepcopy(ast_node)
        self._generate_code(ast_node)
        return ast_node
