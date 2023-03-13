import utils.interfacing_parser as interfacing_parser
import phase.lexer as lexer
import phase.parser as parser
import printer.AST_printer as AST_printer
import printer.symbol_printer as Symbol_printer
import phase.symbol_collection as symbol_collection


parser.parser.parse(
    input("Write your input\n"), 
    lexer=lexer.lexer)

the_program_AST = interfacing_parser.the_program

AST_pretty_printer = AST_printer.ASTTreePrinter("AST")
AST_pretty_printer.build_graph(the_program_AST)
AST_pretty_printer.render('png')

symbol_table_incorporator = symbol_collection.ASTSymbolIncorporator()
symbol_table_incorporator.build_symbol_table(the_program_AST)

symbol_table_printer = Symbol_printer.SymbolPrinter("Symbol")
symbol_table_printer.build_graph(the_program_AST)
symbol_table_printer.render('png', {'rankdir': 'BT'})
