import copy
from collections import defaultdict

from src.dataclass.iloc import Instruction, Operand, Target
from src.enums.code_generation_enum import Op, T


class Allocator:
    """ This class is responsible for performing control flow analysis, 
        constructing an interference graph, graph coloring and assigning 
        colors to instructions.

        The API exposes `perform_register_allocation`.
    """

    _labels: dict = {}

    def _find_labels(self, code: list) -> None:
        i = 0
        length_instructions = len(code)
        while (i < length_instructions):
            instruction = code[i]
            match instruction:
                case list():
                    self._find_labels(instruction)
                case Instruction(opcode=Op.LABEL, args=(Operand(target=Target(val=label)), )):
                    j = i + 1
                    succ_instruction = None
                    while (j < length_instructions):
                        ins = code[j]
                        match ins:
                            case Instruction(args=(Operand(target=Target(spec=T.REG)), Operand())):
                                succ_instruction = ins
                                break
                            case Instruction(args=(Operand(), Operand(target=Target(spec=T.REG)))):
                                succ_instruction = ins
                                break
                            case Instruction(args=(Operand(target=Target(spec=T.REG)), )):
                                succ_instruction = ins
                                break
                        j += 1
                    self._labels[label] = succ_instruction
            i += 1

    def _control_flow(self, code: list) -> None:
        def setup_linking(before, instruction: Instruction) -> None:
            if before:
                instruction.pred.append(before)
                before.succ.append(instruction)

        for ins in code:
            match ins:
                case list():
                    self._control_flow(ins)
                case _:
                    ins.pred = []
                    ins.succ = []
                    ins.in_ = set()
                    ins.out = set()
                    ins.in_prime = set()
                    ins.out_prime = set()

        before = None
        for ins in code:
            match ins:
                case Instruction(args=(Operand(target=Target(spec=T.REG)), Operand())):
                    setup_linking(before, ins)
                    before = ins
                case Instruction(args=(Operand(), Operand(target=Target(spec=T.REG)))):
                    setup_linking(before, ins)
                    before = ins
                case Instruction(args=(Operand(target=Target(spec=T.REG)), )):
                    setup_linking(before, ins)
                    before = ins
                case Instruction(opcode=op, args=(Operand(target=Target(val=label)), )) if op in [Op.JE, Op.JNE, Op.JL, Op.JG, Op.JGE, Op.JLE, Op.JMP]:
                    node = self._labels[label]
                    if node is not None:
                        before.succ.append(node)
                        node.pred.append(before)

    def _live_set_changed_and_out_calc(self, ins: Instruction) -> bool:
        change = None

        for node in ins.succ:
            ins.out = ins.out.union(node.in_)

        if ins.in_prime == ins.in_ and ins.out_prime == ins.out:
            change = False
        else:
            change = True

        ins.in_prime = set(ins.in_)
        ins.out_prime = set(ins.out)

        return change

    def _do_set_calc(self, ins: Instruction or list) -> bool:
        matched = None
        match ins:
            case list():
                self._liveness_analysis(ins)
            case Instruction(opcode=Op.MOVE, args=(op, Operand(target=Target(spec=T.REG, val=val_def)))):
                match op:
                    case Operand(target=Target(spec=T.REG, val=val_use)):
                        ins.in_.add(val_use)
                        ins.in_ = ins.in_.union(ins.out - {val_def})
                    case _:
                        ins.in_ = ins.in_.union(ins.out - {val_def})

                matched = ins
            case Instruction(opcode=op, args=(Operand(target=Target(spec=T.REG, val=val1)),
                                              Operand(target=Target(spec=T.REG, val=val2)))) if op in [Op.ADD, Op.SUB, Op.DIV, Op.MUL]:
                ins.in_.add(val1)
                ins.in_.add(val2)
                ins.in_ = ins.in_.union(ins.out - {val2})
                matched = ins
            case Instruction(args=(Operand(target=Target(spec=T.REG, val=val1)),
                                   Operand(target=Target(spec=T.REG, val=val2)))):
                ins.in_.add(val1)
                ins.in_.add(val2)
                ins.in_ = ins.in_.union(ins.out)
                matched = ins
            case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), Operand())):
                ins.in_.add(val)
                ins.in_.union(ins.out)
                matched = ins
            case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), )):
                ins.in_.add(val)
                ins.in_ = ins.in_.union(ins.out)
                matched = ins

        if matched:
            return self._live_set_changed_and_out_calc(matched)

    def _liveness_analysis(self, code: list) -> None:
        change = True

        while (change):
            change = False

            for ins in reversed(code):
                if self._do_set_calc(ins):
                    change = True

    def _build_graph(self, code: list, graphs: list[defaultdict] = None) -> list[defaultdict]:
        graph = {}

        if graphs is None:
            graphs = []

        for ins in code:
            node = None
            
            match ins:
                case list():
                    self._build_graph(ins, graphs)
                case Instruction(args=(Operand(target=Target(spec=T.REG)), Operand())):
                    node = ins
                case Instruction(args=(Operand(), Operand(target=Target(spec=T.REG)))):
                    node = ins
                case Instruction(args=(Operand(target=Target(spec=T.REG)), )):
                    node = ins

            if node:
                for i in node.in_:
                    if i not in graph:
                        graph[i] = set()
                    for j in node.in_:
                        if i == j:
                            continue
                        graph[i].add(j)

        graphs.append(graph)

        return graphs

    def _remove_node_from_graph(self, graph: defaultdict, node: int) -> None:
        for k in graph:
            adj = graph[k]
            if node in adj:
                adj.remove(node)

        graph.pop(node)

    def _take_graph_apart(self, graph: defaultdict) -> list:
        stack = []

        while (graph):
            found = None
            for node, adj in graph.items():
                if len(adj) < 10:
                    found = (node, set(adj))
                    break

            if not found:
                # Pick random
                found = list(graph.items())[0]

            stack.append(found)
            self._remove_node_from_graph(graph, found[0])

        return stack

    def _assign_colors(self, stack: list, colors: dict) -> dict:
        graph = defaultdict(set)

        for node, adj in reversed(stack):
            graph[node] = adj
            for adj_node in adj:
                graph[adj_node].add(node)

            adj_colors = set()
            for i in adj:
                color = colors[i]

                if color is None:
                    continue

                adj_colors.add(color)

            i = 0
            while (i := i + 1):
                if i in adj_colors:
                    continue
                else:
                    colors[node] = i
                    break

    def _color_graph(self, graphs: list[defaultdict]) -> dict[int, int]:
        colors = defaultdict(lambda: None)

        for graph in graphs:
            stack = self._take_graph_apart(graph)
            self._assign_colors(stack, colors)

        return colors

    def _rename_registers(self, colors: dict, code: list) -> None:
        for ins in code:
            match ins:
                case Instruction(args=(Operand(target=Target(spec=T.REG, val=val1)), Operand(target=Target(spec=T.REG, val=val2)))):
                    ins.args[0].target.val = colors[val1]
                    ins.args[1].target.val = colors[val2]
                case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), Operand())):
                    ins.args[0].target.val = colors[val]
                case Instruction(args=(Operand(), Operand(target=Target(spec=T.REG, val=val)))):
                    ins.args[1].target.val = colors[val]
                case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), )):
                    ins.args[0].target.val = colors[val]

    def _flatmap(self, code, acc: list = None) -> list[Instruction]:
        if acc is None:
            acc = []

        for ins in code:
            if isinstance(ins, list):
                self._flatmap(ins, acc)
            else:
                acc.append(ins)
        return acc

    def perform_register_allocation(self, code: list[Instruction]) -> list[Instruction]:
        """ This method is responsible for orchestrating the total allocation flow. 
            The method calls a selection of hidden methods, so that it is finally 
            possible to return a list of instructions with correctly assigned registers,
            such that the rest can be handled by emit.

                1. find labels
                2. do control flow
                3. perform liveness
                4. build graph
                5. color graph
                6. flatmap code
                7. assign colors to instructions
            
            Parameters
            ----------
            code : list[Instruction]

            Returns
            -------
            code : list[instructions]
        """

        code = copy.deepcopy(code) # input is left untouched

        self._find_labels(code)
        self._control_flow(code)
        self._liveness_analysis(code)
        graph = self._build_graph(code)
        colors = self._color_graph(graph)
        code = self._flatmap(code)
        self._rename_registers(colors, code)

        return code
