from dataclasses import dataclass

from src.dataclass.iloc import Instruction, Operand, Target
from src.enums.code_generation_enum import Op, T

# if(3<5){int main(){}}else{}

@dataclass
class Liveness:
    def perform_liveness_analysis(self, code: list):
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
                        while(j < length_instructions):
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
            for i in code:
                match i:
                    case list():
                        control_flow(i)
                    case Instruction(args=(Operand(target=Target(spec=T.REG)), Operand())):
                        break
                    case Instruction(args=(Operand(), Operand(target=Target(spec=T.REG)))):
                        pass
                    case Instruction(args=(Operand(target=Target(spec=T.REG)), )):
                        pass

        find_labels(code)
        control_flow(code)
