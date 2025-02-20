import numpy as np
import time

x = np.random.rand(5000, 100)

start_time = time.time()
for j in range(x.shape[1]):
    for i in range(x.shape[0]):
        x[i][j] = 2 * x[i][j]

end_time = time.time()  
print("Execution time without optimization: ", end_time - start_time)