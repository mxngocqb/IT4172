#!/usr/bin/env python3
"""
Thu tín hiệu IQ thô từ RTL-SDR và lưu xuống file.

Bước 1 của chuỗi: record_raw.py  ->  demod_raw.py
"""
import json
import datetime
from pathlib import Path

from rtlsdr import RtlSdr

# ============================================================
# CẤU HÌNH
# ============================================================
FREQ_MHZ = 105.5
RF_RATE = 256_000          # IQ từ RTL-SDR
BLOCK_SIZE = 16_384        # số mẫu IQ mỗi lần đọc
GAIN = "auto"

DURATION = 10.0            # thời gian thu (giây); None = thu tới khi Ctrl+C

# Thư mục chứa file thu được (tự tạo nếu chưa có)
OUT_DIR = Path(__file__).parent / "raw"

# ============================================================
# CÁCH THỨC LƯU DỮ LIỆU
# ============================================================
#
# 1. ĐỊNH DẠNG BÊN TRONG FILE
#
#    ADC của RTL-SDR là 8 bit. Thiết bị trả về một luồng BYTE
#    trong đó I và Q nằm XEN KẼ nhau:
#
#        byte:   0    1    2    3    4    5   ...
#                I0   Q0   I1   Q1   I2   Q2  ...
#
#    - Mỗi mẫu phức x[n] = I[n] + jQ[n] chiếm ĐÚNG 2 byte.
#    - Mỗi byte là số nguyên KHÔNG DẤU (uint8), giá trị 0..255,
#      mức 0 V của tín hiệu ứng với giá trị 127.5 (giữa dải).
#
#    Ở đây ta dùng sdr.read_bytes() để lấy thẳng luồng byte đó và
#    ghi nguyên vẹn xuống file, KHÔNG xử lý gì thêm -> "raw IQ".
#    Đây cũng chính là định dạng của lệnh `rtl_sdr` chuẩn, nên file
#    thu được có thể mở bằng GNU Radio, inspectrum, rtl_fm...
#
#    (Nếu dùng sdr.read_samples() thì pyrtlsdr đã tự đổi sang
#     complex128 = 16 byte/mẫu, tốn gấp 8 lần dung lượng mà không
#     thêm được chút thông tin nào.)
#
# 2. KHÔI PHỤC LẠI KHI ĐỌC FILE (xem demod_raw.py)
#
#        b     = np.frombuffer(data, dtype=np.uint8)
#        v     = (b - 127.5) / 127.5        # đưa về [-1, 1]
#        iq    = v[0::2] + 1j * v[1::2]     # tách I, Q
#
# 3. DUNG LƯỢNG
#
#        2 byte/mẫu x 256 000 mẫu/s = 512 000 byte/s ~ 0,5 MB/s
#        => 10 giây ~ 5 MB,  1 phút ~ 30 MB
#
# 4. TÊN FILE ghi rõ TẦN SỐ FM + NGÀY THÁNG + giờ thu, ví dụ:
#
#        iq_96.5MHz_256kHz_16-09-2026_15h48m30s.bin
#
#    Kèm theo một file .json cùng tên chứa metadata (tần số,
#    sample rate, gain, số mẫu...) để bước giải điều chế đọc lại
#    mà không phải đoán tham số.
# ============================================================
BYTES_PER_SAMPLE = 2       # 1 byte I + 1 byte Q


# ============================================================
# TẠO TÊN FILE THEO TẦN SỐ + NGÀY THÁNG
# ============================================================
def make_filename():
    now = datetime.datetime.now()

    # %d-%m-%Y = ngày-tháng-năm, %Hh%Mm%Ss = giờ phút giây
    stamp = now.strftime("%d-%m-%Y_%Hh%Mm%Ss")

    name = (
        f"iq_{FREQ_MHZ:.1f}MHz"
        f"_{RF_RATE // 1000}kHz"
        f"_{stamp}.bin"
    )
    return OUT_DIR / name


# ============================================================
# MAIN
# ============================================================
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = make_filename()

    # --------------------------------------------------------
    # RTL-SDR
    # --------------------------------------------------------
    sdr = RtlSdr()
    sdr.sample_rate = RF_RATE
    sdr.center_freq = FREQ_MHZ * 1e6
    sdr.gain = GAIN

    print(f"Đang thu FM {FREQ_MHZ:.1f} MHz")
    print(f"RF sample rate : {RF_RATE / 1000:.0f} kHz")
    print(f"File           : {path.name}")
    if DURATION:
        print(f"Thời gian      : {DURATION:.0f} s "
              f"(~{DURATION * RF_RATE * BYTES_PER_SAMPLE / 1e6:.1f} MB)")
    else:
        print("Thời gian      : tới khi dừng")
    print("Ctrl+C để dừng")

    total_bytes = 0

    # Số byte cần thu; None = không giới hạn
    target_bytes = (
        int(DURATION * RF_RATE) * BYTES_PER_SAMPLE
        if DURATION else None
    )

    try:
        # ----------------------------------------------------
        # Mở file ở chế độ "wb" = write binary
        # (ghi byte thô, KHÔNG phải text)
        # ----------------------------------------------------
        with open(path, "wb") as f:
            while True:
                # ============================================
                # 1. ĐỌC BYTE THÔ TỪ RTL-SDR
                #
                # read_bytes(n) trả về n byte: I,Q,I,Q,...
                # ============================================
                data = sdr.read_bytes(
                    BLOCK_SIZE * BYTES_PER_SAMPLE
                )

                # ============================================
                # 2. GHI THẲNG XUỐNG FILE
                #
                # Không chuẩn hóa, không lọc -> giữ nguyên
                # dữ liệu gốc của ADC.
                # ============================================
                f.write(data)
                total_bytes += len(data)

                # ============================================
                # 3. HIỂN THỊ TIẾN ĐỘ
                # ============================================
                seconds = total_bytes / BYTES_PER_SAMPLE / RF_RATE
                print(
                    f"\r{seconds:6.1f} s "
                    f"| {total_bytes / 1e6:6.2f} MB",
                    end="",
                    flush=True
                )

                if target_bytes and total_bytes >= target_bytes:
                    break

    except KeyboardInterrupt:
        print("\nĐã dừng.")
    finally:
        sdr.close()

    num_samples = total_bytes // BYTES_PER_SAMPLE

    # --------------------------------------------------------
    # GHI METADATA (.json) ĐI KÈM
    #
    # demod_raw.py sẽ đọc file này để biết tần số / sample rate
    # --------------------------------------------------------
    meta = {
        "file": path.name,
        "center_freq_hz": FREQ_MHZ * 1e6,
        "freq_mhz": FREQ_MHZ,
        "sample_rate": RF_RATE,
        "gain": GAIN,
        "format": "uint8 interleaved IQ (I,Q,I,Q...)",
        "bytes_per_sample": BYTES_PER_SAMPLE,
        "num_samples": num_samples,
        "duration_s": num_samples / RF_RATE,
        "recorded_at": datetime.datetime.now().isoformat(
            timespec="seconds"
        ),
    }
    meta_path = path.with_suffix(".json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print()
    print(f"Đã lưu : {path}")
    print(f"Metadata: {meta_path.name}")
    print(f"Tổng    : {num_samples} mẫu IQ "
          f"({num_samples / RF_RATE:.1f} s, "
          f"{total_bytes / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
