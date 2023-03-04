from __future__ import annotations

import graphviz

import AST


class ASTTreePrinter:
    def __init__(self) -> ASTTreePrinter:
        self.nodes = 0
        self.graph = graphviz.Digraph()

    def _add_node(self, label: str) -> int:
        self.graph.node(str(self.nodes), label)
        self.nodes += 1
        return str(self.nodes - 1)

    def _add_edge(self, start: int, end: int) -> None:
        self.graph.edge(start, end)

    def build_graph(self, ast_node: AST.AstNode) -> None:
        """Create Graphviz graph of AST.

        Parameter
        ---------
        ast_node : AstNode
            Root of any AstNode subtree to perform post-order traversal.
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                ast_node.dotnum = self._add_node("body")
                if decls:
                    self.build_graph(decls)
                    self._add_edge(ast_node.dotnum, decls.dotnum)
                if stm_list:
                    self.build_graph(stm_list)
                    self._add_edge(ast_node.dotnum, stm_list.dotnum)
            case AST.DeclarationList(decl, next):
                self.build_graph(decl)
                ast_node.dotnum = self._add_node("decl_list")
                if next:
                    self.build_graph(next)
                    self._add_edge(ast_node.dotnum, next.dotnum)
                self._add_edge(ast_node.dotnum, decl.dotnum)
            case AST.DeclarationFunction(type, func):
                ast_node.dotnum = self._add_node("func_decl")
                self.build_graph(func)
                tmp_dotnum = self._add_node(type)
                self._add_edge(ast_node.dotnum, func.dotnum)
                self._add_edge(ast_node.dotnum, tmp_dotnum)
            case AST.DeclarationVariableList(type, var_lst):
                ast_node.dotnum = self._add_node("var_decl")
                self.build_graph(var_lst)
                tmp_dotnum = self._add_node(type)
                self._add_edge(ast_node.dotnum, var_lst.dotnum)
                self._add_edge(ast_node.dotnum, tmp_dotnum)
            case AST.DeclarationVariableInit(type, name, exp):
                ast_node.dotnum = self._add_node("init_var_decl")
                self.build_graph(exp)
                tmp_dotnum = self._add_node(type)
                tmp_dotnum2 = self._add_node(name)
                self._add_edge(ast_node.dotnum, tmp_dotnum)
                self._add_edge(ast_node.dotnum, tmp_dotnum2)
                self._add_edge(ast_node.dotnum, exp.dotnum)
            case AST.VariableList(name, next):
                ast_node.dotnum = self._add_node(name)
                if next:
                    self.build_graph(next)
                    self._add_edge(ast_node.dotnum, next.dotnum)
            case AST.Function(name, par_list, body):
                ast_node.dotnum = self._add_node(name)
                if par_list:
                    self.build_graph(par_list)
                    self._add_edge(ast_node.dotnum, par_list.dotnum)
                if body:
                    self.build_graph(body)
                    self._add_edge(ast_node.dotnum, body.dotnum)
            case AST.Parameter(type, name):
                ast_node.dotnum = self._add_node("param")
                tmp_dotnum = self._add_node(type)
                tmp_dotnum2 = self._add_node(name)
                self._add_edge(ast_node.dotnum, tmp_dotnum)
                self._add_edge(ast_node.dotnum, tmp_dotnum2)
            case AST.ParameterList(param, next):
                self.build_graph(param)
                ast_node.dotnum = self._add_node("param_list")
                self._add_edge(ast_node.dotnum, param.dotnum)
                if next:
                    self.build_graph(next)
                    self._add_edge(ast_node.dotnum, next.dotnum)
            case AST.StatementList(stm, next):
                ast_node.dotnum = self._add_node("stm_list")
                self.build_graph(stm)
                self._add_edge(ast_node.dotnum, stm.dotnum)
                if next:
                    self.build_graph(next)
                    self._add_edge(ast_node.dotnum, next.dotnum)
            case AST.StatementAssignment(lhs, rhs):
                self.build_graph(rhs)
                ast_node.dotnum = self._add_node("=")
                tmp_dotnum = self._add_node(lhs)
                self._add_edge(ast_node.dotnum, tmp_dotnum)
                self._add_edge(ast_node.dotnum, rhs.dotnum)
            case AST.StatementIfthenelse(exp, stm_list1, stm_list2):
                self.build_graph(exp)
                self.build_graph(stm_list1)
                ast_node.dotnum = self._add_node("if")
                if stm_list2:
                    self.build_graph(stm_list2)
                    self._add_edge(ast_node.dotnum, stm_list2.dotnum)
                self._add_edge(ast_node.dotnum, exp.dotnum)
                self._add_edge(ast_node.dotnum, stm_list1.dotnum)
            case AST.StatementWhile(exp, stm_list):
                self.build_graph(exp)
                self.build_graph(stm_list)
                ast_node.dotnum = self._add_node("while")
                self._add_edge(ast_node.dotnum, exp.dotnum)
                self._add_edge(ast_node.dotnum, stm_list.dotnum)
            case AST.StatementFor(iter, exp, assign, exp_list):
                self.build_graph(iter)
                self.build_graph(exp)
                self.build_graph(assign)
                self.build_graph(exp_list)
                ast_node.dotnum = self._add_node("for")
                self._add_edge(ast_node.dotnum, iter.dotnum)
                self._add_edge(ast_node.dotnum, exp.dotnum)
                self._add_edge(ast_node.dotnum, assign.dotnum)
                self._add_edge(ast_node.dotnum, exp_list.dotnum)
            case AST.StatementPrint(exp):
                self.build_graph(exp)
                ast_node.dotnum = self._add_node("print")
                self._add_edge(ast_node.dotnum, exp.dotnum)
            case AST.StatementReturn(exp):
                self.build_graph(exp)
                ast_node.dotnum = self._add_node("return")
                self._add_edge(ast_node.dotnum, exp.dotnum)
            case AST.ExpressionIdentifier(identifier):
                ast_node.dotnum = self._add_node(identifier)
            case AST.ExpressionInteger(integer):
                ast_node.dotnum = self._add_node(str(integer))
            case AST.ExpressionBinop(op, lhs, rhs):
                self.build_graph(lhs)
                self.build_graph(rhs)
                ast_node.dotnum = self._add_node(op)
                self._add_edge(ast_node.dotnum, lhs.dotnum)
                self._add_edge(ast_node.dotnum, rhs.dotnum)
            case AST.ExpressionCall(name, exp_list):
                ast_node.dotnum = self._add_node("call " + name)
                if exp_list:
                    self.build_graph(exp_list)
                    self._add_edge(ast_node.dotnum, exp_list.dotnum)
            case AST.ExpressionList(exp, next):
                self.build_graph(exp)
                ast_node.dotnum = self._add_node("expr_list")
                self._add_edge(ast_node.dotnum, exp.dotnum)
                if next:
                    self.build_graph(next)
                    self._add_edge(ast_node.dotnum, next.dotnum)
            case _:
                raise ValueError(f"Unrecognized node: {ast_node}")

    def render(self, format: str) -> None:
        """Render Graphviz graph to any format.

        Parameter
        ---------
        format : str
            This could be png, pdf etc.
        """

        self.graph.format = format
        self.graph.directory = "./printers/images"
        self.graph.render()
