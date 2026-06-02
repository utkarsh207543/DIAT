# Load CCDF data
ccdf = pd.read_csv("BW6_ccdf.csv")

plt.figure(figsize=(6,4))

plt.semilogy(ccdf["Energy"], ccdf["CCDF"],
             linewidth=2,
             color="#1f77b4")

plt.axvline(SWH, color="red", linestyle="--", linewidth=2, label="SWH")
plt.axvline(RW,  color="blue", linestyle="--", linewidth=2, label="2.2×SWH")

plt.xlabel("Pulse energy (a.u.)")
plt.ylabel("CCDF  P(E ≥ E₀)")
plt.title("Heavy-tail CCDF (BW = 6 nm)")
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig("BW6_CCDF_RW.pdf")
plt.savefig("BW6_CCDF_RW.png", dpi=600)
plt.show()
