import AST
from printers.generic_printer import GenericPrinter


class SymbolPrinter(GenericPrinter):
    """
    """
        
    def __init__(self) -> GenericPrinter:
        super().__init__()

    def build_graph(self, ast_node: AST.AstNode) -> None:
        pass