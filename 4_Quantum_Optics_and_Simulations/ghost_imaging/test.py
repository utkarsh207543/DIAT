import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv("test.csv", comment='%', names=["Source", "Timestamp"])

# Clean up Source column
df["Source"] = df["Source"].astype(str).str.replace(",", "").astype(int)

# Choose which channel(s) to plot
timestamps = df[df["Source"] == 1]["Timestamp"].values  # Use Ch1
# timestamps = df["Timestamp"].values  # Or use both Ch1 and Ch2

# Define time bin size and range
bin_width = 1e-9 # 1 µs
start_time = 0
end_time = np.max(timestamps)
bins = np.arange(start_time, end_time + bin_width, bin_width)

# Histogram: Counts vs Time
counts, edges = np.histogram(timestamps, bins=bins)
bin_centers = (edges[:-1] + edges[1:]) / 2

# Plot
plt.figure(figsize=(12, 5))
plt.plot(bin_centers * 1e6, counts, drawstyle='steps-mid', color='blue')  # µs scale
plt.xlabel("Time (µs)")
plt.ylabel("Counts per bin")
plt.title("Counts vs. Time Tags")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
