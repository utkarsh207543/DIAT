import numpy as np

# =========================
# SETTINGS
# =========================
filename = "A5.csv"
coinc_window = 5e-9   # coincidence window (5 ns typical)

# =========================
# LOAD CSV
# =========================
data = np.genfromtxt(filename, delimiter=',', comments='%')
data = data[~np.isnan(data).any(axis=1)]

channel = data[:, 0].astype(int)
timestamps = data[:, 1]

# Sort timestamps
sort_idx = np.argsort(timestamps)
timestamps = timestamps[sort_idx]
channel = channel[sort_idx]

# Split channels
ch1 = timestamps[channel == 1]
ch2 = timestamps[channel == 2]

print("Original counts:")
print("Ch1 =", len(ch1))
print("Ch2 =", len(ch2))

# =========================
# FIND COINCIDENCES
# =========================
i = 0
j = 0

remove_ch1 = set()
remove_ch2 = set()

while i < len(ch1) and j < len(ch2):

    diff = ch1[i] - ch2[j]

    if abs(diff) <= coinc_window:
        remove_ch1.add(i)
        remove_ch2.add(j)

        i += 1
        j += 1

    elif diff < 0:
        i += 1
    else:
        j += 1

# =========================
# REMOVE COINCIDENCES
# =========================
ch1_clean = np.delete(ch1, list(remove_ch1))
ch2_clean = np.delete(ch2, list(remove_ch2))

print("\nCoincidences removed:", len(remove_ch1))

print("\nCleaned counts:")
print("Ch1 =", len(ch1_clean))
print("Ch2 =", len(ch2_clean))

# =========================
# SAVE CLEAN DATA
# =========================
clean_data = []

for t in ch1_clean:
    clean_data.append([1, t])

for t in ch2_clean:
    clean_data.append([2, t])

clean_data = np.array(clean_data)

np.savetxt(
    "cleaned_timestamps.csv",
    clean_data,
    fmt=["%d", "%.12e"],
    delimiter=","
)

print("\nCleaned file saved as cleaned_timestamps.csv")