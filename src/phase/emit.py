import copy

import src.dataclass.iloc as iloc
from src.enums.code_generation_enum import M, Meta, Op, T
from src.utils.label_generator import Labels
from src.utils.x86_instruction_enum_dict import intermediate_to_x86


class Emit:
    """Functionality to translate from linear ILOC IR to x86-64 assembly

    The API exposes emit.
    """

    def __init__(self):
        self._callee_save_reg: list[str] = [
            "rbx", "r12", "r13", "r14", "r15", "rbp"]
        self._calleer_save_reg: list[str] = [
            "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11"]

        self._labels = Labels()
        self._instruction_indent = 16
        self._code = []
        self._reg_scope = []
        self._registers_on_stack = -1

        self._enum_to_method_map = {
            Meta.CALL_PRINTF: self._call_printf,
            Meta.PROLOG: self._prolog,
            Meta.EPILOG: self._epilog,
            Meta.PRECALL: self._precall,
            Meta.POSTRETURN: self._postreturn,
            Meta.RET: self._ret
        }

    def emit(self, iloc_ir: list[iloc.Instruction]) -> str:
        """Translates the ILOC IR to x86-64 assembly instructions.

        The function outputs a string containing the complete program.
        """

        self._program_prologue()
        list(map(self._dispatch, iloc_ir))
        self._code.append("\n")
        return "\n".join(self._code)

    def _append_label(self, lbl: str) -> None:
        self._code.append(lbl + ":")

    def _append_instruction(self, instr_str) -> None:
        self._code.append(self._instruction_indent * " " + instr_str)

    def _append_newline(self) -> None:
        self._code.append("")

    def _append_section(self, section):
        self._code.append(f".{section}")

    def _dispatch(self, instruction: iloc.Instruction) -> None:
        # Remove redundant move instructions
        if instruction.opcode == Op.MOVE:
            for arg in instruction.args:
                if arg.target.spec == T.REG and arg.target.val is None:
                    return

        instructions = self._handle_reg_spill(instruction)

        for ins in instructions:
            match ins:
                case iloc.Instruction(opcode, args) if opcode in intermediate_to_x86:
                    line = intermediate_to_x86[opcode]
                    if len(args) > 0:
                        line += " " + self._do_operand(args[0])
                    for i in range(1, len(args)):
                        line += ", " + self._do_operand(args[i])
                    self._append_instruction(line)
                case iloc.Instruction(opcode=Op.DIV, args=args):
                    # prepare for division
                    self._append_instruction(
                        f"movq {self._do_operand(args[1])}, %rax")
                    # RDX:RAX <- sign-extend of RAX
                    self._append_instruction("cqo")
                    # divide
                    self._append_instruction(
                        f"idivq {self._do_operand(args[0])}")
                    # move to destination
                    self._append_instruction(
                        f"movq %rax, {self._do_operand(args[1])}")
                case iloc.Instruction(opcode=Op.LABEL, args=args):
                    self._append_label(args[0].target.val)
                case iloc.Instruction(opcode=Op.META, args=method):
                    self._enum_to_method_map[method[0]]()
                case _:
                    raise ValueError(f"Unknown instruction: {instruction}.")

    def _do_operand(self, operand: iloc.Operand) -> str:
        match operand.target:
            case iloc.Target(spec=T.IMI, val=val):
                text = f"${val}"
            case iloc.Target(spec=T.MEM, val=val):
                text = str(val)
            case iloc.Target(spec=T.RBP):
                text = "%rbp"
            case iloc.Target(spec=T.RSP):
                text = "%rsp"
            case iloc.Target(spec=T.RRT):
                text = "%rax"
            case iloc.Target(spec=T.RSL):
                text = "%rdx"
            case iloc.Target(spec=T.REG, val=1):
                text = "%rbx"
            case iloc.Target(spec=T.REG, val=2):
                text = "%rcx"
            case iloc.Target(spec=T.REG, val=3):
                text = "%rsi"
            case iloc.Target(spec=T.REG, val=4):
                text = "%rdi"
            case iloc.Target(spec=T.REG, val=5):
                text = "%r8"
            case iloc.Target(spec=T.REG, val=6):
                text = "%r9"
            case iloc.Target(spec=T.REG, val=7):
                text = "%r10"
            case iloc.Target(spec=T.REG, val=8):
                text = "%r12"
            case iloc.Target(spec=T.REG, val=9):
                text = "%r13"
            case iloc.Target(spec=T.REG, val=10):
                text = "%r14"
            case iloc.Target(spec=T.REG, val=11):
                text = "%r15"
            case _:
                raise ValueError(f"Unkown target: {operand.target}")

        match operand.addressing:
            case iloc.Mode(mode=M.DIR):
                pass
            case iloc.Mode(mode=M.IRL, offset=offset):
                text = f"{-8*offset}({text})"
            case _:
                raise ValueError(f"Unkown addressing: {operand.addressing}")

        return text


