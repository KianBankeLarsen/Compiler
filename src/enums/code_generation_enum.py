from enum import Enum, auto


class Op(str, Enum):
    """Non-system specific opcodes.
    """

    MOVE = auto()
    PUSH = auto()
    POP = auto()
    CALL = auto()
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
    
    CMP = auto()


class Meta(Enum):
    """Meta operations for composite procedures.
    """

    CALL_PRINTF = auto()
    PROLOG = auto()
    EPILOG = auto()
    PRECALL = auto()
    POSTRETURN = auto()
    RET = auto()
