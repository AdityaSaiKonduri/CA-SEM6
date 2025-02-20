import numpy as np
import time

# Initialize matrices
N = 500  # You can adjust this size
B = 2  # Block size
y = np.random.randint(1, 10, (N, N))  # Random values for y
z = np.random.randint(1, 10, (N, N))  # Random values for z
x = np.zeros((N, N))  # Initialize result matrix x

# Start time measurement for the blocked matrix multiplication
start_time = time.time()

# Matrix multiplication with blocking
for jj in range(0, N, B):
    for kk in range(0, N, B):
        for i in range(N):
            for j in range(jj, min(jj + B, N)):
                r = 0
                for k in range(kk, min(kk + B, N)):
                    r += y[i][k] * z[k][j]
                x[i][j] += r

# Measure time taken
end_time = time.time()
print("Result matrix x (with blocking):")
print(x)
print(f"Time taken for blocked matrix multiplication: {end_time - start_time:.6f} seconds\n")
