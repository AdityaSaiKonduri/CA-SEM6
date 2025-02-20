import random
import matplotlib.pyplot as plt
import numpy as np

class CacheSimulator:
    def __init__(self):
        self.way = 4
        self.main_memory_size = 64 * 1024
        self.l1cache_size = 2 * 1024
        self.l2cache_size = 16 * 1024 // self.way
        self.block_size = 16
        self.word_size = 64
        self.address_size = 16
        
        # Initialize main memory
        self.main_memory = []
        for i in range(self.main_memory_size):
            address = format(i, f'0{self.address_size}b')
            data = format(random.randint(0, 2**self.word_size - 1), f'0{self.word_size}b')
            self.main_memory.append([address, data])
        
        # Initialize cache
        self.l1cache_blocks = self.l1cache_size // self.block_size
        self.l2cache_blocks = self.l2cache_size // self.block_size
        self.isb_misses = 0
        self.isb_accesses = 0
        self.isb_interval_misses = 0
        self.isb_misses_per_interval = []
        
        # Add victim cache stats
        self.victim_misses = 0
        self.victim_accesses = 0
        self.victim_interval_misses = 0
        self.victim_misses_per_interval = []
        self.reset_cache()

    def check_isb(self, tag, index, word_offset):
        self.isb_accesses += 1
        for i in range(len(self.ISB)):
            if self.ISB[i]["valid"] == 1 and self.ISB[i]["tag"] == tag:
                self.ISB[i]["lru"] = 0
                return self.ISB[i]["data"][word_offset*self.word_size:word_offset*self.word_size+self.word_size]
        self.isb_misses += 1
        self.isb_interval_misses += 1
        return None
        
    def reset_cache(self):
        # Existing initialization code remains same
        self.cache1 = [{"valid": 0, "dirty": 0, "tag": None, "data": "", "lru": 0} 
                     for _ in range(self.l1cache_blocks)]
        self.cache2 = [[{"valid": 0, "dirty": 0, "tag": None, "data": "", "lru": 0} 
                      for ii in range(self.way)] for _ in range(self.l2cache_blocks)]
        
        self.victim_cache = [{"valid": 0, "dirty": 0, "tag": None, "data": "", "lru": 0} for _ in range(4)]
        self.write_buffer = [{"valid": 0, "dirty": 0, "tag": None, "data": ""} for _ in range(4)]
        self.ISB = [{"valid": 0, "dirty": 0, "tag": None, "data": "", "lru" : 0} for _ in range(4)]

        # Reset L1 stats
        self.l1misses = 0
        self.l1accesses = 0
        self.l1_replacements = 0
        self.l1_misses_per_interval = []
        self.l1_interval_misses = 0

        # Reset L2 stats
        self.l2misses = 0
        self.l2accesses = 0
        self.l2_replacements = 0
        self.l2_misses_per_interval = []
        self.l2_interval_misses = 0

        # Reset ISB stats
        self.isb_misses = 0
        self.isb_accesses = 0
        self.isb_interval_misses = 0
        self.isb_misses_per_interval = []
        
        # Reset victim cache stats
        self.victim_misses = 0
        self.victim_accesses = 0
        self.victim_interval_misses = 0
        self.victim_misses_per_interval = []

    def prefetch_to_isb(self, instruction):
        # Calculate next block address
        current_addr = int(instruction, 2)
        next_addr = current_addr + self.block_size
        if next_addr >= self.main_memory_size:
            return
            
        next_instruction = format(next_addr, f'0{self.address_size}b')
        tag = format(int(next_instruction[:5], 2), f'0{5}b')
        
        # Find empty or LRU slot in ISB
        empty_slot = None
        max_lru = -1
        max_lru_slot = 0
        
        for i in range(len(self.ISB)):
            if self.ISB[i]["valid"] == 0:
                empty_slot = i
                break
            if self.ISB[i]["lru"] > max_lru:
                max_lru = self.ISB[i]["lru"]
                max_lru_slot = i
                
        slot = empty_slot if empty_slot is not None else max_lru_slot
        
        # Load data into ISB
        self.ISB[slot]["valid"] = 1
        self.ISB[slot]["tag"] = tag
        self.ISB[slot]["data"] = ""
        self.ISB[slot]["lru"] = 0
        
        # Get data from main memory
        tag2 = next_instruction[:12]
        x = tag2 + '0'*int(self.block_size ** 0.5)
        for k in range(self.block_size):
            y = int(x, 2) + k
            self.ISB[slot]["data"] += str(self.main_memory[y][1])

    def l1accessing_cache(self, instruction):
        self.l1accesses += 1
        tag = format(int(instruction[:5]))
        index = int(instruction[5:12], 2)
        word_offset = int(instruction[12:16],2)
        
        if self.cache1[index]["valid"] == 1 and self.cache1[index]["tag"] == tag:
            self.cache1[index]["lru"] = 0
            # return the data from l1 cache
            return self.cache1[index]["data"][word_offset*self.word_size:word_offset*self.word_size+self.word_size]
        
        isb_data = self.check_isb(tag, index, word_offset)
        if isb_data:
            return isb_data
        self.victim_accesses+=1
        for i in range(len(self.victim_cache)):
            if self.victim_cache[i]["valid"] == 1 and self.victim_cache[i]["tag"] == tag and self.cache1[index]["valid"] == 0:
                self.victim_cache[i]["valid"] = 0
                # now send this data to index in l1 cache
                self.cache1[index]["valid"] = 1
                self.cache1[index]["tag"] = tag
                self.cache1[index]["data"] = self.victim_cache[i]["data"]
                self.cache1[index]["lru"] = 0
                return self.cache1[index]["data"][word_offset*self.word_size:word_offset*self.word_size+self.word_size]

        else:
            self.victim_misses += 1
            self.victim_interval_misses += 1    
            self.l1misses += 1
            self.l1_interval_misses += 1
            self.l1_replacements += 1
            if self.cache1[index]["valid"] == 0:
                self.l2accessing_cache(index,instruction, tag)
                self.prefetch_to_isb(instruction)
                return self.cache1[index]["data"][word_offset*self.word_size:word_offset*self.word_size+self.word_size]
            else:
                # put this block in victim cache if space is available or replace the block with max lru value in the victim cache
                for i in range(len(self.victim_cache)):
                    if self.victim_cache[i]["valid"] == 0:
                        self.victim_cache[i]["valid"] = 1
                        self.victim_cache[i]["tag"] = self.cache1[index]["tag"]
                        self.victim_cache[i]["data"] = self.cache1[index]["data"]
                        self.victim_cache[i]["lru"] = 0
                        self.l2accessing_cache(index,instruction, tag)
                        self.prefetch_to_isb(instruction)
                        return self.cache1[index]["data"][word_offset*self.word_size:word_offset*self.word_size+self.word_size]
                max_lru = max(block["lru"] for block in self.victim_cache)
                for i in range(len(self.victim_cache)):
                    if self.victim_cache[i]["lru"] == max_lru:
                        self.victim_cache[i]["tag"] = self.cache1[index]["tag"]
                        self.victim_cache[i]["data"] = self.cache1[index]["data"]
                        self.victim_cache[i]["lru"] = 0
                        self.l2accessing_cache(index,instruction, tag)
                        self.prefetch_to_isb(instruction)
                        return self.cache1[index]["data"][word_offset*self.word_size:word_offset*self.word_size+self.word_size]

    def l2accessing_cache(self, i, instruction, tag1):
        self.l2accesses += 1
        tag = format(int(instruction[:4], 2), f'0{4}b')
        index = int(instruction[4:12], 2)
        
        for j in range(self.way):
            if self.cache2[index][j]["valid"] == 1 and self.cache2[index][j]["tag"] == tag:
                self.cache2[index][j]["lru"] = 0
                self.cache1[i]["valid"] = 1
                self.cache1[i]["tag"] = tag1
                self.cache1[i]["data"] = self.cache2[index][j]["data"]
                self.cache1[i]["lru"] = 0
                return True
                
        self.l2misses += 1
        self.l2_interval_misses += 1
        
        for j in range(self.way):
            if self.cache2[index][j]["valid"] == 0:
                self._handle_cache_miss(index, tag, instruction, j, tag1, i)
                return False
                
        self.l2_replacements += 1
        max_lru = max(block["lru"] for block in self.cache2[index])
        for j in range(self.way):
            if self.cache2[index][j]["lru"] == max_lru:
                self._handle_cache_miss(index, tag, instruction, j, tag1, i)
                return False

    def _handle_cache_miss(self, index, tag, instruction, j, tag1, i):
        # print("Inside handle miss")
        self.cache2[index][j]['valid'] = 1
        self.cache2[index][j]['tag'] = tag
        self.cache2[index][j]['data'] = ""
        self.cache2[index][j]['lru'] = 0
        self.cache1[i]['valid'] = 1
        self.cache1[i]['tag'] = tag1
        self.cache1[i]['data'] = ""
        self.cache1[i]['lru'] = 0
        
        tag2 = instruction[:12]
        x = tag2 + '0'*int(self.block_size ** 0.5)
        for k in range(self.block_size):
            y = int(x, 2) + k
            self.cache1[i]['data'] += str(self.main_memory[y][1])
            self.cache2[index][j]['data'] += str(self.main_memory[y][1])

    def simulate_random_access(self, num_accesses=1000000):
        self.reset_cache()
        
        l1_misses_per_interval = []
        l2_misses_per_interval = []
        isb_misses_per_interval = []
        victim_misses_per_interval = []
        
        for i in range(num_accesses):
            # Generate random address
            addr = random.randint(0, self.main_memory_size - 1)
            instruction_address = format(addr, f'0{self.address_size}b')
            
            data = self.l1accessing_cache(instruction_address)
            p =0.3
            r = np.random.uniform(0,1)
            if r < p:
                if data is None or data == '':
                    print(data)
                    continue
                data = int(data, 2)
                data+=1
                # write in the write buffer
                self.write_buffer[0]["valid"] = 1
                self.write_buffer[0]["tag"] = instruction_address
                self.write_buffer[0]["data"] = format(data, f'0{self.word_size}b')

                # make it dirty in l1 cache
                l1_index = int(instruction_address[5:12],2)
                l1_word_offset = int(instruction_address[12:],2)
                self.cache1[l1_index]["dirty"] = 1

                # make it dirty in l2 cache
                l2_index = int(instruction_address[4:12],2)
                for i in range(self.way):
                    if self.cache2[l2_index][i]["tag"] == instruction_address[:4]:
                        self.cache2[l2_index][i]["dirty"] = 1
                        break
                

                self.modify_data(instruction=instruction_address, data=data)

            if (i + 1) % 10000 == 0:
                l1_misses_per_interval.append(self.l1_interval_misses)
                l2_misses_per_interval.append(self.l2_interval_misses)
                isb_misses_per_interval.append(self.isb_interval_misses)
                victim_misses_per_interval.append(self.victim_interval_misses)
                self.l1_interval_misses = 0
                self.l2_interval_misses = 0
                self.isb_interval_misses = 0
                self.victim_interval_misses = 0
        
        print(f"ISB Miss Rate: {(self.isb_misses/self.isb_accesses)*100:.2f}%")
        print("ISB Accesses: ", self.isb_accesses)
        print("ISB Misses: ", self.isb_misses)
        print(f"Victim Cache Miss Rate: {(self.victim_misses/self.victim_accesses)*100:.2f}%")
        print("Victim Access :",self.victim_accesses)
        print("Victim Misses :",self.victim_misses)
        print("L1 Access :",self.l1accesses)
        print("L1 Misses :",self.l1misses)
        print("L2 Access :",self.l2accesses)
        print("L2 Misses :",self.l2misses)
        return l1_misses_per_interval, l2_misses_per_interval, self.l1misses, self.l2misses
    
    def modify_data(self, instruction, data):
        # modify the data in the main memory location
        location = int(instruction, 2)
        self.main_memory[location][1] = format(data, f'0{self.word_size}b')

        # change in L! cache
        l1_index = int(instruction[5:12],2)
        l1_word_offset = int(instruction[12:],2)
        self.cache1[l1_index]["data"] = self.cache1[l1_index]["data"][:l1_word_offset*self.word_size] + format(data, f'0{self.word_size}b') + self.cache1[l1_index]["data"][l1_word_offset*self.word_size+self.word_size:]

        # change in l2 cache
        l2_index = int(instruction[4:12],2)
        for i in range(self.way):
            if self.cache2[l2_index][i]["tag"] == instruction[:4]:
                l2_word_offset = int(instruction[12:],2)
                self.cache2[l2_index][i]["data"] = self.cache2[l2_index][i]["data"][:l2_word_offset*self.word_size] + format(data, f'0{self.word_size}b') + self.cache2[l2_index][i]["data"][l2_word_offset*self.word_size+self.word_size:]


        # make dirty bit pure in l1 cache
        self.cache1[l1_index]["dirty"] = 0

        # make dirty bit pure in l2 cache
        for i in range(self.way):
            if self.cache2[l2_index][i]["tag"] == instruction[:4]:
                self.cache2[l2_index][i]["dirty"] = 0

        return True


