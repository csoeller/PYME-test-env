# from https://stackoverflow.com/questions/70240506/why-is-numpy-native-on-m1-max-greatly-slower-than-on-old-intel-i5/70255105#70255105
# svd benchmark for numpy
import time
import numpy as np
np.random.seed(42)
a = np.random.uniform(size=(300, 300))
runtimes = 10

timecosts = []
for _ in range(runtimes):
    s_time = time.time()
    for i in range(100):
        a += 1
        np.linalg.svd(a)
    timecosts.append(time.time() - s_time)

print(f'mean of {runtimes} runs: {np.mean(timecosts):.5f}s')
