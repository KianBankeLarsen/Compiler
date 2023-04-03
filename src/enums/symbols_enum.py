from enum import Enum, auto


class NameCategory(Enum):
    """Possible symbol categories.
    """

    VARIABLE = auto()
    PARAMETER = auto()
    FUNCTION = auto()