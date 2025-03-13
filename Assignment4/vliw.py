class VLIW:
    def __init__(self, instructions):
        self.clock = 1
        self.execution_unit = {
            "iadd" : {"busy" : False, "arrival_cc" : 0, "execution_cc": 6, "remaining_exec_time" : 0, "instruction": None, "op" : None},
            "imul" : {"busy" : False, "arrival_cc" : 0, "execution_cc": 12, "remaining_exec_time" : 0, "instruction": None, "op" : None},
            "fadd" : {"busy" : False, "arrival_cc" : 0, "execution_cc": 18, "remaining_exec_time" : 0, "instruction": None, "op" : None},
            "fmul" : {"busy" : False, "arrival_cc" : 0, "execution_cc": 30, "remaining_exec_time" : 0, "instruction": None, "op" : None},
            "ld" : {"busy" : False, "arrival_cc" : 0, "execution_cc": 1, "remaining_exec_time" : 0, "instruction": None, "op" : None},
            "st" : {"busy" : False, "arrival_cc" : 0, "execution_cc": 1, "remaining_exec_time" : 0, "instruction": None, "op" : None},
            "lu" : {"busy" : False, "arrival_cc" : 0, "execution_cc": 1, "remaining_exec_time" : 0, "instruction": None, "op" : None},
        }

        self.instructions = instructions

    
    def issue(self):
        for key in list(self.execution_unit.keys()):
            if self.execution_unit[key]["busy"] == True:
                return False
        
        self.read_dependencies = set()
        self.write_dependencies = set()
        instructions_copy = self.instructions[:]
        for instruction in instructions_copy:
            instruction_split = instruction.split()
            if instruction_split[0] == 'ld' and instruction_split[1] not in self.read_dependencies and self.execution_unit[instruction_split[0]]["busy"] == False:
                self.execution_unit[instruction_split[0]]["instruction"] = instruction_split
                self.execution_unit[instruction_split[0]]["busy"] = True
                self.execution_unit[instruction_split[0]]["arrival_cc"] = self.clock
                self.execution_unit[instruction_split[0]]["remaining_exec_time"] = self.execution_unit[instruction_split[0]]["execution_cc"]
                self.instructions.remove(instruction)
            elif instruction_split[0] == 'st' and instruction_split[1] not in self.write_dependencies and self.execution_unit[instruction_split[0]]["busy"] == False:
                self.execution_unit[instruction_split[0]]["instruction"] = instruction_split
                self.execution_unit[instruction_split[0]]["busy"] = True
                self.execution_unit[instruction_split[0]]["arrival_cc"] = self.clock
                self.execution_unit[instruction_split[0]]["remaining_exec_time"] = self.execution_unit[instruction_split[0]]["execution_cc"]
                self.instructions.remove(instruction)
            elif (instruction_split[0] == 'iadd' or instruction_split[0] =='imul' or instruction_split[0] == 'fadd' or instruction_split[0] == 'fmul') and instruction_split[1] not in self.read_dependencies and self.execution_unit[instruction_split[0]]["busy"] == False and instruction_split[2] not in self.write_dependencies and instruction_split[3] not in self.write_dependencies:
                self.execution_unit[instruction_split[0]]["instruction"] = instruction_split
                self.execution_unit[instruction_split[0]]["busy"] = True
                self.execution_unit[instruction_split[0]]["arrival_cc"] = self.clock
                self.execution_unit[instruction_split[0]]["remaining_exec_time"] = self.execution_unit[instruction_split[0]]["execution_cc"]
                self.instructions.remove(instruction)

            elif instruction_split[0] == 'lu' and instruction_split[1] not in self.read_dependencies and self.execution_unit[instruction_split[0]]["busy"] == False and instruction_split[2] not in self.write_dependencies and instruction_split[3] not in self.write_dependencies:
                self.execution_unit[instruction_split[0]]["instruction"] = instruction_split
                self.execution_unit[instruction_split[0]]["busy"] = True
                self.execution_unit[instruction_split[0]]["arrival_cc"] = self.clock
                self.execution_unit[instruction_split[0]]["remaining_exec_time"] = self.execution_unit[instruction_split[0]]["execution_cc"]
                self.instructions.remove(instruction)

            self.write_dependencies.add(instruction_split[1])
            self.read_dependencies.add(instruction_split[2])
            if(len(instruction_split) == 4):
                self.read_dependencies.add(instruction_split[3])
        
        for key in list(self.execution_unit.keys()):
            if self.execution_unit[key]["busy"] == False:
                self.execution_unit[key]["op"] = 'NOP'
                self.execution_unit[key]["instruction"] = ['NOP']
                self.execution_unit[key]["remaining_exec_time"] = 1
                self.execution_unit[key]["busy"] = True
                self.execution_unit[key]["arrival_cc"] = self.clock
        
        return True

    def execute(self):
        tag = self.issue()
        if tag == False:
            for key in list(self.execution_unit.keys()):
                if self.execution_unit[key]["busy"] == True:
                    self.execution_unit[key]["remaining_exec_time"] -= 1
                    if self.execution_unit[key]["remaining_exec_time"] == 0:
                        self.execution_unit[key]["busy"] = False
                        self.execution_unit[key]["remaining_exec_time"] = 0
                        self.execution_unit[key]["op"] = "NOP"
                        self.execution_unit[key]["instruction"] = ['NOP']

        self.print_status()
        self.clock += 1
    
    def print_status(self):
        print(f'Clock cycle: {self.clock}')
        print(f'Issued at CC : {self.execution_unit["iadd"]["arrival_cc"]} Instruction: {self.execution_unit["iadd"]["instruction"]} Remaining Execution : {self.execution_unit["iadd"]["remaining_exec_time"]}')
        print(f'Issued at CC : {self.execution_unit["imul"]["arrival_cc"]} Instruction: {self.execution_unit["imul"]["instruction"]} Remaining Execution : {self.execution_unit["imul"]["remaining_exec_time"]}')
        print(f'Issued at CC : {self.execution_unit["fadd"]["arrival_cc"]} Instruction: {self.execution_unit["fadd"]["instruction"]} Remaining Execution : {self.execution_unit["fadd"]["remaining_exec_time"]}')
        print(f'Issued at CC : {self.execution_unit["fmul"]["arrival_cc"]} Instruction: {self.execution_unit["fmul"]["instruction"]} Remaining Execution : {self.execution_unit["fmul"]["remaining_exec_time"]}')
        print(f'Issued at CC : {self.execution_unit["ld"]["arrival_cc"]} Instruction: {self.execution_unit["ld"]["instruction"]} Remaining Execution : {self.execution_unit["ld"]["remaining_exec_time"]}')
        print(f'Issued at CC : {self.execution_unit["st"]["arrival_cc"]} Instruction: {self.execution_unit["st"]["instruction"]} Remaining Execution : {self.execution_unit["st"]["remaining_exec_time"]}')
        print(f'Issued at CC : {self.execution_unit["lu"]["arrival_cc"]} Instruction: {self.execution_unit["lu"]["instruction"]} Remaining Execution : {self.execution_unit["lu"]["remaining_exec_time"]}')
    
    def any_unit_busy(self):
        for key in self.execution_unit:
            if self.execution_unit[key]["busy"]:
                return True
        return False
    
    def run(self):
        while len(self.instructions) > 0 or self.any_unit_busy():
            self.execute()
        
        print("\nFinal status:")
        self.print_status()
        print(f'Total clock cycles: {self.clock - 1}')


with open('instructions.txt', 'r') as file:
    instructions = [line.strip() for line in file.readlines()]
vliw = VLIW(instructions)
vliw.run()