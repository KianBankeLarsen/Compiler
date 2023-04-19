import argparse
import unittest
from src.compiler import PandaCompiler
import testing.test
import shutil

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
    '-t', '--runTests',
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

args = argparser.parse_args()

if args.runTests:
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(testing.test.load_tests(args))

    if result.errors or result.failures:
        raise ValueError("Test failed")
    
    if args.debug and not result.errors:
        shutil.rmtree("src/printer/images/AST.testing")
        shutil.rmtree("src/printer/images/AST-desugar.testing")
        shutil.rmtree("src/printer/images/Symbol.testing")
else:
    PandaCompiler(args).compile()
