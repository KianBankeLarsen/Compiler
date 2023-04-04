import src.dataclass.AST as AST
from src.printer.generic_printer import GenericPrinter


class SymbolPrinter(GenericPrinter):
    """Facilitating visualization of symbol tables.
    """

    def __init__(self, name: str) -> GenericPrinter:
        super().__init__(name)

    def _add_scope(self, ast_node: AST.AstNode, symbol_table_name: str):
        symbol_table = getattr(ast_node, symbol_table_name)
        symbol_table.dotnum = self.add_node(str(symbol_table))
        if symbol_table.parent:
            self.add_edge(symbol_table.dotnum, symbol_table.parent.dotnum)

    def build_graph(self, ast_node: AST.AstNode) -> None:
        """Build Dot digraph to visualize lexical scopes.
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                self.build_graph(decls)
                self.build_graph(stm_list)
            case AST.DeclarationList(decl, next):
                self.build_graph(decl)
                self.build_graph(next)
            case AST.DeclarationFunction(_, func):
                self.build_graph(func)
            case AST.Function(_, par_list, body):
                self._add_scope(ast_node, "symbol_table")
                self.build_graph(par_list)
                self.build_graph(body)
            case AST.StatementList(stm, next):
                self.build_graph(stm)
                self.build_graph(next)
            case AST.StatementIfthenelse(_, then_part, else_part):
                self._add_scope(ast_node, "symbol_table_then")
                self.build_graph(then_part)
                if else_part:
                    self._add_scope(ast_node, "symbol_table_else")
                    self.build_graph(else_part)
            case AST.StatementWhile(_, body):
                self._add_scope(ast_node, "symbol_table")
                self.build_graph(body)
            case AST.StatementFor(iter, _, _, body):
                self._add_scope(ast_node, "symbol_table")
                self.build_graph(body)
                self.build_graph(iter)
