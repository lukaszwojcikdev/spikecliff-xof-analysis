import pandas as pd
import matplotlib.pyplot as plt

df1 = pd.read_csv("STEC_LIVE_i9_shake128_085741_No_TurboB_no_stress.csv")  # no stress
df2 = pd.read_csv("STEC_LIVE_i9_shake128_092643_No_TurboB_stress.csv")  # stress

plt.figure(figsize=(12, 5))
plt.plot(df1["duration_ns"] / 1e6, label="No load", alpha=0.8)
plt.plot(df2["duration_ns"] / 1e6, label="With a load (80% CPU)", alpha=0.8)
plt.ylabel("Chunk access time [ms]")
plt.xlabel("Block number")
plt.title("Timing side-channel: CPU load impact on XOF stream access - No TurboB SHAKE128 on i9")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.savefig("timing_comparison_i9_No_TurboB_shake128.png", dpi=250)
plt.show()
