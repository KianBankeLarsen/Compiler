import argparse
import unittest
from src.compiler import PandaCompiler
import testing.test

argparser = argparse.ArgumentParser(
    prog='Compiler for Panda',
    description='Compiles source code to assembly'
)
argparser.add_argument(
    '-o', '--output',
    default='a',
    help="Specify name of assembly output file"
)
argparser.add_argument(
    '-c', '--compile',
    default=False,
    action='store_true',
    help="Set this flag if the output file should be compilled with gcc"
)
argparser.add_argument(
    '-d', '--debug',
    default=False,
    action='store_true',
    help="Set this flag for debugging information, i.e., ILOC and Graphviz"
)
argparser.add_argument(
    '-f', '--file',
    default=False,
    help="Path to input file, otherwise stdin will be used"
)
argparser.add_argument(
    '--runTests',
    default=False,
    action='store_true',
    help="Run tests"
)
argparser.add_argument(
    '-r', '--run',
    default=False,
    action='store_true',
    help="Run compilled program"
)
argparser.add_argument(
    '--testFlag',
    default=False,
    action='store_true',
    help="Run compilled program"
)
args = argparser.parse_args()

if args.runTests:
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(testing.test.load_tests(args))
else:
    args.runTests = args.testFlag
    PandaCompiler(args).compile()
