class body:
    """
    """

    def __init__(self, variables_decl, functions_decl, stm_list, lineno):
        self.variables_decl = variables_decl
        self.functions_decl = functions_decl
        self.stm_list = stm_list
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.variables_decl:
            self.variables_decl.accept(visitor)
        visitor.preMidVisit(self)
        if self.functions_decl:
            self.functions_decl.accept(visitor)
        visitor.postMidVisit(self)
        self.stm_list.accept(visitor)
        visitor.postVisit(self)


class function:
    def __init__(self, name, par_list, body, lineno):
        self.name = name
        self.par_list = par_list
        self.body = body
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.par_list:
            self.par_list.accept(visitor)
        visitor.midVisit(self)
        self.body.accept(visitor)
        visitor.postVisit(self)


class statement_list:
    """
    """

    def __init__(self, stm, next_, lineno):
        self.stm = stm
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.stm.accept(visitor)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)


class statement_assignment:
    """
    """

    def __init__(self, lhs, rhs, lineno):
        self.lhs = lhs
        self.rhs = rhs
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.rhs.accept(visitor)
        visitor.postVisit(self)


class expression_integer:
    """
    """

    def __init__(self, i, lineno):
        self.integer = i
        self.lineno = lineno

    def accept(self, visitor):
        visitor.postVisit(self)


class expression_identifier:
    """
    """

    def __init__(self, identifier, lineno):
        self.identifier = identifier
        self.lineno = lineno

    def accept(self, visitor):
        visitor.postVisit(self)


class expression_binop:
    """
    """

    def __init__(self, op, lhs, rhs, lineno):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.lhs.accept(visitor)
        visitor.midVisit(self)
        self.rhs.accept(visitor)
        visitor.postVisit(self)
