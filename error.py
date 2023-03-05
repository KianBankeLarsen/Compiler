import sys


def error_message(phase, description, lineno):

    print(f"\nError in phase {phase}, line {lineno}:\n{description}",
          file=sys.stderr)
    sys.exit(1)
    