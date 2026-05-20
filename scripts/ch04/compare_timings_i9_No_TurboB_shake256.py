# compare_timings_i9_No_TurboB_shake256.py
import pandas as pd
import matplotlib.pyplot as plt

df1 = pd.read_csv("STEC_LIVE_i9_shake256_091115_No_TurboB_no_stress.csv")  # no stress
df2 = pd.read_csv("STEC_LIVE_i9_shake256_093830_No_TurboB_stress.csv")  # stress

plt.figure(figsize=(12, 5))
plt.plot(df1["duration_ns"] / 1e6, label="Bez obciaznia", alpha=0.8)
plt.plot(df2["duration_ns"] / 1e6, label="Z obciazeniem (80% CPU)", alpha=0.8)
plt.ylabel("Czas dostepu do chunka [ms]")
plt.xlabel("Numer bloku")
plt.title("Timing side-channel: wplyw obciaznia CPU na dostep do XOF stream - No TurboB SHAKE256 na i9")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.savefig("timing_comparison_i9_No_TurboB_shake256.png", dpi=250)
plt.show()
