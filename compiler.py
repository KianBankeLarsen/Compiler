import AST_printer
import interfacing_program
import lexer_parser


lexer_parser.parser.parse(input(""), lexer=lexer_parser.lexer)

pp = AST_printer.ASTTreePrinter()

pp.build_graph(interfacing_program.the_program)
pp.render('png')
