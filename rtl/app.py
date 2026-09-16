#!/usr/bin/env python3
import numpy as np
import sounddevice as sd
import threading
import queue
from rtlsdr import RtlSdr
from scipy.signal import firwin, lfilter
# ============================================================
# CẤU HÌNH
# ============================================================
FREQ_MHZ = 96.5
RF_RATE = 256_000          # IQ từ RTL-SDR
AUDIO_RATE = 16_000        # Loa
BLOCK_SIZE = 16_384
GAIN = "auto"
VOLUME = 1.5
# 256 kHz -> 32 kHz
DECIM = RF_RATE // AUDIO_RATE
# ============================================================
NUM_TAPS = 129
filter_state = np.zeros(NUM_TAPS - 1)
# ============================================================
# QUEUE ÂM THANH
# ============================================================
audio_queue = queue.Queue(maxsize=10)
# ============================================================
# THREAD LOA
# ============================================================
def audio_worker():
    with sd.OutputStream(
        samplerate=AUDIO_RATE,
        channels=1,
        dtype="float32"
    ) as speaker:
        while True:
            audio = audio_queue.get()
            if audio is None:
                break
            speaker.write(
                audio.reshape(-1, 1)
            )
# ============================================================
# MAIN
# ============================================================
def main():
    global filter_state
    # --------------------------------------------------------
    # RTL-SDR
    # --------------------------------------------------------
    sdr = RtlSdr()
    sdr.sample_rate = RF_RATE
    sdr.center_freq = FREQ_MHZ * 1e6
    sdr.gain = GAIN
    print(f"Đang thu FM {FREQ_MHZ:.1f} MHz")
    print(f"RF sample rate : {RF_RATE / 1000:.0f} kHz")
    print(f"Audio rate     : {AUDIO_RATE / 1000:.0f} kHz")
    print("Ctrl+C để dừng")
    # --------------------------------------------------------
    # Thread phát loa
    # --------------------------------------------------------
    thread = threading.Thread(
        target=audio_worker,
        daemon=True
    )
    thread.start()
    # Mẫu cuối block trước
    previous = 1.0 + 0.0j
    try:
        while True:
            # =================================================
            # 1. THU IQ
            # =================================================
            iq = sdr.read_samples(BLOCK_SIZE)
            # =================================================
            # 2. GIẢI ĐIỀU CHẾ FM
            #
            # Δphi[n] = angle(x[n] * conj(x[n-1]))
            # =================================================
            fm = np.empty(iq.size)
            fm[0] = np.angle(
                iq[0] * np.conj(previous)
            )
            fm[1:] = np.angle(
                iq[1:] * np.conj(iq[:-1])
            )
            previous = iq[-1]
            # =================================================
            # 3. CHUẨN HÓA
            # =================================================
            fm /= np.pi
            # =================================================
            # 4. GIẢM SAMPLE RATE
            #
            # 256 kHz -> 32 kHz
            # =================================================
            audio = fm[::DECIM]
            # =================================================
            # 5. ÂM LƯỢNG
            # =================================================
            audio *= VOLUME
            audio = np.clip(
                audio,
                -1.0,
                1.0
            )
            audio = audio.astype(np.float32)
            # =================================================
            # 6. GỬI SANG LOA
            # =================================================
            try:
                audio_queue.put(
                    audio,
                    timeout=0.01
                )
            except queue.Full:
                pass

    except KeyboardInterrupt:
        print("\nĐã dừng.")
    finally:
        audio_queue.put(None)
        thread.join()
        sdr.close()
        
if __name__ == "__main__":
    main()