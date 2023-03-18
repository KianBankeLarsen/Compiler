from __future__ import annotations

import copy
from dataclasses import dataclass, field

import dataclass.AST as AST
import dataclass.symbol as symbol
import utils.error
import utils.label_generator as label
from dataclass.iloc import Instruction, Mode, Operand, Target
from enums.code_generation_enum import M, Meta, Op, T
from enums.symbols_enum import NameCategory


@dataclass
class GenerateCode:
    """Orchestrating code generation. 
    The API exposes `generate_code` and `get_code`.
    """

    _current_scope: symbol.SymbolTable = None
    _code: list(Instruction) = field(default_factory=list)
    _function_stack: list(AST.AstNode) = field(default_factory=list)
    _labels: label.Labels = label.Labels()

    def _append_instruction(self, instruction: Instruction) -> None:
        self._code.append(instruction)

    def _follow_static_link(self, level_difference: int) -> None:
        self._append_instruction(
            Instruction(Op.MOVE,
                        Operand(Target(T.RBP), Mode(M.DIR)),
                        Operand(Target(T.RSL), Mode(M.DIR)))
        )
        self._code.extend(
            [Instruction(Op.MOVE,
                         Operand(Target(T.RSL), Mode(M.IRL, -2)),
                         Operand(Target(T.RSL), Mode(M.DIR)))
             for _ in range(level_difference)]
        )

    def get_code(self) -> list(Instruction):
        """Get copy of linear ILOC IR code.
        """

        return copy.deepcopy(self._code)

    def generate_code(self, ast_node: AST.AstNode) -> None:
        """Generate linear ILOC IR code.
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                self.generate_code(decls)
                self.generate_code(stm_list)
            case AST.DeclarationList(decl, next):
                self.generate_code(decl)
                self.generate_code(next)
            case AST.DeclarationVariableInit(_, name, exp, lineno):
                self.generate_code(AST.StatementAssignment(name, exp, lineno))
            case AST.Function(name, par_list, body):
                self.generate_code(par_list)
                self.generate_code(body)
            case AST.StatementList(stm, next):
                self.generate_code(stm)
                self.generate_code(next)
            case AST.StatementAssignment(lhs, rhs):
                self.generate_code(lhs)
                self.generate_code(rhs)
                # TODO Write some code
            case AST.StatementIfthenelse(exp, then_part, else_part):
                """     pop reg1
                        move 0, reg 2
                        cmp reg1, reg2
                        je else_label
                        *then_part*
                        jmp esle_label
                    else_label:
                        *Possibly else_part*
                    esle_label:
                """
                ast_node.else_label = self._labels.next("else")
                ast_node.esle_label = self._labels.next("esle")

                self._append_instruction(
                    Instruction(Op.POP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.MOVE,
                                Operand(Target(T.IMI, 0), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.CMP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.JE,
                                Operand(Target(T.MEM, ast_node.else_label), Mode(M.DIR)))
                )

                self.generate_code(then_part)

                self._append_instruction(
                    Instruction(Op.JMP, Operand(
                        Target(T.MEM, ast_node.esle_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.else_label), Mode(M.DIR)))
                )

                self.generate_code(else_part)

                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.esle_label), Mode(M.DIR)))
                )
            case AST.StatementWhile(exp, body):
                """ while_label:
                        pop reg1
                        move 0, reg2
                        cmp reg1, reg2
                        je elihw_label  
                        *body*
                        jmp while_label
                    elihw_label:
                """
                ast_node.while_label = self._labels.next("while")
                ast_node.elihw_label = self._labels.next("elihw")

                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.while_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.POP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)))
                )

                self.generate_code(exp)

                self._append_instruction(
                    Instruction(Op.MOVE,
                                Operand(Target(T.IMI, 0), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.CMP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.JE,
                                Operand(Target(T.MEM, ast_node.elihw_label), Mode(M.DIR)))
                )

                self.generate_code(body)

                self._append_instruction(
                    Instruction(Op.JMP,
                                Operand(Target(T.MEM, ast_node.while_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.elihw_label), Mode(M.DIR)))
                )
            case AST.StatementFor(iter, exp, assign, body):
                """ for_label: 
                        pop reg1
                        move 0, reg2
                        cmp reg1, reg2
                        je rof_label
                        *body*
                        *assign*
                        jmp for_label
                    rof_label:
                """

                ast_node.for_label = self._labels("for")
                ast_node.rof_label = self._labels("rof")

                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.for_label), Mode(M.DIR)))
                )

                self.generate_code(AST.StatementAssignment(
                    iter.name, iter.exp, iter.lineno))
                self.generate_code(exp)

                self._append_instruction(
                    Instruction(Op.POP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.MOVE,
                                Operand(Target(T.IMI, 0), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.CMP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(Op.JE,
                                         Operand(Target(T.MEM, ast_node.rof_label), Mode(M.DIR)))

                self.generate_code(body)
                self.generate_code(assign)

                self._append_instruction(
                    Instruction(Op.JMP,
                                Operand(Target(T.MEM, ast_node.for_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.rof_label), Mode(M.DIR)))
                )
            case AST.StatementPrint(exp):
                self.generate_code(exp)
                self._append_instruction(
                    Instruction(Op.META, Meta.CALLER_SAVE)
                )
                self._append_instruction(
                    Instruction(Op.META, Meta.CALLER_PROLOGUE)
                )
                self._append_instruction(
                    Instruction(Op.META, Meta.CALL_PRINTF)
                )
                self._append_instruction(
                    Instruction(Op.META, Meta.CALLER_EPILOGUE)
                )
                self._append_instruction(
                    Instruction(Op.META, Meta.CALLER_RESTORE)
                )
            case AST.StatementReturn(exp):
                pass
            case AST.ExpressionIdentifier(identifier):
                """ move rbp, rsl
                    move -2(rsl), rsl - dereference zero or more times
                    push rsl_offset
                """
                symbol, symbol_level = self._current_scope.lookup(identifier)
                current_level = self._current_scope.level
                level_difference = current_level - symbol_level
                self._follow_static_link(level_difference)

                match symbol:
                    case symbol.Symbol(_, kind=NameCategory.PARAMETER, info=info):
                        self._append_instruction(
                            Instruction(Op.PUSH,
                                        Operand(Target(T.RSL), Mode(M.IRL, -(info + 3))))
                        )
                    case symbol.Symbol(_, kind=NameCategory.VARIABLE, info=info):
                        self._append_instruction(
                            Instruction(Op.PUSH,
                                        Operand(Target(T.RSL), Mode(M.IRL, info + 1)))
                        )
                    case _:
                        raise ValueError(
                            f"Symbol kind, {symbol.kind}, is unknown.")
            case AST.ExpressionInteger(integer):
                """ push integer
                """
                self._append_instruction(
                    Instruction(Op.PUSH,
                                Operand(Target(T.IMI, integer), Mode(M.DIR)))
                )
            case AST.ExpressionFloat(_, lineno):
                utils.error("code Generation",
                            "Floats are not implemented, yet.",
                            lineno)
            case AST.ExpressionBinop(binop, lhs, rhs) if binop in [Op.ADD, Op.SUB, Op.DIV, Op.MUL]:
                """ pop reg1
                    pop reg2
                    op reg1, reg2
                    push reg2
                """
                self.generate_code(lhs)
                self.generate_code(rhs)

                self._append_instruction(
                    Instruction(Op.POP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.POP,
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(binop,
                                Operand(Target(T.REG, 1), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.PUSH,
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
            case AST.ExpressionBinop(binop_cmp, lhs, rhs) if binop_cmp in [Op.JE, Op.JNE, Op.JL, Op.JG, Op.JGE]:
                """     pop reg2
                        pop reg1
                        cmp reg2, reg1
                        cond_jump true_label
                        push false
                        jmp end_label
                    true_label:
                        push true
                    end_label:
                """
                self.generate_code(lhs)
                self.generate_code(rhs)

                true_label = self._labels.next("cmp_true")
                end_label = self._labels.next("cmp_end")

                self._append_instruction(
                    Instruction(Op.POP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.POP,
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.CMP,
                                Operand(Target(T.REG, 1), Mode(M.DIR)),
                                Operand(Target(T.REG, 2), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(binop_cmp,
                                Operand(Target(T.MEM, true_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.PUSH,
                                Operand(Target(T.IMI, 0), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.JMP,
                                Operand(Target(T.MEM, end_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, true_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.PUSH,
                                Operand(Target(T.IMI, 1), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, end_label), Mode(M.DIR)))
                )
            case AST.ExpressionCall(name, exp_list):
                self.generate_code(exp_list)
            case AST.ExpressionList(exp, next):
                self.generate_code(exp)
                self.generate_code(next)
