from __future__ import annotations

import graphviz


class GenericPrinter:
    """Basic functionality to instantiate Graphviz digraph.
    
    The API exposes functionality to add nodes, edges 
        and finally render the resulting graph.
    """
    
    def __init__(self, name: str) -> GenericPrinter:
        self.nodes = 0
        self.graph = graphviz.Digraph(name)

    def add_node(self, label: str) -> int:
        """Add node with custom `label`.

        Returns
        ---------
        Node number : int
            Total number of nodes in the graph.
        """

        self.graph.node(str(self.nodes), label)
        self.nodes += 1
        return str(self.nodes - 1)

    def add_edge(self, start: int, end: int) -> None:
        """Add edge between `start` and `end` node.
        """
        
        self.graph.edge(start, end)

    def render(self, format: str, attr: dict = {}) -> None:
        """Render Graphviz graph to any format.

        Parameter
        ---------
        format : str
            This could be png, pdf etc.

        Returns
        ---------
        Visualized of graph of the format specified.
        Output is in folder: /printer/images.
        """

        self.graph.format = format
        self.graph.directory = "./printer/images"
        self.graph.graph_attr.update(attr)
        self.graph.render()
