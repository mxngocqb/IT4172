#!/usr/bin/env python3
"""
Đọc file IQ thô do record_raw.py tạo ra, giải điều chế FM,
phát ra loa và lưu thành file WAV.

Bước 2 của chuỗi: record_raw.py  ->  demod_raw.py

Cách chạy:
    python demod_raw.py                      # lấy file mới nhất trong raw/
    python demod_raw.py raw/iq_96.5MHz_....bin
"""
import sys
import json
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.signal import firwin, lfilter
from scipy.io import wavfile

# ============================================================
# CẤU HÌNH
# ============================================================
RAW_DIR = Path(__file__).parent / "raw"

AUDIO_RATE = 16_000        # Loa
VOLUME = 1.5

NUM_TAPS = 129             # độ dài bộ lọc thông thấp
DEEMPHASIS_TAU = 75e-6     # chuẩn FM VN/US

BYTES_PER_SAMPLE = 2       # 1 byte I + 1 byte Q

# Số bit giữ lại của mỗi mẫu I/Q. File gốc là 8 bit (ADC của RTL-SDR).
# Đặt nhỏ hơn 8 để nghe thử tín hiệu bị lượng tử hóa thô: 6, 4, 3, 2, 1
IQ_BITS = 8


# ============================================================
# CHỌN FILE + ĐỌC METADATA
# ============================================================
def pick_file():
    # Ưu tiên đường dẫn truyền từ dòng lệnh
    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    # Nếu không có thì lấy file .bin mới nhất trong raw/
    files = sorted(RAW_DIR.glob("*.bin"), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit(f"Không tìm thấy file .bin nào trong {RAW_DIR}")
    return files[-1]


def read_meta(path):
    """Đọc file .json đi kèm; nếu thiếu thì suy ra từ tên file."""
    meta_path = path.with_suffix(".json")
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            return json.load(f)

    # Dự phòng: tên file dạng iq_96.5MHz_256kHz_16-09-2026_...
    print("(Không có file .json - dùng tham số suy từ tên file)")
    meta = {"freq_mhz": None, "sample_rate": 256_000}
    for part in path.stem.split("_"):
        if part.endswith("MHz"):
            meta["freq_mhz"] = float(part[:-3])
        elif part.endswith("kHz"):
            meta["sample_rate"] = int(part[:-3]) * 1000
    return meta


# ============================================================
# GIẢM SỐ BIT (LƯỢNG TỬ HÓA LẠI)
#
# Byte gốc 8 bit có 256 mức. Giữ lại n bit CAO NHẤT tức là chỉ còn
# 2^n mức, bước lượng tử nở ra 2^(8-n) lần:
#
#       8 bit -> 256 mức, bước 1
#       4 bit ->  16 mức, bước 16
#       1 bit ->   2 mức, bước 128  (chỉ còn dấu của I, Q)
#
# Cách làm: dịch phải rồi dịch trái n bit -> xóa các bit thấp.
# Cộng thêm nửa bước để mức tái tạo nằm GIỮA ô lượng tử thay vì
# ở mép dưới (tránh lệch một chiều - sai số DC).
#
# Mỗi bit bỏ đi làm nhiễu lượng tử tăng ~6 dB (quy tắc SNR ~ 6,02n dB).
# ============================================================
def quantize(b, bits):
    step = 1 << (8 - bits)                      # bước lượng tử mới
    return (b >> (8 - bits) << (8 - bits)) + step // 2


# ============================================================
# MAIN
# ============================================================
def main():
    path = pick_file()
    meta = read_meta(path)

    rf_rate = int(meta["sample_rate"])
    freq_mhz = meta.get("freq_mhz")

    # Hệ số giảm mẫu: 256 kHz -> 16 kHz
    decim = rf_rate // AUDIO_RATE

    # ========================================================
    # 1. ĐỌC CẢ FILE VÀ KHÔI PHỤC IQ
    #
    # File chứa byte xen kẽ I,Q,I,Q... mỗi byte là uint8 (0..255),
    # mức 0 của tín hiệu ứng với 127.5 (xem record_raw.py)
    #
    #   v  = (b - 127.5) / 127.5   ->  [-1, 1]
    #   x  = v[0::2] + j * v[1::2]
    # ========================================================
    b = np.fromfile(path, dtype=np.uint8)
    b = b[:b.size - b.size % 2]        # bỏ byte lẻ nếu file bị cắt

    if IQ_BITS < 8:
        b = quantize(b, IQ_BITS)

    v = (b.astype(np.float32) - 127.5) / 127.5
    iq = v[0::2] + 1j * v[1::2]

    print(f"File           : {path.name}")
    if freq_mhz:
        print(f"Tần số FM      : {freq_mhz:.1f} MHz")
    print(f"RF sample rate : {rf_rate / 1000:.0f} kHz")
    print(f"Audio rate     : {AUDIO_RATE / 1000:.0f} kHz (giảm mẫu 1/{decim})")
    print(f"Độ dài         : {iq.size / rf_rate:.1f} s")
    print(f"Độ phân giải IQ: {IQ_BITS} bit ({1 << IQ_BITS} mức)")

    # ========================================================
    # 2. GIẢI ĐIỀU CHẾ FM
    #
    # Thông tin nằm ở ĐỘ LỆCH PHA giữa hai mẫu liên tiếp:
    #     Δphi[n] = angle(x[n] * conj(x[n-1]))
    # Chia cho pi để đưa về [-1, 1]
    # ========================================================
    fm = np.angle(iq[1:] * np.conj(iq[:-1])) / np.pi

    # ========================================================
    # 3. LỌC THÔNG THẤP CHỐNG CHỒNG PHỔ (anti-aliasing)
    #
    # Lấy 1 mẫu trong mỗi `decim` mẫu chỉ đúng khi băng thông
    # tín hiệu < AUDIO_RATE/2. Cắt tại ~AUDIO_RATE/2 trước khi
    # giảm mẫu để phần phổ cao không gập ngược vào dải nghe.
    # ========================================================
    lpf = firwin(NUM_TAPS, AUDIO_RATE / 2, fs=rf_rate)
    fm = lfilter(lpf, 1.0, fm)

    # ========================================================
    # 4. GIẢM SAMPLE RATE: 256 kHz -> 16 kHz
    # ========================================================
    audio = fm[::decim]

    # ========================================================
    # 5. DE-EMPHASIS 75 us
    #
    # Đài FM khuếch đại sẵn tần số cao (pre-emphasis), phía thu
    # phải hạ lại bằng bộ lọc 1 cực:
    #     y[n] = (1 - a) x[n] + a y[n-1],  a = exp(-1 / (fs.tau))
    # ========================================================
    alpha = np.exp(-1.0 / (AUDIO_RATE * DEEMPHASIS_TAU))
    audio = lfilter([1 - alpha], [1, -alpha], audio)

    # ========================================================
    # 6. ÂM LƯỢNG + CHỐNG TRÀN
    # ========================================================
    audio = np.clip(audio * VOLUME, -1.0, 1.0).astype(np.float32)

    # ========================================================
    # 7. LƯU WAV
    #
    # WAV 16 bit PCM: nhân [-1, 1] với 32767 rồi ép về int16
    # ========================================================
    suffix = ".wav" if IQ_BITS == 8 else f"_{IQ_BITS}bit.wav"
    wav_path = path.with_name(path.stem + suffix)
    wavfile.write(wav_path, AUDIO_RATE, (audio * 32767).astype(np.int16))
    print(f"Đã lưu audio   : {wav_path.name}")

    # ========================================================
    # 8. PHÁT RA LOA
    # ========================================================
    print("Đang phát... (Ctrl+C để dừng)")
    try:
        sd.play(audio, AUDIO_RATE)
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()
        print("\nĐã dừng.")


if __name__ == "__main__":
    main()
