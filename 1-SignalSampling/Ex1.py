import matplotlib.pyplot as plt
import numpy as np
import math
# Tạo trục thời gian
t = np.arange(0, 0.01 , 0.00001)
print(t.shape)
print(t[-10:])
t[:10]
# a) vẽ tính hiệu s(t)
# tạo tín hiệu s(t) = cos(2π1000t)
st = np.cos(2 * math.pi * 1000 * t)
# vẽ tín hiệu s(t)
plt.plot(t, st)
plt.axis([0,0.01,-1.1,1.1])
plt.grid()
plt.show()
# b) Xác định các mẫu trên s(t)
# Lấy mẫu để tạo s(n)
Fs = 8000
n = np.arange(0, 80, 1)
nt = n / Fs
sn = np.cos(2*math.pi * 1000 / Fs * n)
plt.plot(t, st)
plt.plot(nt, sn, "g*")
plt.axis([0,0.01,-1.1,1.1])
plt.grid()
plt.show()
# c) Vẽ tín hiệu s(n)
plt.plot(n, sn, "g*")
plt.axis([0,80,-1.1,1.1])
plt.grid()
plt.show()
# d) Tìm phương trình của s(n)
# s(n) = s(t) tại t = n/Fs
#      = cos(2π1000/Fs * n)
#      = cos(2π1000/8000 * n) 
#      = cos(π/4 * n)
# e) Tìm tần số Fd của s(n)
# Fd = Fa/Fs = 1000/8000 = 1/8 (chu kỳ/samples)
# => Tần số góc rời rạc của s(n) là: 
#       ωd = 2πFd = 2π/8 = π/4
# f) Công thức biểu diễn mối quan hệ giữa:
# Fa của s(t) và Fd của s(n)
# Fd = Fa/Fs 
# Fa = Fd * Fs = 