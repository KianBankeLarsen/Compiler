from __future__ import annotations

import dataclass.AST as AST
from printer.generic_printer import GenericPrinter


class ASTTreePrinter(GenericPrinter):
    """Facilitating visualization of abstract syntax tree.
    """

    def __init__(self, name: str) -> GenericPrinter:
        super().__init__(name)

    def build_graph(self, ast_node: AST.AstNode) -> None:
        """Create Graphviz graph of AST.

        Parameter
        ---------
        ast_node : AstNode
            Root of any AstNode subtree to perform post-order traversal.
        """

        match ast_node:
            case AST.Body(decls, stm_list):
                ast_node.dotnum = self.add_node("body")
                if decls:
                    self.build_graph(decls)
                    self.add_edge(ast_node.dotnum, decls.dotnum)
                if stm_list:
                    self.build_graph(stm_list)
                    self.add_edge(ast_node.dotnum, stm_list.dotnum)
            case AST.DeclarationList(decl, next):
                self.build_graph(decl)
                ast_node.dotnum = self.add_node("decl_list")
                if next:
                    self.build_graph(next)
                    self.add_edge(ast_node.dotnum, next.dotnum)
                self.add_edge(ast_node.dotnum, decl.dotnum)
            case AST.DeclarationFunction(type, func):
                ast_node.dotnum = self.add_node("func_decl")
                self.build_graph(func)
                tmp_dotnum = self.add_node(type)
                self.add_edge(ast_node.dotnum, func.dotnum)
                self.add_edge(ast_node.dotnum, tmp_dotnum)
            case AST.DeclarationVariableList(type, var_lst):
                ast_node.dotnum = self.add_node("var_decl")
                self.build_graph(var_lst)
                tmp_dotnum = self.add_node(type)
                self.add_edge(ast_node.dotnum, var_lst.dotnum)
                self.add_edge(ast_node.dotnum, tmp_dotnum)
            case AST.DeclarationVariableInit(type, name, exp):
                ast_node.dotnum = self.add_node("init_var_decl")
                self.build_graph(exp)
                tmp_dotnum = self.add_node(type)
                tmp_dotnum2 = self.add_node(name)
                self.add_edge(ast_node.dotnum, tmp_dotnum)
                self.add_edge(ast_node.dotnum, tmp_dotnum2)
                self.add_edge(ast_node.dotnum, exp.dotnum)
            case AST.VariableList(name, next):
                ast_node.dotnum = self.add_node(name)
                if next:
                    self.build_graph(next)
                    self.add_edge(ast_node.dotnum, next.dotnum)
            case AST.Function(name, par_list, body):
                ast_node.dotnum = self.add_node(name)
                if par_list:
                    self.build_graph(par_list)
                    self.add_edge(ast_node.dotnum, par_list.dotnum)
                if body:
                    self.build_graph(body)
                    self.add_edge(ast_node.dotnum, body.dotnum)
            case AST.Parameter(type, name):
                ast_node.dotnum = self.add_node("param")
                tmp_dotnum = self.add_node(type)
                tmp_dotnum2 = self.add_node(name)
                self.add_edge(ast_node.dotnum, tmp_dotnum)
                self.add_edge(ast_node.dotnum, tmp_dotnum2)
            case AST.ParameterList(param, next):
                self.build_graph(param)
                ast_node.dotnum = self.add_node("param_list")
                self.add_edge(ast_node.dotnum, param.dotnum)
                if next:
                    self.build_graph(next)
                    self.add_edge(ast_node.dotnum, next.dotnum)
            case AST.StatementList(stm, next):
                ast_node.dotnum = self.add_node("stm_list")
                self.build_graph(stm)
                self.add_edge(ast_node.dotnum, stm.dotnum)
                if next:
                    self.build_graph(next)
                    self.add_edge(ast_node.dotnum, next.dotnum)
            case AST.StatementAssignment(lhs, rhs):
                self.build_graph(rhs)
                ast_node.dotnum = self.add_node("=")
                tmp_dotnum = self.add_node(lhs)
                self.add_edge(ast_node.dotnum, tmp_dotnum)
                self.add_edge(ast_node.dotnum, rhs.dotnum)
            case AST.StatementIfthenelse(exp, then_part, else_part):
                self.build_graph(exp)
                self.build_graph(then_part)
                ast_node.dotnum = self.add_node("if")
                if else_part:
                    self.build_graph(else_part)
                    self.add_edge(ast_node.dotnum, else_part.dotnum)
                self.add_edge(ast_node.dotnum, exp.dotnum)
                self.add_edge(ast_node.dotnum, then_part.dotnum)
            case AST.StatementWhile(exp, body):
                self.build_graph(exp)
                self.build_graph(body)
                ast_node.dotnum = self.add_node("while")
                self.add_edge(ast_node.dotnum, exp.dotnum)
                self.add_edge(ast_node.dotnum, body.dotnum)
            case AST.StatementFor(iter, exp, assign, body):
                self.build_graph(iter)
                self.build_graph(exp)
                self.build_graph(assign)
                self.build_graph(body)
                ast_node.dotnum = self.add_node("for")
                self.add_edge(ast_node.dotnum, iter.dotnum)
                self.add_edge(ast_node.dotnum, exp.dotnum)
                self.add_edge(ast_node.dotnum, assign.dotnum)
                self.add_edge(ast_node.dotnum, body.dotnum)
            case AST.StatementPrint(exp):
                self.build_graph(exp)
                ast_node.dotnum = self.add_node("print")
                self.add_edge(ast_node.dotnum, exp.dotnum)
            case AST.StatementReturn(exp):
                self.build_graph(exp)
                ast_node.dotnum = self.add_node("return")
                self.add_edge(ast_node.dotnum, exp.dotnum)
            case AST.ExpressionIdentifier(identifier):
                ast_node.dotnum = self.add_node(identifier)
            case AST.ExpressionInteger(integer):
                ast_node.dotnum = self.add_node(str(integer))
            case AST.ExpressionFloat(float):
                ast_node.dotnum = self.add_node(str(float))
            case AST.ExpressionBinop(op, lhs, rhs):
                self.build_graph(lhs)
                self.build_graph(rhs)
                ast_node.dotnum = self.add_node(op)
                self.add_edge(ast_node.dotnum, lhs.dotnum)
                self.add_edge(ast_node.dotnum, rhs.dotnum)
            case AST.ExpressionCall(name, body):
                ast_node.dotnum = self.add_node("call " + name)
                if body:
                    self.build_graph(body)
                    self.add_edge(ast_node.dotnum, body.dotnum)
            case AST.ExpressionList(exp, next):
                self.build_graph(exp)
                ast_node.dotnum = self.add_node("expr_list")
                self.add_edge(ast_node.dotnum, exp.dotnum)
                if next:
                    self.build_graph(next)
                    self.add_edge(ast_node.dotnum, next.dotnum)
            case _:
                raise ValueError(f"Unrecognized node: {ast_node}")
