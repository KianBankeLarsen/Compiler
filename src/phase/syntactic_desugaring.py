from __future__ import annotations

import copy
from dataclasses import dataclass

import src.dataclass.AST as AST


@dataclass
class ASTSyntacticDesugar:
    """This phase is created as a consequence of the 
        way the input is parsed. It is necessary to rewrite 
        the syntactic sugar used when writing
        `<type><name>=<exp>` to statements, 
        otherwise the code generation will not work.

    The API exposes `desugar_AST` which takes an IR as actual parameter.
    """

    def _collect_decl_var_init(self, decls_arg: AST.DeclarationList) -> list[AST.DeclarationVariableInit]:
        acc = []

        if decls_arg is None:
            return acc

        while (decl := decls_arg.decl):
            if isinstance(decl, AST.DeclarationVariableInit):
                acc.append(decl)

            if decls_arg.next is None:
                break

            decls_arg = decls_arg.next

        return acc

    def _trans_var_init_list_to_stm(self, init_list: list[AST.DeclarationVariableInit]) -> AST.StatementList:
        top_node = None

        if init_list:
            var = init_list.pop(0)
            top_node = AST.StatementList(
                AST.StatementAssignment(var.name, var.exp, -1),
                None,
                -1
            )

        stm_list = top_node
        for var in init_list:
            stm_list.next = AST.StatementList(
                AST.StatementAssignment(var.name, var.exp, -1),
                None,
                -1
            )
            stm_list = stm_list.next

        return top_node

    def _insert_stm(self, assignments: AST.StatementList, ast_node: AST.Body) -> None:
        if not assignments:
            return

        top_node = assignments
        second_last_node = assignments

        while (assignments := assignments.next):
            second_last_node = assignments

        second_last_node.next = ast_node.stm_list
        ast_node.stm_list = top_node

    def desugar_AST(self, ast_node: AST.AstNode) -> AST.AstNode:
        """Perform deep copy of provided IR before desugaring.

        Returns new desugared IR/AST.
        """

        ast_node = copy.deepcopy(ast_node)
        self._desugar_AST(ast_node)
        return ast_node

    def _desugar_AST(self, ast_node: AST.AstNode) -> None:
        match ast_node:
            case AST.Body(decls):
                self._desugar_AST(decls)
                decl_var_init_list = self._collect_decl_var_init(decls)
                assignments = self._trans_var_init_list_to_stm(
                    decl_var_init_list)
                self._insert_stm(assignments, ast_node)
                self._desugar_AST(ast_node.stm_list)
            case AST.DeclarationList(decl, next):
                self._desugar_AST(decl)
                self._desugar_AST(next)
            case AST.DeclarationFunction(_, func):
                self._desugar_AST(func)
            case AST.Function(body=body):
                self._desugar_AST(body)
            case AST.StatementList(stm, next):
                self._desugar_AST(stm)
                self._desugar_AST(next)
            case AST.StatementIfthenelse(_, then_part, else_part):
                self._desugar_AST(then_part)
                self._desugar_AST(else_part)
            case AST.StatementWhile(_, body):
                self._desugar_AST(body)
            case AST.StatementFor(body=body):
                self._desugar_AST(body)
