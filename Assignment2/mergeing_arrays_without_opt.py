import time
import numpy as np

val = np.random.rand(100, 100)
key = np.random.rand(100, 100)

# Start time measurement for before scenario
start_time = time.time()

# Perform an operation: Add corresponding elements from val and key
result = [v + k for v, k in zip(val, key)]

# Measure and print the time taken
end_time = time.time()
print(f"Time taken: {end_time - start_time:.6f} seconds\n")
