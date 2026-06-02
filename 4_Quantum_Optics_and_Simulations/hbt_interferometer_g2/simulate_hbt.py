import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --- 1. Simulation Physical Parameters ---
N_photons = 3_000_000        # Number of actual quantum dot photons generated
tau_pump = 2e-9              # How fast the laser re-excites the dot (2 ns)
tau_decay = 10e-9            # Emitting lifetime of the quantum dot (10 ns)

noise_ratio = 0.4            # Add 40% random background laser scatter / dark counts
detector_jitter = 0.4e-9     # SPAD timing jitter (400 ps blurring)

bin_width = 1e-9             # Histogram binning resolution (1 ns)
max_delay = 100e-9           # Plotting horizontal scale out to +- 100 ns

print(f"--- Simulating HBT setup ---")
print(f"Generating quantum dot continuous wave emission ({N_photons} photons)...")

# --- 2. Generate Two-Level System Physics (Antibunching) ---
# A true single photon source cannot emit two photons at once. 
# It must first absorb a pump photon (tau_pump) and then re-emit it (tau_decay).
# Summing two exponentially distributed wait times perfectly models a 2-level quantum emitter!
dt_qd = np.random.exponential(tau_pump, N_photons) + np.random.exponential(tau_decay, N_photons)
timestamps_qd = np.cumsum(dt_qd)
T_total = timestamps_qd[-1]

# --- 3. Add Classical Noise (Laser Bleed / Poissonian) ---
N_bg = int(N_photons * noise_ratio)
print(f"Injecting {N_bg} background noise photons...")
timestamps_bg = np.random.uniform(0, T_total, N_bg)

# Combine true quantum photons + random classical noise
all_timestamps = np.concatenate((timestamps_qd, timestamps_bg))
all_timestamps = np.sort(all_timestamps)

# --- 4. Hit the 50:50 Beamsplitter ---
# A physical photon can only hit Detector A OR Detector B. Never both.
route = np.random.rand(len(all_timestamps)) < 0.5
tA = all_timestamps[route]
tB = all_timestamps[~route]

# --- 5. Detector Jitter Fluctuation ---
# Smears exact timing timestamps slightly 
tA += np.random.normal(0, detector_jitter, len(tA))
tB += np.random.normal(0, detector_jitter, len(tB))

tA = np.sort(tA)
tB = np.sort(tB)

print(f"Detector A captured: {len(tA)} events")
print(f"Detector B captured: {len(tB)} events")


# --- 6. HBT Math (Exact same cross-correlation engine as our analysis script) ---
print("Running cross-correlation...")
edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
tau = 0.5 * (edges[:-1] + edges[1:])
H = np.zeros(len(tau))

j0 = 0
tA_len, tB_len = len(tA), len(tB)
for i in range(tA_len):
    ta_i = tA[i]
    while j0 < tB_len and tB[j0] < ta_i - max_delay:
        j0 += 1
    j = j0
    while j < tB_len and tB[j] <= ta_i + max_delay:
        idx = int((tB[j] - ta_i + max_delay) / bin_width)
        if 0 <= idx < len(H): H[idx] += 1
        j += 1

# Normalize
outer_left = H[:len(H)//4]
outer_right = H[3*len(H)//4:]
baseline = np.mean(np.concatenate((outer_left, outer_right)))

g2 = H / baseline
g2 = 0.5 * (g2 + g2[::-1])

# Fit to mathematical model
def antibunching_model(t, g0, tc):
    return 1 - (1 - g0) * np.exp(-np.abs(t) / tc)

popt, _ = curve_fit(antibunching_model, tau, g2, p0=[0.2, 10e-9], bounds=([0, 1e-12], [np.inf, np.inf]))
g0_fit, tc_fit = popt

print(f"\nSimulation Achieved g²(0) = {g0_fit:.3f}")


# --- 7. Plotting the Simulation ---
plt.rcParams.update({
    'font.size': 14,
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.linewidth': 2,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.width': 2,
    'ytick.major.width': 2,
    'xtick.major.size': 6,
    'ytick.major.size': 6,
    'xtick.top': True,
    'ytick.right': True
})

fig, ax = plt.subplots(figsize=(7, 5))

ax.scatter(tau*1e9, g2, color='#ff007f', s=60, alpha=0.9, label="Simulated SPAD Data", zorder=3)
tau_fit_axis = np.linspace(-max_delay, max_delay, 500)
ax.plot(tau_fit_axis*1e9, antibunching_model(tau_fit_axis, *popt), 'black', linewidth=2.5, label="Quantum Fit", zorder=4)

ax.axhline(1.0, color='gray', linestyle='--', linewidth=2, alpha=0.5, zorder=1)

ax.set_xlim([-40, 40])
ax.set_ylim([0, 1.25])
ax.set_yticks([0, 0.5, 1.0])

ax.set_xlabel("Delay Time (ns)", fontweight='bold')
ax.set_ylabel("g²(τ)", fontweight='bold')
ax.set_title("Simulated Single-Photon Emitter", fontweight='bold')

stats_str = f"Sim g²(0) = {g0_fit:.2f}\nSim $\\tau_c$ = {tc_fit*1e9:.1f} ns"
ax.text(0.5, 0.1, stats_str, transform=ax.transAxes, 
        fontsize=14, fontweight='bold', va='bottom', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', alpha=0.9))

ax.legend(loc='lower right', frameon=False)
plt.tight_layout()

out_file = "simulated_hbt_plot.png"
plt.savefig(out_file, dpi=300)
print(f"Saved highly realistic simulation to {out_file}")

plt.show()
