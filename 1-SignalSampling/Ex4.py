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

N_bits = 8
NUMBER_QUANTIZATION_LEVELS = 2 ** N_bits
quantization_step = 2 / (NUMBER_QUANTIZATION_LEVELS - 1)
quantization_levels = np.arange(-1.0, 1.0 + quantization_step, quantization_step)

print("Tổng số mức lượng tử: ", NUMBER_QUANTIZATION_LEVELS)
print("Bước lượng tử: ", quantization_step)
print("Các mức lượng tử: ", quantization_levels.shape)
print("Các mức lượng tử: ", quantization_levels)

Xqn_truncation = []
Xqn_rounding = []
Error_truncation = []
Error_rounding = []

# tìm các Xqn theo lam tron
for idx, xn in enumerate(Xn):
    #print(idx, xn)
    xqn_truncation = quantization_levels[-1]
    xqn_rounding = quantization_levels[-1]
    for i in range(len(quantization_levels) - 1):
        #print(i)
        if xn >= quantization_levels[i] and xn < quantization_levels[i+1]:
            if xn >= 0: 
                xqn_truncation = quantization_levels[i]
            else: 
                xqn_truncation = quantization_levels[i+1]
            if abs(xn - quantization_levels[i]) < abs(xn - quantization_levels[i+1]):
                xqn_rounding = quantization_levels[i]
            else: 
                xqn_rounding = quantization_levels[i+1]
                break

    Xqn_rounding.append(xqn_truncation)
    Error_truncation.append(xn - xqn_truncation)
    Xqn_truncation.append(xqn_rounding)
    Error_rounding.append(xn - xqn_rounding)
    #print("Truncation: ", xn, " => ", xqn_truncation, " Error: ", xn - xqn_truncation)
    abs_error_rounding = [abs(error) for error in Error_rounding]
    # print("Trunction Max Error: ", max(Error_truncation))
    # print("Rounding Max Error: ", max(abs_error_rounding))

N_plot = 200
plt.plot(Xqn_truncation[:N_plot], "o")
plt.plot(Xqn_rounding[:N_plot], "x")
plt.plot(Xn[:N_plot], "*")
plt.yticks(quantization_levels)
plt.grid(axis="y")
plt.legend(("Truncation","Rounding","Analog"))
plt.show()

Eq_truncation = [error*error for error in Error_truncation]
Eq_rounding = [error*error for error in Error_rounding]
Ex = [xn * xn for xn in Xn]
Pq_truncation = sum(Eq_truncation) / len(Eq_truncation)
Pq_rounding = sum(Eq_rounding) / len(Eq_rounding)
Px = sum(Ex) / len(Ex)
SQNR_truncation = 10 * math.log10(Px/Pq_truncation)
SQNR_rounding = 10 * math.log10(Px/Pq_rounding)

print("Pq_truncation: %8.6f" % Pq_truncation)
print("Pq_rounding: %8.6f" % Pq_rounding)
print("Px: %4.1f " % Px)
print("SQNR_truncation: %5.2f dB" % SQNR_truncation)
print("SQNR_rounding: %5.2f dB" % SQNR_rounding)
# SQNR = 1.76 + 6.02b
print("SQNR rounding in theory: %5.2f dB" % (1.76 + 6.02 * N_bits))