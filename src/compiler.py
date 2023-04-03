import argparse
import pprint
import subprocess

import phase.code_generation_stack as code_generation_stack
import phase.emit as emit
import phase.lexer as lexer
import phase.parser as parser
import phase.symbol_collection as symbol_collection
import printer.ast_printer as ast_printer
import printer.symbol_printer as Symbol_printer
import utils.interfacing_parser as interfacing_parser

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
args = argparser.parse_args()

if args.file:
    with open(args.file, "r") as f:
        input = f.read()
else:
    input = input()

parser.parser.parse(
    input,
    lexer=lexer.lexer
)

the_program_AST = interfacing_parser.the_program

symbol_table_incorporator = symbol_collection.ASTSymbolIncorporator()
symbol_collection_IR = symbol_table_incorporator.build_symbol_table(
    the_program_AST)

code_generation_stack = code_generation_stack.GenerateCode()
code_generated_IR = code_generation_stack.generate_code(symbol_collection_IR)
stack_program_code = code_generation_stack.get_code()

code_emitter = emit.Emit()
assembly_code = code_emitter.emit(stack_program_code)

output = f"./output/{args.output}"

with open(f"{output}.s", "w") as f:
    f.write(assembly_code)

if args.compile:
    subprocess.call(["gcc", f"{output}.s", "-o", f"{output}.out"])

if args.run:
    subprocess.call([f"./{output}.out"])

if args.debug:
    AST_pretty_printer = ast_printer.ASTTreePrinter(f"AST.{args.output}")
    AST_pretty_printer.build_graph(the_program_AST)
    AST_pretty_printer.render('png')

    symbol_table_printer = Symbol_printer.SymbolPrinter(
        f"Symbol.{args.output}")
    symbol_table_printer.build_graph(symbol_collection_IR)
    symbol_table_printer.render('png', {'rankdir': 'BT'})

    with open(f"./output/{args.output}.iloc", 'w') as f:
        pp = pprint.PrettyPrinter(stream=f)
        pp.pprint(stack_program_code)

if args.runTests:
    pass
