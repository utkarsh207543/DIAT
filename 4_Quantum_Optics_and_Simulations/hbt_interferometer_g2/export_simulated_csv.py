import numpy as np
import datetime
import os

# --- 1. Simulation Physics Parameters ---
N_photons = 3_000_000        
tau_pump = 2e-9              
tau_decay = 10e-9            
noise_ratio = 0.4            
detector_jitter = 0.4e-9     

print(f"--- Simulating Physical Photons ---")
dt_qd = np.random.exponential(tau_pump, N_photons) + np.random.exponential(tau_decay, N_photons)
timestamps_qd = np.cumsum(dt_qd)
T_total = timestamps_qd[-1]

N_bg = int(N_photons * noise_ratio)
timestamps_bg = np.random.uniform(0, T_total, N_bg)

all_timestamps = np.concatenate((timestamps_qd, timestamps_bg))

route = np.random.rand(len(all_timestamps)) < 0.5
tA = all_timestamps[route]
tB = all_timestamps[~route]

tA += np.random.normal(0, detector_jitter, len(tA))
tB += np.random.normal(0, detector_jitter, len(tB))

# Crop any negative times caused by jitter shifting
tA = tA[tA >= 0]
tB = tB[tB >= 0]

print("Chronologically interleaving Detectors A and B...")
# Source 1 = Channel A, Source 2 = Channel B
events_A = np.column_stack((np.ones(len(tA), dtype=int), tA))
events_B = np.column_stack((np.full(len(tB), 2, dtype=int), tB))

all_events = np.vstack((events_A, events_B))
# Sort all global events exactly chronologically
all_events = all_events[all_events[:, 1].argsort()]

csv_filename = "xx.csv"
print(f"Writing {len(all_events)} perfect Moku format rows to {csv_filename}...")

now_str = datetime.datetime.now().strftime("%Y-%m-%d T %H:%M:%S +0530")

with open(csv_filename, "w") as f:
    # Exact replica of the Moku header footprint 
    f.write("% Moku:Lab Time & Frequency Analyzer\n")
    f.write("% Windowed acquisition, window length 1.000 s\n")
    f.write("% Linear interpolation\n")
    f.write("% Event A (logging on) - Input 1, 0.000 V, Rising edge, 0.000 s holdoff\n")
    f.write("% Event B (logging on) - Input 2, 0.000 V, Rising edge, 0.000 s holdoff\n")
    f.write("% Interval A (on) - Start: Event A, Stop: Event A\n")
    f.write("% Interval B (on) - Start: Event B, Stop: Event B\n")
    f.write("% Histograms - g?^2? correlation function, start time 0.000 000 00 s, stop time 100.000 000 us\n")
    f.write("% Advanced settings - Smoothing filter: Auto, Multiple start events: Use last, Incomplete intervals: Discard\n")
    f.write("% Output 1 - Interval A, Zero point: 0.000 s, 1.000 0 kV/s, Invert off, 2 Vpp\n")
    f.write("% Output 2 - Interval B, Zero point: 0.000 s, 1.000 0 kV/s, Invert off, 2 Vpp\n")
    f.write("% Internal 10 MHz clock\n")
    f.write(f"% Acquired {now_str}\n")
    f.write("% Source (1 = Event A; 2 = Event B), Timestamp (s)\n")
    
    # Write precisely in scientific float notation matching original Moku output perfectly
    for row in all_events:
        f.write(f"{int(row[0])}, {row[1]:.16e}\n")

print(f"DONE! File Size: {os.path.getsize(csv_filename)/1e6:.1f} MB")
