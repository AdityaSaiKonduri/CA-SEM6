import time
import random
import numpy as np
# Define a structure-like class
class Merge:
    def __init__(self, val, key):
        self.val = val
        self.key = key

# Define arrays
val = np.random.rand(1000, 1000)
key = np.random.rand(1000, 1000)

# Start time measurement for after scenario
start_time = time.time()

# Create merged array of structures
merged_array = [Merge(v, k) for v, k in zip(val, key)]

# Perform an operation: Add corresponding elements from val and key in the merged array
result = [item.val + item.key for item in merged_array]

# Measure and print the time taken
end_time = time.time()
print(f"Time taken: {end_time - start_time:.6f} seconds")
