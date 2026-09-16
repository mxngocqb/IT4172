import matplotlib.pyplot as plt
import numpy as np
import math

# Tạo trục thời gian
t = np.arange(0, 1 , 0.0001)
print(t.shape)
print(t[-10:])
t[:10]

# Tạo tín hiệu x(t)
Fa = 50
xt = np.cos(2 * math.pi * Fa * t)


# ============================================================
# (a) Tần số lấy mẫu tối thiểu theo định lý Nyquist
# Fs >= 2 * Fa
# ============================================================

Fs_min = 2 * Fa

print("(a) Tần số lấy mẫu tối thiểu:")
print("Fs_min =", Fs_min, "Hz")


# ============================================================
# (b) Lấy mẫu với Fs = 200 Hz
#
# x[n] = cos(2*pi*(Fa/Fs)*n)
#      = cos(pi*n)
# ============================================================

Fs = 200
n = np.arange(0, 40, 1)
nt = n / Fs
xn = np.cos(2*math.pi * Fa / Fs * n)

plt.plot(t, xt)
plt.plot(nt, xn, "g*")
plt.axis([0,0.2,-1.1,1.1])
plt.grid()
plt.show()

# ============================================================
# (c) Lấy mẫu với Fs = 75 Hz
#
# x[n] = cos(2*pi*(Fa/Fs)*n)
#      = cos(pi*n)
# ============================================================

Fs = 75
n = np.arange(0, 40, 1)
nt = n / Fs
xn = np.cos(2*math.pi * Fa / Fs * n)

plt.plot(t, xt)
plt.plot(nt, xn, "g*")
plt.axis([0,0.2,-1.1,1.1])
plt.grid()
plt.show()

# d) Lấy mẫu với Fs = 25 Hz
xt_25 = np.cos(2 * math.pi * 25 * t)

n = np.arange(0, 40, 1)
xn_25 = np.cos(2*math.pi * 25 / Fs * n)

plt.plot(t, xt)
plt.plot(t, xt_25, "g-")
plt.plot(nt, xn_25, "go")
plt.plot(nt, xn, "rx")
plt.axis([0,0.2,-1.1,1.1])
plt.grid()
plt.show()