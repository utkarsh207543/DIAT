import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

# ================== LOAD DATA ==================
fname = "BW3_energy.mat"   # <-- BW = 5 nm
data = sio.loadmat(fname)

E = np.abs(data["E"].squeeze())
E = E[E > 0]

print(f"Total round trips loaded = {len(E)}")

# ================== REMOVE BUILD-UP ==================
burn_fraction = 0.30
burn = int(burn_fraction * len(E))
E_ss = E[burn:]

print(f"Steady-state round trips = {len(E_ss)}")

if len(E_ss) < 200:
    raise RuntimeError("Not enough steady-state data for RW statistics")

# ================== SWH & RW THRESHOLD ==================
E_sorted = np.sort(E_ss)[::-1]
SWH = np.mean(E_sorted[:len(E_sorted)//3])
RW_thr = 2.2 * SWH

print(f"SWH          = {SWH:.3e}")
print(f"RW threshold = {RW_thr:.3e}")

# ================== HISTOGRAM ==================
plt.figure(figsize=(9,5.2))

plt.hist(
    E_ss,
    bins=60,
    log=True,
    color="#00cfd1",      # cyan (as in reference)
    edgecolor="black"
)

# Threshold lines
plt.axvline(SWH, color="red", linestyle="--", linewidth=2, label="SWH")
plt.axvline(RW_thr, color="blue", linestyle="--", linewidth=2, label="2.2×SWH")

plt.grid(True, which="both", linestyle=":", linewidth=0.7)
plt.xlabel("Pulse energy (a.u.)", fontsize=12)
plt.ylabel("Number of events", fontsize=12)
plt.title("Statistical distribution of pulse energies (BW = 5 nm)", fontsize=13)

plt.legend(fontsize=11, loc="upper right")

# ================== SAVE ==================
plt.tight_layout()
plt.savefig("RW_histogram_BW5.png", dpi=600)
plt.show()

# ================== RW COUNT ==================
RW_events = np.sum(E_ss > RW_thr)
RW_percent = 100 * RW_events / len(E_ss)

print(f"Rogue-wave events = {RW_events} ({RW_percent:.2f}%)")
