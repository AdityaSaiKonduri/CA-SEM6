import numpy as np
import time

# Initialize matrices
N = 500  # You can adjust this size
y = np.random.randint(1, 10, (N, N))  # Random values for y
z = np.random.randint(1, 10, (N, N))  # Random values for z
x = np.zeros((N, N))  # Initialize result matrix x

# Start time measurement for the original matrix multiplication
start_time = time.time()

# Matrix multiplication without blocking
for i in range(N):
    for j in range(N):
        r = 0
        for k in range(N):
            r += y[i][k] * z[k][j]
        x[i][j] = r

# Measure time taken
end_time = time.time()
print("Result matrix x (without blocking):")
print(x)
print(f"Time taken for original matrix multiplication: {end_time - start_time:.6f} seconds\n")
