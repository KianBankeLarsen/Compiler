from enum import Enum, auto


class Op(str, Enum):
    """Non-system specific opcodes.
    """
    
    MOVE = auto()
    PUSH = auto()
    POP = auto()
    CALL = auto()
    RET = auto()
    CMP = auto()
    JMP = auto()
    LABEL = auto()
    META = auto()
    JE = "=="
    JNE = "!="
    JL = "<"
    JLE = "<="
    JG = ">"
    JGE = ">="
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"


class M(Enum):
    """Addressing modes.

    Several options are possible, but we only differentiate 
    whether the addressing is direct or not.
    """
    
    DIR = auto()  # direct
    IRL = auto()  # indirect relative


class T(Enum):
    """Non-system specific register classes.
    """
    
    IMI = auto()  # immediate integer
    MEM = auto()  # memory (a label)
    RBP = auto()  # register: base (frame) pointer
    RSP = auto()  # register: stack pointer
    RRT = auto()  # register: return value
    RSL = auto()  # register: static link computation
    REG = auto()  # general-purpose registers


class Meta(Enum):
    """Meta operations for composite procedures.
    """

    MAIN_CALLEE_SAVE = auto()
    MAIN_CALLEE_RESTORE = auto()
    CALLEE_PROLOGUE = auto()
    CALLEE_EPILOGUE = auto()
    CALLEE_SAVE = auto()
    CALLEE_RESTORE = auto()
    CALLER_PROLOGUE = auto()
    CALLER_EPILOGUE = auto()
    CALLER_SAVE = auto()
    CALLER_RESTORE = auto()
    CALL_PRINTF = auto()
    ALLOCATE_STACK_SPACE = auto()
    DEALLOCATE_STACK_SPACE = auto()
    REVERSE_PUSH_ARGUMENTS = auto()
