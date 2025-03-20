from time import sleep

class Tomasulo:
    def __init__(self, instructions):
        self.instructions = instructions
        self.clock = 1
        self.count = 0

        self.read_dependencies = set()
        self.write_dependencies = set()

        self.instruction_status = {
            f"i{i}": {"issue": None, "execution_completion": None, "write_result": None, "remaining_exec_time": None}
            for i in range(len(self.instructions))
        }

        self.iadd_units = 3
        self.imul_units = 2
        self.fadd_units = 3
        self.fmul_units = 2
        self.load_store_units = 3
        self.logic_units = 3

        self.arithmetic_reservation_station = {
            f"iadd{i}": {"busy": False, "op": None, "vj": None, "vk": None, "qj": None, "qk": None, "dest": None ,"instruction": None}
            for i in range(self.iadd_units)
        }
        self.arithmetic_reservation_station.update({
            f"imul{i}": {"busy": False, "op": None, "vj": None, "vk": None, "qj": None, "qk": None, "dest": None ,"instruction": None}
            for i in range(self.imul_units)
        })
        self.arithmetic_reservation_station.update({
            f"fadd{i}": {"busy": False, "op": None, "vj": None, "vk": None, "qj": None, "qk": None, "dest": None , "instruction": None}
            for i in range(self.fadd_units)
        })
        self.arithmetic_reservation_station.update({
            f"fmul{i}": {"busy": False, "op": None, "vj": None, "vk": None, "qj": None, "qk": None, "dest": None, "instruction": None}
            for i in range(self.fmul_units)
        })
        self.arithmetic_reservation_station.update({
            f"logic{i}": {"busy": False, "op": None, "vj": None, "vk": None, "qj": None, "qk": None, "dest": None, "instruction": None}
            for i in range(self.logic_units)
        })

        self.memory_reservation_station = {
            f"load{i}": {"busy": False, "address": None, "dest": None,"instruction": None}
            for i in range(self.load_store_units)
        }

        self.register_file = {
            "r0": {"busy": None, "value": None , "used_by": None},
            "r1": {"busy": None, "value": None , "used_by": None},
            "r2": {"busy": None, "value": None , "used_by": None},
            "r3": {"busy": None, "value": None , "used_by": None},
            "r4": {"busy": None, "value": None , "used_by": None},
            "r5": {"busy": None, "value": None , "used_by": None},
            "r6": {"busy": None, "value": None , "used_by": None},
            "r7": {"busy": None, "value": None , "used_by": None},
            "r8": {"busy": None, "value": None , "used_by": None},
            "r9": {"busy": None, "value": None , "used_by": None},
            "r10": {"busy": None, "value": None , "used_by": None},
            "r11": {"busy": None, "value": None , "used_by": None},
            "r12": {"busy": None, "value": None , "used_by": None},
            "r13": {"busy": None, "value": None , "used_by": None},
            "r14": {"busy": None, "value": None , "used_by": None},
            "r15": {"busy": None, "value": None , "used_by": None},
            "r16": {"busy": None, "value": None , "used_by": None},
            "r17": {"busy": None, "value": None , "used_by": None},
            "r18": {"busy": None, "value": None , "used_by": None},
            "r19": {"busy": None, "value": None , "used_by": None},
            "r20": {"busy": None, "value": None , "used_by": None},
            "r21": {"busy": None, "value": None , "used_by": None},
            "r22": {"busy": None, "value": None , "used_by": None},
            "r23": {"busy": None, "value": None , "used_by": None},
            "r24": {"busy": None, "value": None , "used_by": None},
            "r25": {"busy": None, "value": None , "used_by": None},
            "r26": {"busy": None, "value": None , "used_by": None},
            "r27": {"busy": None, "value": None , "used_by": None},
            "r28": {"busy": None, "value": None , "used_by": None},
            "r29": {"busy": None, "value": None , "used_by": None},
            "r30": {"busy": None, "value": None , "used_by": None},
            "r31": {"busy": None, "value": None , "used_by": None}
        }
        self.instructions_copy = self.instructions[:]

    def rename(self, register):
        for i in range(32):
            if not self.register_file[f"r{i}"]["busy"]:
                new_name = f"r{i}"
                self.register_file[f"r{i}"]["busy"] = True
                self.register_file[f"r{i}"]["value"] = self.register_file[register]["value"]
                self.register_file[f"r{i}"]["used_by"] = None

                for j in range(len(self.instructions)):
                    self.instructions[j] = self.instructions[j].replace(register, new_name)
                self.instructions_copy = self.instructions[:]
                return f"r{i}"

    def issue(self):
        self.instructions_copy = self.instructions[:]
        dependency = []
        for instruction in self.instructions_copy:
            if instruction == ' ':
                continue
            instruction_split = instruction.split()
            if instruction_split[1] in dependency:
                continue
            dependency.append(instruction_split[1])
            if instruction_split[0] == 'iadd':
                for i in range(self.iadd_units):
                    if not self.arithmetic_reservation_station[f"iadd{i}"]["busy"]:
                        self.arithmetic_reservation_station[f"iadd{i}"]["busy"] = True
                        self.arithmetic_reservation_station[f"iadd{i}"]["op"] = instruction_split[0]
                        if self.register_file[instruction_split[2]]["busy"]:
                            self.arithmetic_reservation_station[f"iadd{i}"]["qj"] = instruction_split[2]
                        else:
                            self.arithmetic_reservation_station[f"iadd{i}"]["vj"] = self.register_file[instruction_split[2]]["value"]

                        if self.register_file[instruction_split[3]]["busy"]:
                            self.arithmetic_reservation_station[f"iadd{i}"]["qk"] = instruction_split[3]
                        else:
                            self.arithmetic_reservation_station[f"iadd{i}"]["vk"] = self.register_file[instruction_split[3]]["value"]
                        if self.register_file[instruction_split[1]]["busy"]:
                            new_name = self.rename(instruction_split[1])
                            instruction = instruction.replace(instruction_split[1], new_name)
                            self.arithmetic_reservation_station[f"iadd{i}"]["dest"] = new_name
                            self.write_dependencies.add(new_name)
                        else:
                            self.arithmetic_reservation_station[f"iadd{i}"]["dest"] = instruction_split[1]
                            self.register_file[instruction_split[1]]["busy"] = True
                            self.write_dependencies.add(instruction_split[1])

                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["issue"] = self.clock
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["remaining_exec_time"] = 6
                        self.count+=1
                        self.arithmetic_reservation_station[f"iadd{i}"]["instruction"] = self.instructions.index(instruction)
                        p = self.instructions.index(instruction)
                        self.instructions[p] = ' '
                        self.register_file[self.arithmetic_reservation_station[f"iadd{i}"]["dest"]]["used_by"] = f"i{self.instructions_copy.index(instruction)}"
                        return
            elif instruction_split[0] == 'imul':
                for i in range(self.imul_units):
                    if not self.arithmetic_reservation_station[f"imul{i}"]["busy"]:
                        self.arithmetic_reservation_station[f"imul{i}"]["busy"] = True
                        self.arithmetic_reservation_station[f"imul{i}"]["op"] = instruction_split[0]
                        if self.register_file[instruction_split[2]]["busy"]:
                            self.arithmetic_reservation_station[f"imul{i}"]["qj"] = instruction_split[2]
                        else:
                            self.arithmetic_reservation_station[f"imul{i}"]["vj"] = self.register_file[instruction_split[2]]["value"]

                        if self.register_file[instruction_split[3]]["busy"]:
                            self.arithmetic_reservation_station[f"imul{i}"]["qk"] = instruction_split[3]
                        else:
                            self.arithmetic_reservation_station[f"imul{i}"]["vk"] = self.register_file[instruction_split[3]]["value"]

                        if self.register_file[instruction_split[1]]["busy"]:
                            new_name = self.rename(instruction_split[1])
                            instruction = instruction.replace(instruction_split[1], new_name)
                            self.arithmetic_reservation_station[f"imul{i}"]["dest"] = new_name
                            self.write_dependencies.add(new_name)
                        else:
                            self.arithmetic_reservation_station[f"imul{i}"]["dest"] = instruction_split[1]
                            self.register_file[instruction_split[1]]["busy"] = True
                            self.write_dependencies.add(instruction_split[1])

                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["issue"] = self.clock
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["remaining_exec_time"] = 12
                        self.count+=1
                        self.arithmetic_reservation_station[f"imul{i}"]["instruction"] = self.instructions.index(instruction)
                        p = self.instructions.index(instruction)
                        self.instructions[p] = ' '
                        self.register_file[self.arithmetic_reservation_station[f"imul{i}"]["dest"]]["used_by"] = f"i{self.instructions_copy.index(instruction)}"
                        return
            
            elif instruction_split[0] == 'fadd':
                for i in range(self.fadd_units):
                    if not self.arithmetic_reservation_station[f"fadd{i}"]["busy"]:
                        self.arithmetic_reservation_station[f"fadd{i}"]["busy"] = True
                        self.arithmetic_reservation_station[f"fadd{i}"]["op"] = instruction_split[0]
                        if self.register_file[instruction_split[2]]["busy"]:
                            self.arithmetic_reservation_station[f"fadd{i}"]["qj"] = instruction_split[2]
                        else:
                            self.arithmetic_reservation_station[f"fadd{i}"]["vj"] = self.register_file[instruction_split[2]]["value"]

                        if self.register_file[instruction_split[3]]["busy"]:
                            self.arithmetic_reservation_station[f"fadd{i}"]["qk"] = instruction_split[3]
                        else:
                            self.arithmetic_reservation_station[f"fadd{i}"]["vk"] = self.register_file[instruction_split[3]]["value"]

                        if self.register_file[instruction_split[1]]["busy"]:
                            new_name = self.rename(instruction_split[1])
                            instruction = instruction.replace(instruction_split[1], new_name)
                            self.arithmetic_reservation_station[f"fadd{i}"]["dest"] = new_name
                            self.write_dependencies.add(new_name)
                        else:
                            self.arithmetic_reservation_station[f"fadd{i}"]["dest"] = instruction_split[1]
                            self.register_file[instruction_split[1]]["busy"] = True
                            self.write_dependencies.add(instruction_split[1])

                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["issue"] = self.clock
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["remaining_exec_time"] = 18
                        self.count+=1
                        self.arithmetic_reservation_station[f"fadd{i}"]["instruction"] = self.instructions.index(instruction)
                        p = self.instructions.index(instruction)
                        self.instructions[p] = ' '
                        self.register_file[self.arithmetic_reservation_station[f"fadd{i}"]["dest"]]["used_by"] = f"i{self.instructions_copy.index(instruction)}"
                        return
            
            elif instruction_split[0] == 'fmul':
                for i in range(self.fmul_units):
                    if not self.arithmetic_reservation_station[f"fmul{i}"]["busy"]:
                        self.arithmetic_reservation_station[f"fmul{i}"]["busy"] = True
                        self.arithmetic_reservation_station[f"fmul{i}"]["op"] = instruction_split[0]
                        if self.register_file[instruction_split[2]]["busy"]:
                            self.arithmetic_reservation_station[f"fmul{i}"]["qj"] = instruction_split[2]
                        else:
                            self.arithmetic_reservation_station[f"fmul{i}"]["vj"] = self.register_file[instruction_split[2]]["value"]

                        if self.register_file[instruction_split[3]]["busy"]:
                            self.arithmetic_reservation_station[f"fmul{i}"]["qk"] = instruction_split[3]
                        else:
                            self.arithmetic_reservation_station[f"fmul{i}"]["vk"] = self.register_file[instruction_split[3]]["value"]

                        if self.register_file[instruction_split[1]]["busy"]:
                            new_name = self.rename(instruction_split[1])
                            instruction = instruction.replace(instruction_split[1], new_name)
                            self.arithmetic_reservation_station[f"fmul{i}"]["dest"] = new_name
                            self.write_dependencies.add(new_name)
                        else:
                            self.arithmetic_reservation_station[f"fmul{i}"]["dest"] = instruction_split[1]
                            self.register_file[instruction_split[1]]["busy"] = True
                            self.write_dependencies.add(instruction_split[1])

                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["issue"] = self.clock
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["remaining_exec_time"] = 30
                        self.count+=1
                        self.arithmetic_reservation_station[f"fmul{i}"]["instruction"] = self.instructions.index(instruction)
                        p = self.instructions.index(instruction)
                        self.instructions[p] = ' '
                        self.register_file[self.arithmetic_reservation_station[f"fmul{i}"]["dest"]]["used_by"] = f"i{self.instructions_copy.index(instruction)}"
                        return
            
            elif instruction_split[0] == 'lu':
                for i in range(self.logic_units):
                    if not self.arithmetic_reservation_station[f"logic{i}"]["busy"]:
                        self.arithmetic_reservation_station[f"logic{i}"]["busy"] = True
                        self.arithmetic_reservation_station[f"logic{i}"]["op"] = instruction_split[0]
                        if self.register_file[instruction_split[2]]["busy"]:
                            self.arithmetic_reservation_station[f"logic{i}"]["qj"] = instruction_split[2]
                        else:
                            self.arithmetic_reservation_station[f"logic{i}"]["vj"] = self.register_file[instruction_split[2]]["value"]

                        if self.register_file[instruction_split[3]]["busy"]:
                            self.arithmetic_reservation_station[f"logic{i}"]["qk"] = instruction_split[3]
                        else:
                            self.arithmetic_reservation_station[f"logic{i}"]["vk"] = self.register_file[instruction_split[3]]["value"]

                        if self.register_file[instruction_split[1]]["busy"]:
                            new_name = self.rename(instruction_split[1])
                            instruction = instruction.replace(instruction_split[1], new_name)
                            self.arithmetic_reservation_station[f"logic{i}"]["dest"] = new_name
                            self.write_dependencies.add(new_name)
                        else:
                            self.arithmetic_reservation_station[f"logic{i}"]["dest"] = instruction_split[1]
                            self.register_file[instruction_split[1]]["busy"] = True
                            self.write_dependencies.add(instruction_split[1])

                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["issue"] = self.clock
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["remaining_exec_time"] = 1
                        self.count+=1
                        self.arithmetic_reservation_station[f"logic{i}"]["instruction"] = self.instructions.index(instruction)
                        p = self.instructions.index(instruction)
                        self.instructions[p] = ' '
                        self.register_file[self.arithmetic_reservation_station[f"logic{i}"]["dest"]]["used_by"] = f"i{self.instructions_copy.index(instruction)}"
                        return

            
            elif instruction_split[0] == 'ld':
                for i in range(self.load_store_units):
                    if not self.memory_reservation_station[f"load{i}"]["busy"]:
                        self.memory_reservation_station[f"load{i}"]["busy"] = True
                        self.memory_reservation_station[f"load{i}"]["op"] = instruction_split[0]
                        if self.register_file[instruction_split[1]]["busy"]:
                            new_name = self.rename(instruction_split[1])
                            instruction = instruction.replace(instruction_split[1], new_name)
                            self.memory_reservation_station[f"load{i}"]["dest"] = new_name
                            self.write_dependencies.add(new_name)
                        else:
                            self.memory_reservation_station[f"load{i}"]["dest"] = instruction_split[1]
                            self.register_file[instruction_split[1]]["busy"] = True
                            self.write_dependencies.add(instruction_split[1])
                        self.memory_reservation_station[f"load{i}"]["address"] = instruction_split[2]
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["issue"] = self.clock
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["remaining_exec_time"] = 1
                        self.count+=1
                        self.memory_reservation_station[f"load{i}"]["instruction"] = self.instructions.index(instruction)
                        p = self.instructions.index(instruction)
                        self.instructions[p] = ' '
                        self.register_file[self.memory_reservation_station[f"load{i}"]["dest"]]["used_by"] = f"i{self.instructions_copy.index(instruction)}"
                        return
                    
            elif instruction_split[0] == "st":
                for i in range(self.load_store_units):
                    if not self.memory_reservation_station[f"load{i}"]["busy"]:
                        self.memory_reservation_station[f"load{i}"]["busy"] = True
                        self.memory_reservation_station[f"load{i}"]["op"] = instruction_split[0]
                        self.memory_reservation_station[f"load{i}"]["address"] = instruction_split[2]
                        self.memory_reservation_station[f"load{i}"]["dest"] = instruction_split[1]
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["issue"] = self.clock
                        self.instruction_status[f"i{self.instructions_copy.index(instruction)}"]["remaining_exec_time"] = 1
                        self.count+=1
                        self.memory_reservation_station[f"load{i}"]["instruction"] = self.instructions.index(instruction)
                        p = self.instructions.index(instruction)
                        self.instructions[p] = ' '
                        self.register_file[self.memory_reservation_station[f"load{i}"]["dest"]]["used_by"] = f"i{self.instructions_copy.index(instruction)}"
                        return
                    

    def execute(self):
        # Execute instructions in the execution units
        self.issue()
        self.clock += 1

        for i in range(self.load_store_units):
            if self.memory_reservation_station[f"load{i}"]["busy"]:
                if self.instruction_status[f"i{self.memory_reservation_station[f'load{i}']['instruction']}"]["remaining_exec_time"] == -1:
                    self.register_file[self.memory_reservation_station[f"load{i}"]["dest"]]["used_by"] = None
                    self.write_dependencies.remove(self.memory_reservation_station[f"load{i}"]["dest"]) if self.memory_reservation_station[f"load{i}"]["dest"] in self.write_dependencies else None
                    self.memory_reservation_station[f"load{i}"]["busy"] = False
                    self.memory_reservation_station[f"load{i}"]["address"] = None
                    self.memory_reservation_station[f"load{i}"]["dest"] = None
                    self.memory_reservation_station[f"load{i}"]["instruction"] = None
        
        for i in range(self.iadd_units):
            if self.arithmetic_reservation_station[f"iadd{i}"]["busy"]:
                if self.instruction_status[f"i{self.arithmetic_reservation_station[f'iadd{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.write_dependencies.remove(self.arithmetic_reservation_station[f"iadd{i}"]["dest"]) if self.arithmetic_reservation_station[f"iadd{i}"]["dest"] in self.write_dependencies else None
                        self.register_file[self.arithmetic_reservation_station[f"iadd{i}"]["dest"]]["used_by"] = None
                        self.arithmetic_reservation_station[f"iadd{i}"]["busy"] = False
                        self.arithmetic_reservation_station[f"iadd{i}"]["op"] = None
                        self.arithmetic_reservation_station[f"iadd{i}"]["vj"] = None
                        self.arithmetic_reservation_station[f"iadd{i}"]["vk"] = None
                        self.arithmetic_reservation_station[f"iadd{i}"]["qj"] = None
                        self.arithmetic_reservation_station[f"iadd{i}"]["qk"] = None
                        self.arithmetic_reservation_station[f"iadd{i}"]["dest"] = None
                        self.arithmetic_reservation_station[f"iadd{i}"]["instruction"] = None

        for i in range(self.imul_units):
            if self.arithmetic_reservation_station[f"imul{i}"]["busy"]:
                if self.instruction_status[f"i{self.arithmetic_reservation_station[f'imul{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.write_dependencies.remove(self.arithmetic_reservation_station[f"imul{i}"]["dest"]) if self.arithmetic_reservation_station[f"imul{i}"]["dest"] in self.write_dependencies else None
                        self.register_file[self.arithmetic_reservation_station[f"imul{i}"]["dest"]]["used_by"] = None
                        self.arithmetic_reservation_station[f"imul{i}"]["busy"] = False
                        self.arithmetic_reservation_station[f"imul{i}"]["op"] = None
                        self.arithmetic_reservation_station[f"imul{i}"]["vj"] = None
                        self.arithmetic_reservation_station[f"imul{i}"]["vk"] = None
                        self.arithmetic_reservation_station[f"imul{i}"]["qj"] = None
                        self.arithmetic_reservation_station[f"imul{i}"]["qk"] = None
                        self.arithmetic_reservation_station[f"imul{i}"]["dest"] = None
                        self.arithmetic_reservation_station[f"imul{i}"]["instruction"] = None
        
        for i in range(self.fadd_units):
            if self.arithmetic_reservation_station[f"fadd{i}"]["busy"]:
                if self.instruction_status[f"i{self.arithmetic_reservation_station[f'fadd{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.write_dependencies.remove(self.arithmetic_reservation_station[f"fadd{i}"]["dest"]) if self.arithmetic_reservation_station[f"fadd{i}"]["dest"] in self.write_dependencies else None
                        self.register_file[self.arithmetic_reservation_station[f"fadd{i}"]["dest"]]["used_by"] = None
                        self.arithmetic_reservation_station[f"fadd{i}"]["busy"] = False
                        self.arithmetic_reservation_station[f"fadd{i}"]["op"] = None
                        self.arithmetic_reservation_station[f"fadd{i}"]["vj"] = None
                        self.arithmetic_reservation_station[f"fadd{i}"]["vk"] = None
                        self.arithmetic_reservation_station[f"fadd{i}"]["qj"] = None
                        self.arithmetic_reservation_station[f"fadd{i}"]["qk"] = None
                        self.arithmetic_reservation_station[f"fadd{i}"]["dest"] = None
                        self.arithmetic_reservation_station[f"fadd{i}"]["instruction"] = None

        for i in range(self.fmul_units):
            if self.arithmetic_reservation_station[f"fmul{i}"]["busy"]:
                if self.instruction_status[f"i{self.arithmetic_reservation_station[f'fmul{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.write_dependencies.remove(self.arithmetic_reservation_station[f"fmul{i}"]["dest"]) if self.arithmetic_reservation_station[f"fmul{i}"]["dest"] in self.write_dependencies else None
                        self.register_file[self.arithmetic_reservation_station[f"fmul{i}"]["dest"]]["used_by"] = None
                        self.arithmetic_reservation_station[f"fmul{i}"]["busy"] = False
                        self.arithmetic_reservation_station[f"fmul{i}"]["op"] = None
                        self.arithmetic_reservation_station[f"fmul{i}"]["vj"] = None
                        self.arithmetic_reservation_station[f"fmul{i}"]["vk"] = None
                        self.arithmetic_reservation_station[f"fmul{i}"]["qj"] = None
                        self.arithmetic_reservation_station[f"fmul{i}"]["qk"] = None
                        self.arithmetic_reservation_station[f"fmul{i}"]["dest"] = None
                        self.arithmetic_reservation_station[f"fmul{i}"]["instruction"] = None
        
        for i in range(self.logic_units):
            if self.arithmetic_reservation_station[f"logic{i}"]["busy"]:
                if self.instruction_status[f"i{self.arithmetic_reservation_station[f'logic{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.write_dependencies.remove(self.arithmetic_reservation_station[f"logic{i}"]["dest"]) if self.arithmetic_reservation_station[f"logic{i}"]["dest"] in self.write_dependencies else None
                        self.register_file[self.arithmetic_reservation_station[f"logic{i}"]["dest"]]["used_by"] = None
                        self.arithmetic_reservation_station[f"logic{i}"]["busy"] = False
                        self.arithmetic_reservation_station[f"logic{i}"]["op"] = None
                        self.arithmetic_reservation_station[f"logic{i}"]["vj"] = None
                        self.arithmetic_reservation_station[f"logic{i}"]["vk"] = None
                        self.arithmetic_reservation_station[f"logic{i}"]["qj"] = None
                        self.arithmetic_reservation_station[f"logic{i}"]["qk"] = None
                        self.arithmetic_reservation_station[f"logic{i}"]["dest"] = None
                        self.arithmetic_reservation_station[f"logic{i}"]["instruction"] = None
                

        for i in range(self.load_store_units):
            if self.memory_reservation_station[f"load{i}"]["busy"]:
                if self.memory_reservation_station[f"load{i}"]["op"] == "st":
                    if self.memory_reservation_station[f"load{i}"]["dest"] in self.write_dependencies or self.register_file[self.memory_reservation_station[f"load{i}"]["dest"]]["used_by"]:
                        continue
                self.instruction_status[f"i{self.memory_reservation_station[f'load{i}']['instruction']}"]["remaining_exec_time"] -= 1
                if self.instruction_status[f"i{self.memory_reservation_station[f'load{i}']['instruction']}"]["remaining_exec_time"] == 0:
                    self.instruction_status[f"i{self.memory_reservation_station[f'load{i}']['instruction']}"]["execution_completion"] = self.clock
                if self.instruction_status[f"i{self.memory_reservation_station[f'load{i}']['instruction']}"]["remaining_exec_time"] == -1:
                    self.instruction_status[f"i{self.memory_reservation_station[f'load{i}']['instruction']}"]["write_result"] = self.clock

        for i in range(self.iadd_units):    
            if self.arithmetic_reservation_station[f"iadd{i}"]["busy"]:
                if self.arithmetic_reservation_station[f"iadd{i}"]["qj"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"iadd{i}"]["qj"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"iadd{i}"]["vj"] = self.register_file[self.arithmetic_reservation_station[f"iadd{i}"]["qj"]]["value"]
                        self.arithmetic_reservation_station[f"iadd{i}"]["qj"] = None
                if self.arithmetic_reservation_station[f"iadd{i}"]["qk"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"iadd{i}"]["qk"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"iadd{i}"]["vk"] = self.register_file[self.arithmetic_reservation_station[f"iadd{i}"]["qk"]]["value"]
                        self.arithmetic_reservation_station[f"iadd{i}"]["qk"] = None

                if self.arithmetic_reservation_station[f"iadd{i}"]["qj"] is None and self.arithmetic_reservation_station[f"iadd{i}"]["qk"] is None:
                    self.instruction_status[f"i{self.arithmetic_reservation_station[f'iadd{i}']['instruction']}"]["remaining_exec_time"] -= 1
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'iadd{i}']['instruction']}"]["remaining_exec_time"] == 0:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'iadd{i}']['instruction']}"]["execution_completion"] = self.clock
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'iadd{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'iadd{i}']['instruction']}"]["write_result"] = self.clock

        for i in range(self.imul_units):
            if self.arithmetic_reservation_station[f"imul{i}"]["busy"]:
                if self.arithmetic_reservation_station[f"imul{i}"]["qj"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"imul{i}"]["qj"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"imul{i}"]["vj"] = self.register_file[self.arithmetic_reservation_station[f"imul{i}"]["qj"]]["value"]
                        self.arithmetic_reservation_station[f"imul{i}"]["qj"] = None
                if self.arithmetic_reservation_station[f"imul{i}"]["qk"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"imul{i}"]["qk"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"imul{i}"]["vk"] = self.register_file[self.arithmetic_reservation_station[f"imul{i}"]["qk"]]["value"]
                        self.arithmetic_reservation_station[f"imul{i}"]["qk"] = None

                if self.arithmetic_reservation_station[f"imul{i}"]["qj"] is None and self.arithmetic_reservation_station[f"imul{i}"]["qk"] is None:
                    self.instruction_status[f"i{self.arithmetic_reservation_station[f'imul{i}']['instruction']}"]["remaining_exec_time"] -= 1
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'imul{i}']['instruction']}"]["remaining_exec_time"] == 0:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'imul{i}']['instruction']}"]["execution_completion"] = self.clock
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'imul{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'imul{i}']['instruction']}"]["write_result"] = self.clock

        for i in range(self.fadd_units):
            if self.arithmetic_reservation_station[f"fadd{i}"]["busy"]:
                if self.arithmetic_reservation_station[f"fadd{i}"]["qj"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"fadd{i}"]["qj"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"fadd{i}"]["vj"] = self.register_file[self.arithmetic_reservation_station[f"fadd{i}"]["qj"]]["value"]
                        self.arithmetic_reservation_station[f"fadd{i}"]["qj"] = None
                if self.arithmetic_reservation_station[f"fadd{i}"]["qk"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"fadd{i}"]["qk"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"fadd{i}"]["vk"] = self.register_file[self.arithmetic_reservation_station[f"fadd{i}"]["qk"]]["value"]
                        self.arithmetic_reservation_station[f"fadd{i}"]["qk"] = None

                if self.arithmetic_reservation_station[f"fadd{i}"]["qj"] is None and self.arithmetic_reservation_station[f"fadd{i}"]["qk"] is None:
                    self.instruction_status[f"i{self.arithmetic_reservation_station[f'fadd{i}']['instruction']}"]["remaining_exec_time"] -= 1
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'fadd{i}']['instruction']}"]["remaining_exec_time"] == 0:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'fadd{i}']['instruction']}"]["execution_completion"] = self.clock
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'fadd{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'fadd{i}']['instruction']}"]["write_result"] = self.clock

        for i in range(self.fmul_units):
            if self.arithmetic_reservation_station[f"fmul{i}"]["busy"]:
                if self.arithmetic_reservation_station[f"fmul{i}"]["qj"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"fmul{i}"]["qj"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"fmul{i}"]["vj"] = self.register_file[self.arithmetic_reservation_station[f"fmul{i}"]["qj"]]["value"]
                        self.arithmetic_reservation_station[f"fmul{i}"]["qj"] = None
                if self.arithmetic_reservation_station[f"fmul{i}"]["qk"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"fmul{i}"]["qk"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"fmul{i}"]["vk"] = self.register_file[self.arithmetic_reservation_station[f"fmul{i}"]["qk"]]["value"]
                        self.arithmetic_reservation_station[f"fmul{i}"]["qk"] = None

                if self.arithmetic_reservation_station[f"fmul{i}"]["qj"] is None and self.arithmetic_reservation_station[f"fmul{i}"]["qk"] is None:
                    self.instruction_status[f"i{self.arithmetic_reservation_station[f'fmul{i}']['instruction']}"]["remaining_exec_time"] -= 1
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'fmul{i}']['instruction']}"]["remaining_exec_time"] == 0:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'fmul{i}']['instruction']}"]["execution_completion"] = self.clock
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'fmul{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'fmul{i}']['instruction']}"]["write_result"] = self.clock

        for i in range(self.logic_units):
            if self.arithmetic_reservation_station[f"logic{i}"]["busy"]:
                if self.arithmetic_reservation_station[f"logic{i}"]["qj"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"logic{i}"]["qj"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"logic{i}"]["vj"] = self.register_file[self.arithmetic_reservation_station[f"logic{i}"]["qj"]]["value"]
                        self.arithmetic_reservation_station[f"logic{i}"]["qj"] = None
                if self.arithmetic_reservation_station[f"logic{i}"]["qk"] is not None:
                    if self.register_file[self.arithmetic_reservation_station[f"logic{i}"]["qk"]]["used_by"] is None:
                        self.arithmetic_reservation_station[f"logic{i}"]["vk"] = self.register_file[self.arithmetic_reservation_station[f"logic{i}"]["qk"]]["value"]
                        self.arithmetic_reservation_station[f"logic{i}"]["qk"] = None

                if self.arithmetic_reservation_station[f"logic{i}"]["qj"] is None and self.arithmetic_reservation_station[f"logic{i}"]["qk"] is None:
                    self.instruction_status[f"i{self.arithmetic_reservation_station[f'logic{i}']['instruction']}"]["remaining_exec_time"] -= 1
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'logic{i}']['instruction']}"]["remaining_exec_time"] == 0:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'logic{i}']['instruction']}"]["execution_completion"] = self.clock
                    if self.instruction_status[f"i{self.arithmetic_reservation_station[f'logic{i}']['instruction']}"]["remaining_exec_time"] == -1:
                        self.instruction_status[f"i{self.arithmetic_reservation_station[f'logic{i}']['instruction']}"]["write_result"] = self.clock



    def any_unit_busy(self):
        for i in range(self.load_store_units):
            if self.memory_reservation_station[f"load{i}"]["busy"]:
                return True

        for i in range(self.iadd_units):
            if self.arithmetic_reservation_station[f"iadd{i}"]["busy"]:
                return True

        for i in range(self.imul_units):
            if self.arithmetic_reservation_station[f"imul{i}"]["busy"]:
                return True

        for i in range(self.fadd_units):
            if self.arithmetic_reservation_station[f"fadd{i}"]["busy"]:
                return True

        for i in range(self.fmul_units):
            if self.arithmetic_reservation_station[f"fmul{i}"]["busy"]:
                return True

        for i in range(self.logic_units):
            if self.arithmetic_reservation_station[f"logic{i}"]["busy"]:
                return True

        return False
    def run(self):
        while self.count != len(self.instructions) or self.any_unit_busy():
            self.execute()
            # print instruction status
            print(f'Clock cycle: {self.clock}')
            for key, value in self.instruction_status.items():
                print(f'{key}: {value}')
            # print all the reservation stations
            print('Arithmetic Reservation Stations:')
            for key, value in self.arithmetic_reservation_station.items():
                print(f'{key}: {value}')

            print('Memory Reservation Stations:')
            for key, value in self.memory_reservation_station.items():
                print(f'{key}: {value}')

            print('Register File:')
            for key, value in self.register_file.items():
                print(f'{key}: {value}')

            print('\n')
            # sleep(5)
        # Run the Tomasulo algorithm
        

with open('instructions.txt', 'r') as file:
    instructions = [line.strip() for line in file.readlines()]

tom = Tomasulo(instructions)
tom.run()