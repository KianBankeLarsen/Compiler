from src.enums.code_generation_enum import Op

intermediate_to_x86: dict = {
    Op.MOVE: "movq",
    Op.CALL: "callq",
    Op.PUSH: "pushq",
    Op.POP: "popq",
    Op.CMP: "cmpq",
    Op.JMP: "jmp",
    Op.JE: "je",
    Op.JNE: "jne",
    Op.JL: "jl",
    Op.JLE: "jle",
    Op.JG: "jg",
    Op.JGE: "jge",
    Op.ADD: "addq",
    Op.SUB: "subq",
    Op.MUL: "imulq",
}