from __future__ import annotations

import dataclass.AST as AST
import dataclass.symbol as symbol
import utils.label_generator as label
from dataclass.iloc import Instruction, Mode, Operand, Target
from enums.code_generation_enum import M, Op, T, Meta
import utils.error

arithmic_op = [Op.ADD, Op.SUB, Op.DIV, Op.MUL]
comparison_op = [Op.JE, Op.JNE, Op.JL, Op.JG, Op.JGE]


class GenerateCode:
    """
    """

    def __init__(self) -> GenerateCode:
        self._current_scope: symbol.SymbolTable = None
        self._code: list(Instruction) = []
        self._labels: label.Labels = label.Labels()

    def _append_instruction(self, instruction: Instruction) -> None:
        self._code.append(instruction)

    def get_code(self) -> list(Instruction):
        """Get linear ILOC IR code.
        """

        return self._code

    def generate_code(self, ast_node: AST.AstNode) -> None:
        """Generate linear ILOC IR code.
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                self.generate_code(stm_list)
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
                        jmp while_label
                    elihw_label:
                """
                ast_node.while_label = self._labels.next("while")
                ast_node.elihw_label = self._labels.next("elihw")

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
                pass
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
                pass
            case AST.ExpressionInteger(integer):
                self._append_instruction(
                    Instruction(Op.PUSH,
                                Operand(Target(T.IMI, integer), Mode(M.DIR)))
                )
            case AST.ExpressionFloat(float, lineno):
                utils.error("code Generation",
                            "Floats are not implemented, yet.",
                            lineno)
            case AST.ExpressionBinop(binop, lhs, rhs) if binop in arithmic_op:
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
            case AST.ExpressionBinop(binop_cmp, lhs, rhs) if binop_cmp in comparison_op:
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
                if exp_list:
                    pass
            case AST.ExpressionList(exp, next):
                self.generate_code(exp)
                self.generate_code(next)
