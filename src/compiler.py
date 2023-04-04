import argparse
import pprint
import subprocess
from dataclasses import dataclass

import src.phase.code_generation_stack
import src.phase.emit
import src.phase.lexer
import src.phase.parser
import src.phase.symbol_collection
import src.printer.ast_printer as ast_printer
import src.printer.symbol_printer as Symbol_printer
import src.utils.interfacing_parser as interfacing_parser


@dataclass
class PandaCompiler:
    """
    """

    args: argparse.Namespace

    def compile(self):
        """
        """

        if self.args.file:
            with open(self.args.file, "r") as f:
                user_program = f.read()
        else:
            user_program = input()

        src.phase.parser.parser.parse(
            user_program,
            lexer=src.phase.lexer.lexer
        )

        the_program_AST = interfacing_parser.the_program

        symbol_table_incorporator = src.phase.symbol_collection.ASTSymbolIncorporator()
        symbol_collection_IR = symbol_table_incorporator.build_symbol_table(
            the_program_AST)

        code_generation_stack = src.phase.code_generation_stack.GenerateCode()
        code_generation_stack.generate_code(symbol_collection_IR)
        stack_program_code = code_generation_stack.get_code()

        code_emitter = src.phase.emit.Emit()
        assembly_code = code_emitter.emit(stack_program_code)

        output = f"src/output/{self.args.output}"

        with open(f"{output}.s", "w") as f:
            f.write(assembly_code)

        if self.args.compile:
            subprocess.call(["gcc", f"{output}.s", "-o", f"{output}.out"])

        if self.args.run:
            subprocess.call([f"{output}.out"])

        if self.args.debug:
            AST_pretty_printer = ast_printer.ASTTreePrinter(
                f"AST.{self.args.output}")
            AST_pretty_printer.build_graph(the_program_AST)
            AST_pretty_printer.render('png')

            symbol_table_printer = Symbol_printer.SymbolPrinter(
                f"Symbol.{self.args.output}")
            symbol_table_printer.build_graph(symbol_collection_IR)
            symbol_table_printer.render('png', {'rankdir': 'BT'})

            with open(f"./output/{self.args.output}.iloc", 'w') as f:
                pp = pprint.PrettyPrinter(stream=f)
                pp.pprint(stack_program_code)
