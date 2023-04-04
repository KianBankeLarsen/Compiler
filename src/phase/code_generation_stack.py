from __future__ import annotations

import copy
from dataclasses import dataclass, field

import src.dataclass.AST as AST
import src.dataclass.symbol as dataclass_symbol
import src.utils.error
import src.utils.label_generator as label
from src.dataclass.iloc import Instruction, Mode, Operand, Target
from src.enums.code_generation_enum import M, Meta, Op, T
from src.enums.symbols_enum import NameCategory


@dataclass
class GenerateCode:
    """Orchestrating code generation. 
    The API exposes `generate_code` and `get_code`.

    ----------------------
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
    _code: list(Instruction) = field(default_factory=list)
    _scope_stack: list(AST.AstNode) = field(default_factory=list)
    _labels: label.Labels = label.Labels()

    def _append_instruction(self, instruction: Instruction) -> None:
        self._code.append(instruction)

    def _follow_static_link(self, symbol_level: int) -> None:
        level_difference = self._current_scope.level - symbol_level

        self._append_instruction(
            Instruction(Op.MOVE,
                        Operand(Target(T.RBP), Mode(M.DIR)),
                        Operand(Target(T.RSL), Mode(M.DIR)))
        )
        self._code.extend(
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

    def _epilog(self, body: AST.Body) -> None:
        # Deallocate stack space
        self._append_instruction(
            Instruction(Op.ADD,
                        Operand(
                            Target(T.IMI, 8*body.number_of_variables), Mode(M.DIR)),
                        Operand(Target(T.RSP), Mode(M.DIR)))
        )
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
        
        level_difference = self._current_scope.level - symbol_level
        if level_difference == 0:
            self._append_instruction(
                Instruction(Op.PUSH,
                            Operand(Target(T.RSL), Mode(M.DIR)))
            )
        else:
            self._append_instruction(
                Instruction(Op.PUSH,
                            Operand(Target(T.RSL), Mode(M.IRL, -7)))
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

    def get_code(self) -> list(Instruction):
        """Get copy of linear ILOC IR code.
        """

        return copy.deepcopy(self._code)

    def generate_code(self, ast_node: AST.AstNode) -> AST.AstNode:
        """Generate linear ILOC IR code.
        """

        ast_node = copy.deepcopy(ast_node)
        self._generate_code(ast_node)
        return ast_node

    def _generate_code(self, ast_node: AST.AstNode) -> None:
        match ast_node:
            case AST.Body(decls, stm_list):
                self._generate_code(decls)
                self._generate_code(stm_list)
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
                self._scope_stack.append(ast_node)
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
                self._epilog(body)
                self._append_instruction(
                    Instruction(Op.META, Meta.RET)
                )
                self._generate_code(body.decls)
                self._scope_stack.pop()
                self._current_scope = self._current_scope.parent
            case AST.StatementList(stm, next):
                self._generate_code(stm)
                self._generate_code(next)
            case AST.StatementAssignment(lhs, rhs):
                self._generate_code(rhs)

                symbol, symbol_level = self._current_scope.lookup(lhs)
                self._follow_static_link(symbol_level)

                match symbol:
                    case dataclass_symbol.Symbol(_, kind=NameCategory.PARAMETER, info=info):
                        self._append_instruction(
                            Instruction(Op.POP,
                                        Operand(Target(T.RSL), Mode(M.IRL, -(info + 16))))
                        )
                    case dataclass_symbol.Symbol(_, kind=NameCategory.VARIABLE, info=info):
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

                self._epilog(then_part)
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

                    self._epilog(else_part)
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

                self._epilog(body)
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

                self._epilog(body)
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
                label = self._scope_stack[-1].end_label

                if exp is None:
                    ins = Instruction(Op.RET_VOID, label)
                else:
                    ins = Instruction(Op.RET, label)

                self._append_instruction(ins)
            case AST.ExpressionIdentifier(identifier):
                """ move rbp, rsl
                    move -2(rsl), rsl - dereference zero or more times
                    push rsl_offset
                """
                symbol, symbol_level = self._current_scope.lookup(identifier)
                self._follow_static_link(symbol_level)

                match symbol:
                    case dataclass_symbol.Symbol(_, kind=NameCategory.PARAMETER, info=info):
                        self._append_instruction(
                            Instruction(Op.PUSH,
                                        Operand(Target(T.RSL), Mode(M.IRL, -(info + 16))))
                        )
                    case dataclass_symbol.Symbol(_, kind=NameCategory.VARIABLE, info=info):
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
