from __future__ import annotations

import graphviz

import AST


class ASTTreePrinter:
    def __init__(self) -> ASTTreePrinter:
        self.nodes = 0
        self.graph = graphviz.Digraph()

    def add_node(self, label: str) -> int:
        """Add node to graph

        Parameter
        ---------
        label : str
        """

        self.graph.node(str(self.nodes), label)
        self.nodes += 1
        return str(self.nodes - 1)

    def add_edge(self, start: int, end: int) -> None:
        """Add edge to graph

        Parameters
        ----------
        start : int
        end : int
        """

        self.graph.edge(start, end)

    def build_graph(self, ast_node: AST.AstNode) -> None:
        """Create Graphviz graph of AST.

        Parameter
        ---------
        ast_node : AstNode
        """

        match ast_node:
            case AST.Function(name, _, body):
                self.build_graph(body)
                ast_node.dotnum = self.add_node(name)
                self.add_edge(ast_node.dotnum, body.dotnum)
            case AST.Body(_, _, stm_list):
                self.build_graph(stm_list)
                ast_node.dotnum = self.add_node("body")
                self.add_edge(ast_node.dotnum, stm_list.dotnum)
            case AST.StatementAssignment(lhs, rhs):
                self.build_graph(rhs)
                ast_node.dotnum = self.add_node(lhs)
                self.add_edge(ast_node.dotnum, rhs.dotnum)
            case AST.StatementList(stm, next):
                ast_node.dotnum = self.add_node("stm_list")
                self.build_graph(stm)
                self.add_edge(ast_node.dotnum, stm.dotnum)
                if next:
                    self.build_graph(next)
                    self.add_edge(ast_node.dotnum, next.dotnum)
            case AST.ExpressionInteger(integer):
                ast_node.dotnum = self.add_node(str(integer))
            case AST.ExpressionIdentifier(identifier):
                ast_node.dotnum = self.add_node(identifier)
            case AST.ExpressionBinop(op, lhs, rhs):
                self.build_graph(lhs)
                self.build_graph(rhs)
                ast_node.dotnum = self.add_node(op)
                self.add_edge(ast_node.dotnum, lhs.dotnum)
                self.add_edge(ast_node.dotnum, rhs.dotnum)
            case _:
                raise ValueError(f"Unrecognized node: {ast_node}")

    def render(self, format: str) -> None:
        """Render Graphviz graph to any format.

        Parameter
        ---------
        format : str
        """

        self.graph.format = format
        self.graph.directory = "images"
        self.graph.render()
