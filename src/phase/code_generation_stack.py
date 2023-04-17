from __future__ import annotations

import copy
from dataclasses import dataclass, field

import src.dataclass.AST as AST
import src.dataclass.symbol as dataclass_symbol
import src.phase.code_generation_base
import src.utils.error
from src.dataclass.iloc import Instruction, Mode, Operand, Target
from src.enums.code_generation_enum import M, Meta, Op, T
from src.enums.symbols_enum import NameCategory


@dataclass
class GenerateCodeStack(src.phase.code_generation_base.GenerateCodeBase):
    """Orchestrating stack code generation. 
    The API exposes `generate_code` and `get_code`.
    """

    _code: list[Instruction] = field(default_factory=list)

    def _append_instruction(self, instruction: Instruction) -> None:
        self._code.append(instruction)

    def _get_code_block_to_extend(self) -> list[Instruction]:
        return self._code
    
    def get_code(self) -> list(Instruction):
        """Get copy of linear ILOC IR code.
        """

        return copy.deepcopy(self._code)

    def _generate_code(self, ast_node: AST.AstNode) -> None:
        match ast_node:
            case AST.Body(decls, stm_list):
                self._body_stack.append(ast_node)
                self._generate_code(decls)
                self._generate_code(stm_list)
                self._body_stack.pop()
            case AST.DeclarationList(decl, next):
                self._generate_code(decl)
                self._generate_code(next)
            case AST.DeclarationFunction(_, function):
                self._generate_code(function)
            case AST.Function(name, _, body):
                """ start_label
                    prolog
                    allocate stack
                    body
                    end_label
                    deallocate stack
                    epilog
                """
                self._current_scope = ast_node.symbol_table
                self._function_stack.append(ast_node)
                self._ensure_labels(ast_node)

                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.start_label), Mode(M.DIR)))
                )
                self._prolog(body)

                self._generate_code(body.stm_list)

                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.end_label), Mode(M.DIR)))
                )
                self._epilog()
                self._append_instruction(
                    Instruction(Op.META, Meta.RET)
                )
                self._generate_code(body.decls)
                self._function_stack.pop()
                self._current_scope = self._current_scope.parent
            case AST.StatementList(stm, next):
                self._generate_code(stm)
                self._generate_code(next)
            case AST.StatementAssignment(lhs, rhs):
                self._generate_code(rhs)

                symbol, symbol_level = self._current_scope.lookup(lhs)
                self._follow_static_link(symbol_level)

                match symbol:
                    case dataclass_symbol.Symbol(kind=NameCategory.PARAMETER, info=info):
                        self._append_instruction(
                            Instruction(Op.POP,
                                        Operand(Target(T.RSL), Mode(M.IRL, -(info + 16))))
                        )
                    case dataclass_symbol.Symbol(kind=NameCategory.VARIABLE, info=info):
                        self._append_instruction(
                            Instruction(Op.POP,
                                        Operand(Target(T.RSL), Mode(M.IRL, info + 1)))
                        )
                    case _:
                        raise ValueError(
                            f"Symbol kind, {symbol.kind}, is unknown.")
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

                self._generate_code(exp)

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

                self._current_scope = ast_node.symbol_table_then
                self._precall(None, self._current_scope.level)
                self._push_pseudo_return_address()
                self._prolog(then_part)

                self._generate_code(then_part)

                self._epilog()
                self._pop_pseudo_return_address()
                self._postreturn(0)
                self._current_scope = self._current_scope.parent

                self._append_instruction(
                    Instruction(Op.JMP, Operand(
                        Target(T.MEM, ast_node.esle_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.else_label), Mode(M.DIR)))
                )

                if else_part:
                    self._current_scope = ast_node.symbol_table_else
                    self._precall(None, self._current_scope.level)
                    self._push_pseudo_return_address()
                    self._prolog(else_part)

                    self._generate_code(else_part)

                    self._epilog()
                    self._pop_pseudo_return_address()
                    self._postreturn(0)
                    self._current_scope = self._current_scope.parent

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

                self._current_scope = ast_node.symbol_table
                ast_node.while_label = self._labels.next("while")
                ast_node.elihw_label = self._labels.next("elihw")

                self._precall(None, self._current_scope.level)
                self._push_pseudo_return_address()
                self._prolog(body)

                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.while_label), Mode(M.DIR)))
                )

                self._generate_code(exp)

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
                                Operand(Target(T.MEM, ast_node.elihw_label), Mode(M.DIR)))
                )

                self._generate_code(body)

                self._append_instruction(
                    Instruction(Op.JMP,
                                Operand(Target(T.MEM, ast_node.while_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.elihw_label), Mode(M.DIR)))
                )

                self._epilog()
                self._pop_pseudo_return_address()
                self._postreturn(0)

                self._current_scope = self._current_scope.parent
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
                self._current_scope = ast_node.symbol_table
                ast_node.for_label = self._labels.next("for")
                ast_node.rof_label = self._labels.next("rof")

                self._precall(
                    AST.ExpressionList(iter.exp, None, iter.lineno),
                    self._current_scope.level
                )
                self._push_pseudo_return_address()
                self._prolog(body)

                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.for_label), Mode(M.DIR)))
                )

                self._generate_code(exp)

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
                                Operand(Target(T.MEM, ast_node.rof_label), Mode(M.DIR)))
                )

                self._generate_code(body)
                self._generate_code(assign)

                self._append_instruction(
                    Instruction(Op.JMP,
                                Operand(Target(T.MEM, ast_node.for_label), Mode(M.DIR)))
                )
                self._append_instruction(
                    Instruction(Op.LABEL,
                                Operand(Target(T.MEM, ast_node.rof_label), Mode(M.DIR)))
                )

                self._epilog()
                self._pop_pseudo_return_address
                self._postreturn(ast_node.number_of_parameters)

                self._current_scope = self._current_scope.parent
            case AST.StatementPrint(exp):
                """ push argument
                    precall
                    call printf
                    postreturn
                    remove argument
                """
                self._generate_code(exp)

                self._append_instruction(
                    Instruction(Op.META, Meta.PRECALL)
                )
                self._append_instruction(
                    Instruction(Op.META, Meta.CALL_PRINTF)
                )
                self._append_instruction(
                    Instruction(Op.META, Meta.POSTRETURN)
                )
            case AST.StatementReturn(exp):
                self._generate_code(exp)
                func = self._function_stack[-1]

                if exp:
                    self._append_instruction(
                        Instruction(Op.POP,
                                    Operand(Target(T.RRT), Mode(M.DIR)))
                    )

                if self._body_stack:
                    vars = 0
                    for stack_frame in self._body_stack:
                        vars += stack_frame.number_of_variables

                    save_reg = len(self._body_stack)*16*8
                    local_vars = 8*vars
                    vars_function = func.body.number_of_variables*8
                    self._append_instruction(
                        Instruction(Op.ADD,
                                    Operand(
                                        Target(T.IMI, save_reg + local_vars + vars_function), Mode(M.DIR)),
                                    Operand(Target(T.RSP), Mode(M.DIR)))
                    )

                    self._append_instruction(
                        Instruction(Op.MOVE,
                                    Operand(Target(T.RSP), Mode(M.DIR)),
                                    Operand(Target(T.RBP), Mode(M.DIR)))
                    )

                self._append_instruction(
                    Instruction(Op.JMP,
                                Operand(Target(T.MEM, func.end_label), Mode(M.DIR)))
                )
            case AST.ExpressionIdentifier(identifier):
                """ move rbp, rsl
                    move -2(rsl), rsl - dereference zero or more times
                    push rsl_offset
                """
                symbol, symbol_level = self._current_scope.lookup(identifier)
                self._follow_static_link(symbol_level)

                match symbol:
                    case dataclass_symbol.Symbol(kind=NameCategory.PARAMETER, info=info):
                        self._append_instruction(
                            Instruction(Op.PUSH,
                                        Operand(Target(T.RSL), Mode(M.IRL, -(info + 16))))
                        )
                    case dataclass_symbol.Symbol(kind=NameCategory.VARIABLE, info=info):
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
                src.utils.error("code Generation",
                                "Floats are not implemented, yet.",
                                lineno)
            case AST.ExpressionBinop(binop, lhs, rhs) if binop in [Op.ADD, Op.SUB, Op.DIV, Op.MUL]:
                """ pop reg1
                    pop reg2
                    op reg1, reg2
                    push reg2
                """
                self._generate_code(lhs)
                self._generate_code(rhs)

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
            case AST.ExpressionBinop(binop_cmp, lhs, rhs) if binop_cmp in [Op.JE, Op.JNE, Op.JL, Op.JG, Op.JGE, Op.JLE]:
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
                self._generate_code(lhs)
                self._generate_code(rhs)

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
                """ push arguments
                    precall
                    set up ARP
                    call label
                    remove ARP
                    postreturn
                    remove arguments
                    push rrt
                """
                # Constant work
                symbol, symbol_level = self._current_scope.lookup(name)
                func = symbol.info
                self._ensure_labels(func)

                self._precall(exp_list, symbol_level)

                # Make the call
                self._append_instruction(
                    Instruction(Op.CALL,
                                Operand(Target(T.MEM, func.start_label), Mode(M.DIR)))
                )

                self._postreturn(func.number_of_parameters)

                # Put return value on the stack (if any)
                if symbol.type != "void":
                    self._append_instruction(
                        Instruction(Op.PUSH,
                                    Operand(Target(T.RRT), Mode(M.DIR)))
                    )
            case AST.ExpressionList(exp, next):
                self._generate_code(next)
                self._generate_code(exp)
