import AST
from printers.generic_printer import GenericPrinter


class SymbolPrinter(GenericPrinter):
    """
    """
        
    def __init__(self, name) -> GenericPrinter:
        super().__init__(name)

    def build_graph(self, ast_node: AST.AstNode) -> None:
        """
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                self.build_graph(decls)
                self.build_graph(stm_list)
            case AST.DeclarationList(decl, next):
                self.build_graph(decl)
                self.build_graph(next)
            case AST.DeclarationFunction(type, func, lineno):
                self.build_graph(func)
            case AST.Function(_, par_list, body):
                self.build_graph(par_list)
                self.build_graph(body)
                self.add_node(str(ast_node.symbol_table))
            case AST.StatementList(stm, next):
                self.build_graph(stm)
                self.build_graph(next)
            case AST.StatementIfthenelse(_, then_part, else_part):
                self.build_graph(then_part)
                self.add_node(str(ast_node.symbol_table_then))
                if else_part:
                    self.build_graph(else_part)
                    self.add_node(str(ast_node.symbol_table_else))
            case AST.StatementWhile(_, body):
                self.build_graph(body)
                self.add_node(str(ast_node.symbol_table))
            case AST.StatementFor(iter, _, _, body):
                self.build_graph(body)
                self.build_graph(iter)
                self.add_node(str(ast_node.symbol_table))