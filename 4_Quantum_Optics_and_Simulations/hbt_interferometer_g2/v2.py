import numpy as np
import matplotlib.pyplot as plt

# =========================
# SETTINGS
# =========================
filename = "A1.csv"

bin_width = 10e-9
window = 200e-9

afterpulse_window = 40e-9
burst_threshold = 1e-9


# =========================
# LOAD DATA
# =========================
data = np.genfromtxt(filename, delimiter=',', comments='%')
data = data[~np.isnan(data).any(axis=1)]

channel = data[:,0].astype(int)
timestamps = data[:,1]

# sort timestamps
idx = np.argsort(timestamps)
timestamps = timestamps[idx]
channel = channel[idx]

ch1 = timestamps[channel==1]
ch2 = timestamps[channel==2]

print("Original counts:")
print("Ch1 =", len(ch1))
print("Ch2 =", len(ch2))


# =========================
# REMOVE AFTERPULSING
# =========================
def remove_afterpulsing(events, window):

    cleaned = [events[0]]

    for i in range(1, len(events)):
        if events[i] - cleaned[-1] > window:
            cleaned.append(events[i])

    return np.array(cleaned)


ch1 = remove_afterpulsing(ch1, afterpulse_window)
ch2 = remove_afterpulsing(ch2, afterpulse_window)

print("\nAfter afterpulse removal:")
print("Ch1 =", len(ch1))
print("Ch2 =", len(ch2))


# =========================
# REMOVE BURST EVENTS
# =========================
def remove_bursts(events, threshold):

    diffs = np.diff(events)
    keep = np.insert(diffs > threshold, 0, True)

    return events[keep]


ch1 = remove_bursts(ch1, burst_threshold)
ch2 = remove_bursts(ch2, burst_threshold)

print("\nAfter burst filtering:")
print("Ch1 =", len(ch1))
print("Ch2 =", len(ch2))


# =========================
# BUILD DELAY HISTOGRAM
# =========================
delays = []

j = 0

for t1 in ch1:

    while j < len(ch2) and ch2[j] < t1 - window:
        j += 1

    k = j

    while k < len(ch2) and ch2[k] <= t1 + window:
        delays.append(ch2[k] - t1)
        k += 1

delays = np.array(delays)


# =========================
# HISTOGRAM
# =========================
bins = np.arange(-window, window + bin_width, bin_width)

hist, edges = np.histogram(delays, bins=bins)

tau = (edges[:-1] + edges[1:]) / 2


# =========================
# NORMALIZATION
# =========================
T = timestamps.max() - timestamps.min()

R1 = len(ch1) / T
R2 = len(ch2) / T

g2_tau = hist / (R1 * R2 * bin_width * T)


# =========================
# SMOOTH CENTER BIN ESTIMATE
# =========================
center_idx = np.argmin(np.abs(tau))

center_avg = np.mean(
    g2_tau[center_idx-1:center_idx+2]
)

print("\nEstimated g2(0) =", center_avg)


# =========================
# PLOT
# =========================
plt.figure(figsize=(8,5))

plt.scatter(
    tau*1e9,
    g2_tau,
    color='deeppink',
    label="Measured data"
)

plt.axhline(1, linestyle='--', color='steelblue')

plt.xlabel("Delay τ (ns)")
plt.ylabel("g²(τ)")
plt.title("HBT Second-order correlation function")

plt.legend()
plt.grid(True)

plt.show()