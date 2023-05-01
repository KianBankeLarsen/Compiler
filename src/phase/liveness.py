from src.dataclass.iloc import Instruction, Operand, Target
from src.enums.code_generation_enum import Op, T
import copy

# if(3<5){int main(){}}else{}
# for(int i = 5; i < 6; i = i + 1){} 

class Liveness:
    _labels : dict = {}

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
                instruction.succ.append(before)
                before.pred.append(instruction)

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
                        before.pred.append(node)
                        node.succ.append(before)

    def _live_set_changed_and_out_calc(self, ins: Instruction) -> bool:
        change = None

        for node in ins.succ:
            ins.out.union(node.in_)

        if ins.in_prime == ins.in_ and ins.out_prime == ins.out:
            change = False
        else:
            change = True

        ins.in_prime = set(ins.in_)
        ins.out_prime = set(ins.out)

        return change

    def _do_set_calc(self, ins: Instruction or list) -> bool:
        match ins:
            case list():
                self._liveness_analysis(ins)
            case Instruction(opcode=Op.MOVE, args=(op, Operand(target=Target(spec=T.REG, val=val_def)))):
                match op:
                    case Operand(target=Target(spec=T.REG, val=val_use)):
                        ins.in_.add(val_use)
                        ins.in_.union(ins.out - {val_def})
                    case _:
                        ins.in_.union(ins.out - {val_def})
                
                return self._live_set_changed_and_out_calc(ins)
            case Instruction(opcode=op, args=(Operand(target=Target(spec=T.REG, val=val1)),
                                            Operand(target=Target(spec=T.REG, val=val2)))) if op in [Op.ADD, Op.SUB, Op.DIV, Op.MUL]:
                ins.in_.add(val1)
                ins.in_.add(val2)
                ins.in_.union(ins.out - {val2})

                return self._live_set_changed_and_out_calc(ins)
            case Instruction(args=(Operand(target=Target(spec=T.REG, val=val1)),
                                Operand(target=Target(spec=T.REG, val=val2)))):
                ins.in_.add(val1)
                ins.in_.add(val2)

                return self._live_set_changed_and_out_calc(ins)
            case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), Operand())):
                ins.in_.add(val)

                return self._live_set_changed_and_out_calc(ins)
            case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), )):                
                ins.in_.add(val)

                return self._live_set_changed_and_out_calc(ins)

    def _liveness_analysis(self, code: list) -> None:
        change = True

        while(change):
            change = False

            for ins in reversed(code):
                if self._do_set_calc(ins):
                    change = True

    def _make_interference_graph(self, code):
        for ins in code:
            match ins:
                case list():
                    self._make_interference_graph(ins)
                case Instruction(args=(Operand(target=Target(spec=T.REG)), Operand())):
                    print(ins, ins.in_)
                case Instruction(args=(Operand(), Operand(target=Target(spec=T.REG)))):
                    print(ins, ins.in_)
                case Instruction(args=(Operand(target=Target(spec=T.REG)), )):
                    print(ins, ins.in_)

    def _color_interference_graph(self):
        pass

    def perform_register_allocation(self, code: list) -> dict[str, Instruction]:
        code = copy.deepcopy(code)

        self._find_labels(code)
        self._control_flow(code)
        self._liveness_analysis(code)
        self._make_interference_graph(code)
        self._color_interference_graph()