########################### REGISTER LOGIC ######################################## REGISTER LOGIC ###########################

    def _handle_reg_spill(self, instruction: iloc.Instruction) -> list[iloc.Instruction]:
        if instructions := self._check_register_dependent_operations(instruction):
            return instructions

        instructions.extend(
            self._check_if_spill_is_needed(instruction)
        )

        instructions.append(
            self._make_reference_to_spilled_registers(instruction)
        )

        return instructions

    def _check_register_dependent_operations(self, instruction: iloc.Instruction) -> list[iloc.Instruction]:
        instructions = []

        match instruction:
            case iloc.Instruction(opcode=op, args=(iloc.Operand(target=iloc.Target(spec=T.REG, val=val1)),
                                                   iloc.Operand(target=iloc.Target(spec=T.REG, val=val2)))) if op in [Op.ADD, Op.SUB, Op.DIV, Op.MUL, Op.CMP]:
                reg1 = val1
                reg2 = val2

                if val1 > 9:
                    reg1 = 10
                    instructions.append(
                        iloc.Instruction(Op.MOVE,
                                         iloc.Operand(iloc.Target(
                                             T.RSP), iloc.Mode(M.IRL, self._reg_scope[-1][val1] - self._registers_on_stack)),
                                         iloc.Operand(iloc.Target(T.REG, reg1), iloc.Mode(M.DIR)))
                    )
                if val2 > 9:
                    reg2 = 11
                    instructions.append(
                        iloc.Instruction(Op.MOVE,
                                         iloc.Operand(iloc.Target(
                                             T.RSP), iloc.Mode(M.IRL, self._reg_scope[-1][val2] - self._registers_on_stack)),
                                         iloc.Operand(iloc.Target(T.REG, reg2), iloc.Mode(M.DIR)))
                    )

                instructions.append(
                    iloc.Instruction(op,
                                     iloc.Operand(iloc.Target(
                                         T.REG, reg1), iloc.Mode(M.DIR)),
                                     iloc.Operand(iloc.Target(T.REG, reg2), iloc.Mode(M.DIR)))
                )

                if op is not Op.CMP and val2 > 9:
                    instructions.append(
                        iloc.Instruction(Op.MOVE,
                                         iloc.Operand(iloc.Target(
                                             T.REG, reg2), iloc.Mode(M.DIR)),
                                         iloc.Operand(iloc.Target(T.RSP), iloc.Mode(M.IRL, self._reg_scope[-1][val2] - self._registers_on_stack)))
                    )

        return instructions

    def _check_if_spill_is_needed(self, instruction: iloc.Instruction) -> list[iloc.Instruction]:
        instructions = []

        match instruction:
            case iloc.Instruction(opcode=Op.MOVE, args=(iloc.Operand(), iloc.Operand(target=iloc.Target(spec=T.REG, val=val)))) if val > 9:
                if val not in self._reg_scope[-1]:
                    self._registers_on_stack += 1
                    self._reg_scope[-1][val] = self._registers_on_stack
                    instructions.append(
                        iloc.Instruction(Op.SUB,
                                         iloc.Operand(iloc.Target(
                                             T.IMI, 8), iloc.Mode(M.DIR)),
                                         iloc.Operand(iloc.Target(T.RSP), iloc.Mode(M.DIR)))
                    )

        return instructions

    def _make_reference_to_spilled_registers(self, instruction: iloc.Instruction) -> iloc.Instruction:
        instruction = copy.deepcopy(instruction)

        if instruction.opcode is not Op.META and instruction.opcode is not Op.LABEL:
            for i in range(len(instruction.args)):
                if instruction.args[i].target.spec == T.REG and instruction.args[i].target.val > 9:
                    if len(instruction.args) == 1:
                        val = instruction.args[0].target.val
                        instruction.args = (iloc.Operand(
                            iloc.Target(T.RSP), iloc.Mode(M.IRL, self._reg_scope[-1][val] - self._registers_on_stack)),)
                    elif i == 0:
                        val = instruction.args[0].target.val
                        instruction.args = (iloc.Operand(iloc.Target(
                            T.RSP), iloc.Mode(M.IRL, self._reg_scope[-1][val] - self._registers_on_stack)), instruction.args[1])
                    else:
                        val = instruction.args[1].target.val
                        instruction.args = (instruction.args[0], iloc.Operand(
                            iloc.Target(T.RSP), iloc.Mode(M.IRL, self._reg_scope[-1][val] - self._registers_on_stack)))

        return instruction

