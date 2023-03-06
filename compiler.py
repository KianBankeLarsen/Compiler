import interfacing_parser
import lexer_parser
import printers.AST_printer as AST_printer
import printers.symbol_printer as Symbol_printer
import symbols

lexer_parser.parser.parse(
    input("Write your input\n"), 
    lexer=lexer_parser.lexer)

the_program_AST = interfacing_parser.the_program

AST_pretty_printer = AST_printer.ASTTreePrinter("AST")
AST_pretty_printer.build_graph(the_program_AST)
AST_pretty_printer.render('png')

symbol_table_incorporator = symbols.ASTSymbolIncorporator()
symbol_table_incorporator.build_symbol_table(the_program_AST)

symbol_table_printer = Symbol_printer.SymbolPrinter("Symbol")
symbol_table_printer.build_graph(the_program_AST)
symbol_table_printer.render('png', {'rankdir': 'BT'})
