import utils.interfacing_parser as interfacing_parser
import phase.lexer as lexer
import phase.parser as parser
import printer.ast_printer as ast_printer
import printer.symbol_printer as Symbol_printer
import phase.symbol_collection as symbol_collection
import phase.code_generation_stack as code_generation_stack
import pprint

parser.parser.parse(
    input("Write your input\n"), 
    lexer=lexer.lexer)

the_program_AST = interfacing_parser.the_program

AST_pretty_printer = ast_printer.ASTTreePrinter("AST")
AST_pretty_printer.build_graph(the_program_AST)
AST_pretty_printer.render('png')

symbol_table_incorporator = symbol_collection.ASTSymbolIncorporator()
symbol_collection_IR = symbol_table_incorporator.build_symbol_table(the_program_AST)

symbol_table_printer = Symbol_printer.SymbolPrinter("Symbol")
symbol_table_printer.build_graph(symbol_collection_IR)
symbol_table_printer.render('png', {'rankdir': 'BT'})

code_generation_stack = code_generation_stack.GenerateCode()
code_generationed_IR = code_generation_stack.generate_code(symbol_collection_IR)
stack_program_code = code_generation_stack.get_code()
pp = pprint.PrettyPrinter()
pp.pprint(stack_program_code)