def plot_miss_comparison():
    simulator = CacheSimulator()
    
    # Simulate random access
    l1_misses, l2_misses, total_l1_misses, total_l2_misses = simulator.simulate_random_access()
    
    print(f"\nRandom Access Total Misses:")
    print(f"L1 Cache: {total_l1_misses}")
    print(f"L2 Cache: {total_l2_misses}")
    print(f"L1 Miss Rate: {(total_l1_misses/simulator.l1accesses)*100:.2f}%")
    print(f"L2 Miss Rate: {(total_l2_misses/simulator.l2accesses)*100:.2f}%")
    
    plt.figure(figsize=(15, 6))
    
    # Create x-axis values
    x = np.arange(len(l1_misses))
    
    # L1 Cache Plot (Left)
    plt.subplot(1, 2, 1)
    plt.plot(x, l1_misses, 'b-', linewidth=2)
    plt.xlabel('Intervals (100 accesses each)')
    plt.ylabel('Number of Cache Misses')
    plt.title('L1 Cache - Random Access')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # L2 Cache Plot (Right)
    plt.subplot(1, 2, 2)
    plt.plot(x, l2_misses, 'r-', linewidth=2)
    plt.xlabel('Intervals (100 accesses each)')
    plt.ylabel('Number of Cache Misses')
    plt.title('L2 Cache - Random Access')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.show()

# Run the simulation
plot_miss_comparison()