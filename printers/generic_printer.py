from __future__ import annotations

import graphviz


class GenericPrinter:
    """
    """
    
    def __init__(self, name) -> GenericPrinter:
        self.nodes = 0
        self.graph = graphviz.Digraph(name)

    def add_node(self, label: str) -> int:
        """
        """

        self.graph.node(str(self.nodes), label)
        self.nodes += 1
        return str(self.nodes - 1)

    def add_edge(self, start: int, end: int) -> None:
        """
        """
        
        self.graph.edge(start, end)

    def render(self, format: str, attr: dict = {}) -> None:
        """Render Graphviz graph to any format.

        Parameter
        ---------
        format : str
            This could be png, pdf etc.
        """

        self.graph.format = format
        self.graph.directory = "./printers/images"
        self.graph.graph_attr.update(attr)
        self.graph.render()