class VisitorsBase:
    """
    """

    def _visit(self, t, s):
        method_name = s + "_" + type(t).__name__
        visitor = getattr(self, method_name, None)
        if visitor:
            visitor(t)

    def preVisit(self, t):
        self._visit(t, "preVisit")

    def preMidVisit(self, t):
        self._visit(t, "preMidVisit")

    def midVisit(self, t):
        self._visit(t, "midVisit")

    def postMidVisit(self, t):
        self._visit(t, "postMidVisit")

    def postVisit(self, t):
        self._visit(t, "postVisit")
