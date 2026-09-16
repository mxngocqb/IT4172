import numpy as np
import math
import matplotlib.pyplot as plt
from numpy import r_

TOTAL_SAMPLES = 200
n = np.arange(TOTAL_SAMPLES)
f0 = 1/50
Xn = np.sin(2 * math.pi * f0 * n)
#plt.stem(tn, xn, use_line_collection=True)
plt.plot(n, Xn)
plt.show()
N_bits = 6
NUMBER_QUANTIZATION_LEVELS = 2 ** N_bits
quantization_step = 2 / (NUMBER_QUANTIZATION_LEVELS - 1)
quantization_levels = np.arange(-1.0, 1.0 + quantization_step, quantization_step)

print("Tổng số mức lượng tử: ", NUMBER_QUANTIZATION_LEVELS)
print("Bước lượng tử: ", quantization_step)
print("Các mức lượng tử: ", quantization_levels.shape)
print("Các mức lượng tử: ", quantization_levels)