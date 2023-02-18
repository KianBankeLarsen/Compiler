from lexer_parser import LexerParser
from AST_printer import ASTTreePrinterVisitor

ast = LexerParser().the_program
pp = ASTTreePrinterVisitor()
ast.accept(pp)