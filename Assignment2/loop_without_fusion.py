import numpy as np
import time

a = np.random.rand(1000, 1000)
b = np.random.rand(1000, 1000)
c = np.random.rand(1000, 1000)
d = np.random.rand(1000, 1000)

start_time = time.time()
for i in range(a.shape[0]):
    for j in range(a.shape[1]):
        a[i][j] = 1/b[i][j] * c[i][j]


for i in range(a.shape[0]):
    for j in range(a.shape[1]):
        d[i][j] = a[i][j] + c[i][j]

end_time = time.time()
print(f"Execution time without optimization: {end_time - start_time}")