########################### META ########################### META ########################### META ###########################

    def _save_retore_reg(self, mode: str, registers: list or reversed) -> None:
        self._append_newline()
        for reg in registers:
            self._append_instruction(f"{mode} %{reg}")
        self._append_newline()

    def _prolog(self) -> None:
        self._reg_scope.append({})
        self._save_retore_reg("pushq", self._callee_save_reg)
        self._append_instruction("movq %rsp, %rbp")
        self._append_newline()

    def _epilog(self) -> None:
        self._reg_scope.pop()
        self._append_instruction("movq %rbp, %rsp")
        self._save_retore_reg("popq", reversed(self._callee_save_reg))
        self._append_newline()

    def _ret(self) -> None:
        self._append_instruction("ret")

    def _precall(self) -> None:
        self._save_retore_reg("pushq", self._calleer_save_reg)

    def _postreturn(self) -> None:
        self._save_retore_reg("popq", reversed(self._calleer_save_reg))

    def _program_prologue(self) -> None:
        self._append_section("data")
        self._append_newline()
        self._append_label("form")
        self._append_instruction('.string "%d\\n"')
        self._append_newline()
        self._append_section("text")
        self._append_newline()
        self._append_section("globl main")
        self._append_newline()

    # * The printf function is borrowed from SCIL.
    def _call_printf(self) -> None:
        # pass 1. argument in %rdi
        self._append_instruction("leaq form(%rip), %rdi")
        # By-passing caller save values on the stack:
        # pass 2. argument in %rsi
        self._append_instruction(
            f"movq {8*len(self._calleer_save_reg)}(%rsp), %rsi")
        # no floating point registers used
        self._append_instruction("movq $0, %rax")
        # saving stack pointer for change check
        self._append_instruction("movq %rsp, %rcx")
        # aligning stack pointer for call
        self._append_instruction("andq $-16, %rsp")
        self._append_instruction("movq $0, %rbx")  # preparing check indicator
        # checking for alignment change
        self._append_instruction("cmpq %rsp, %rcx")
        lbl = self._labels.next("aligned")
        self._append_instruction(f"je {lbl}")  # jump if correctly aligned
        # it was not aligned, indicate by '1'
        self._append_instruction("incq %rbx")
        self._append_label(lbl)
        self._append_instruction("pushq %rbx")  # pushing 0/1 on the stack
        self._append_instruction("subq $8, %rsp")  # aligning
        self._append_instruction("callq printf@plt")  # call printf
        self._append_instruction("addq $8, %rsp")  # revert latest aligning
        self._append_instruction("popq %rbx")  # get alignment indicator
        # checking for alignment change
        self._append_instruction("cmpq $0, %rbx")
        lbl = self._labels.next("aligned")
        self._append_instruction(f"je {lbl}")  # jump if correctly aligned
        # revert earlier alignment change
        self._append_instruction("addq $8, %rsp")
        self._append_label(lbl)
        self._append_newline()
