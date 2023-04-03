import sys
from typing import NoReturn


def error_message(phase: str, description: str, lineno: int) -> NoReturn:
    """Prints standardized error message and exits with error code 1.

    Parameters
    ----------
    phase : str
        Current compiler phase
    description : str
        User provided error message
    lineno : int
        Line number for error occurrence.
    """

    print(f"\nError in phase {phase}, line {lineno}:\n{description}",
          file=sys.stderr)
    sys.exit(1)
