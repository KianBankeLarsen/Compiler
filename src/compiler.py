import argparse
import pprint
import subprocess
from dataclasses import dataclass

import src.phase.code_generation_register
import src.phase.code_generation_stack
import src.phase.emit
import src.phase.lexer
import src.phase.allocator
import src.phase.parser
import src.phase.symbol_collection
import src.phase.syntactic_desugaring
import src.printer.ast_printer as ast_printer
import src.printer.symbol_printer as Symbol_printer
import src.utils.interfacing_parser as interfacing_parser


@dataclass
class PandaCompiler:
    """The actual compiler. 

    The API exposes compile.

    The compiler is instantiated with argparse options.

    Argparse options
    ----------------
    output: str
    compile: bool
    debug: bool
    file: str
    runTests: bool
    run: bool
    """

    args: argparse.Namespace

    def compile(self) -> None:
        """Compile file or input as specified upon creation of PandaCompiler.
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

        the_program_ast = interfacing_parser.the_program

        symbol_table_incorporator = src.phase.symbol_collection.ASTSymbolIncorporator()
        symbol_collection_ir = symbol_table_incorporator.build_symbol_table(
            the_program_ast)

        desugared_ast = src.phase.syntactic_desugaring.ASTSyntacticDesugar()
        desugared_ir = desugared_ast.desugar_AST(symbol_collection_ir)

        code_emitter = src.phase.emit.Emit()
        code = None

        if self.args.stack:
            code_generation_stack = src.phase.code_generation_stack.GenerateCodeStack()
            code_generation_stack.generate_code(desugared_ir)
            stack_program_code = code_generation_stack.get_code()
            code = stack_program_code
            assembly_code = code_emitter.emit(code)
        else:
            code_generation_register = src.phase.code_generation_register.GenerateCodeRegister()
            code_generation_register.generate_code(desugared_ir)
            register_program_code = code_generation_register.get_code()
            allocator = src.phase.allocator.Allocator()
            register_program_code = allocator.perform_register_allocation(
                register_program_code)
            code = register_program_code
            assembly_code = code_emitter.emit(code)

        if self.args.runTests:
            output = self.args.output
        else:
            output = f"src/output/{self.args.output}"

        with open(f"{output}.s", "w") as f:
            f.write(assembly_code)

        if self.args.compile or self.args.run:
            subprocess.call(["gcc", f"{output}.s", "-o", f"{output}.out"])

        if self.args.run:
            subprocess.call([f"{output}.out"])

        if self.args.debug:
            AST_pretty_printer = ast_printer.ASTTreePrinter(
                f"AST.{output}")
            AST_pretty_printer.build_graph(the_program_ast)
            AST_pretty_printer.render('png')

            AST_pretty_printer = ast_printer.ASTTreePrinter(
                f"AST-desugar.{output}")
            AST_pretty_printer.build_graph(desugared_ir)
            AST_pretty_printer.render('png')

            symbol_table_printer = Symbol_printer.SymbolPrinter(
                f"Symbol.{output}")
            symbol_table_printer.build_graph(symbol_collection_ir)
            symbol_table_printer.render('png', {'rankdir': 'BT'})

            if self.args.stack:
                with open(f"{output}.stack.iloc", 'w') as f:
                    pp = pprint.PrettyPrinter(stream=f)
                    pp.pprint(code)
            else:
                with open(f"{output}.register.iloc", 'w') as f:
                    pp = pprint.PrettyPrinter(stream=f)
                    pp.pprint(register_program_code)
