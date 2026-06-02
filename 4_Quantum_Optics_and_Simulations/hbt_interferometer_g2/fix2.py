import numpy as np

# =========================
# SETTINGS
# =========================
filename = "x6.csv"

coinc_window = 5e-9
afterpulse_window = 50e-9
min_interarrival = 1e-9

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
# REMOVE COINCIDENCES
# =========================
def remove_coincidences(ch1, ch2, window):

    i = 0
    j = 0

    remove1 = set()
    remove2 = set()

    while i < len(ch1) and j < len(ch2):

        diff = ch1[i] - ch2[j]

        if abs(diff) <= window:

            remove1.add(i)
            remove2.add(j)

            i += 1
            j += 1

        elif diff < 0:
            i += 1
        else:
            j += 1

    ch1_clean = np.delete(ch1, list(remove1))
    ch2_clean = np.delete(ch2, list(remove2))

    return ch1_clean, ch2_clean


ch1, ch2 = remove_coincidences(ch1, ch2, coinc_window)

print("After coincidence removal:")
print("Ch1 =", len(ch1))
print("Ch2 =", len(ch2))


# =========================
# REMOVE AFTERPULSING
# =========================
def remove_afterpulsing(channel_data, window):

    keep = [0]

    for i in range(1, len(channel_data)):

        if channel_data[i] - channel_data[keep[-1]] > window:
            keep.append(i)

    return channel_data[keep]


ch1 = remove_afterpulsing(ch1, afterpulse_window)
ch2 = remove_afterpulsing(ch2, afterpulse_window)

print("After afterpulse removal:")
print("Ch1 =", len(ch1))
print("Ch2 =", len(ch2))


# =========================
# REMOVE BURST EVENTS
# =========================
def remove_bursts(channel_data, threshold):

    diffs = np.diff(channel_data)

    mask = diffs > threshold

    keep = np.insert(mask, 0, True)

    return channel_data[keep]


ch1 = remove_bursts(ch1, min_interarrival)
ch2 = remove_bursts(ch2, min_interarrival)

print("After burst removal:")
print("Ch1 =", len(ch1))
print("Ch2 =", len(ch2))


# =========================
# SAVE CLEAN DATA
# =========================
clean_data = []

for t in ch1:
    clean_data.append([1, t])

for t in ch2:
    clean_data.append([2, t])

clean_data = np.array(clean_data)

np.savetxt(
    "ultra_cleaned_timestamps.csv",
    clean_data,
    fmt=["%d", "%.12e"],
    delimiter=","
)

print("Saved ultra_cleaned_timestamps.csv")