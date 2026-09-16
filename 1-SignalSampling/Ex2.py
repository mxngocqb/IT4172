import matplotlib.pyplot as plt
import numpy as np
import math

# Tạo trục thời gian
t = np.arange(0, 1, 0.001)

# Tạo tín hiệu liên tục x1(t) và x2(t)
x1t = np.cos(2 * math.pi * 10 * t)
x2t = np.cos(2 * math.pi * 50 * t)

# ============================================================
# Lấy mẫu
# ============================================================
Fs = 40                       # Tần số lấy mẫu: 40 Hz
n = np.arange(0, 40)
nt = n / Fs                   # Thời điểm lấy mẫu

x1n = np.cos(2 * math.pi * 10 / Fs * n)
x2n = np.cos(2 * math.pi * 50 / Fs * n)

# ============================================================
# HÌNH 1: Tín hiệu liên tục và tín hiệu sau lấy mẫu
# ============================================================
plt.figure(figsize=(10, 5))

plt.plot(t, x1t, label=r"$x_1(t)$, $f_1=10$ Hz")
plt.plot(nt, x1n, "g*", label=r"$x_1[n]$ sampled at $F_s=40$ Hz")

plt.plot(t, x2t, "g-", label=r"$x_2(t)$, $f_2=50$ Hz")
plt.plot(nt, x2n, "rx", label=r"$x_2[n]$ sampled at $F_s=40$ Hz")

plt.xlabel("Thời gian (s)")
plt.ylabel("Biên độ")
plt.title(
    r"Lấy mẫu hai tín hiệu "
    r"$x_1(t)=\cos(2\pi\cdot10t)$ và "
    r"$x_2(t)=\cos(2\pi\cdot50t)$"
)

plt.axis([0, 0.21, -1.1, 1.1])
plt.legend()
plt.grid()
plt.show()


# ============================================================
# HÌNH 2: Hai tín hiệu liên tục
# ============================================================
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# x1(t)
ax[0].plot(t, x1t, label=r"$f_1=10$ Hz")
ax[0].set_title(
    r"$x_1(t)=\cos(2\pi\cdot10t)$"
)
ax[0].set_ylabel("Biên độ")
ax[0].axis([0, 0.21, -1.1, 1.1])
ax[0].legend()
ax[0].grid()

# x2(t)
ax[1].plot(t, x2t, "g-", label=r"$f_2=50$ Hz")
ax[1].set_title(
    r"$x_2(t)=\cos(2\pi\cdot50t)$"
)
ax[1].set_xlabel("Thời gian (s)")
ax[1].set_ylabel("Biên độ")
ax[1].axis([0, 0.21, -1.1, 1.1])
ax[1].legend()
ax[1].grid()

plt.tight_layout()
plt.show()