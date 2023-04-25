from src.dataclass.iloc import Instruction, Operand, Target
from src.enums.code_generation_enum import Op, T
import copy

# if(3<5){int main(){}}else{}
# for(int i = 5; i < 6; i = i + 1){} 

class Liveness:
    def perform_liveness_analysis(self, code: list) -> dict[str, Instruction]:
        code = copy.deepcopy(code)
        labels = {}

        def find_labels(code: list):
            i = 0
            length_instructions = len(code)
            while (i < length_instructions):
                instruction = code[i]
                match instruction:
                    case list():
                        find_labels(instruction)
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
                        labels[label] = succ_instruction
                i += 1


        def control_flow(code: list):
            def setup_linking(before, instruction):
                if before:
                    instruction.succ.append(before)
                    before.pred.append(instruction)
                instruction.in_ = {}
                instruction.out = {}

            for i in code:
                match i:
                    case list():
                        control_flow(i)
                    case _:
                        i.pred = []
                        i.succ = []

            before = None
            for i in code:
                match i:
                    case Instruction(args=(Operand(target=Target(spec=T.REG)), Operand())):
                        setup_linking(before, i)
                        before = i
                    case Instruction(args=(Operand(), Operand(target=Target(spec=T.REG)))):
                        setup_linking(before, i)
                        before = i
                    case Instruction(args=(Operand(target=Target(spec=T.REG)), )):
                        setup_linking(before, i)
                        before = i
                    case Instruction(opcode=op, args=(Operand(target=Target(val=label)), )) if op in [Op.JE, Op.JNE, Op.JL, Op.JG, Op.JGE, Op.JLE, Op.JMP]:
                        node = labels[label]
                        if node is not None:
                            before.pred.append(node)
                            node.succ.append(before)


        def liveness(code: list):
            for i in code:
                match i:
                    case list():
                        #control_flow(i)
                        pass
                    case Instruction(opcode=Op.MOVE, args=(op, Operand(target=Target(spec=T.REG, val=val)))):
                        print(val, "def")
                        match op:
                            case Operand(target=Target(spec=T.REG, val=val)):
                                print(val, "use")
                    case Instruction(opcode=op, args=(Operand(target=Target(spec=T.REG, val=val1)),
                                                      Operand(target=Target(spec=T.REG, val=val2)))) if op in [Op.ADD, Op.SUB, Op.DIV, Op.MUL]:
                        print(val1, "use")
                        print(val2, "use")
                        print(val2, "def")
                    case Instruction(args=(Operand(target=Target(spec=T.REG, val=val1)),
                                           Operand(target=Target(spec=T.REG, val=val2)))):
                        print(val1, "use")
                        print(val2, "use")
                    case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), Operand())):
                        print(val, "use")
                    case Instruction(args=(Operand(target=Target(spec=T.REG, val=val)), )):
                        print(val, "use")
                    case Instruction(args=(Operand(target=Target(spec=T.REG)), _)):
                        raise ValueError(i)
                    case Instruction(args=(_, Operand(target=Target(spec=T.REG)))):
                        raise ValueError(i)
                    case Instruction(args=(Operand(target=Target(spec=T.REG)), )):
                        raise ValueError(i)

        find_labels(code)
        control_flow(code)
        liveness(code)