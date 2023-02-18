import graphviz

g = graphviz.Digraph('G', filename='hello.png')

g.edge('Hello', 'World')

g.view()