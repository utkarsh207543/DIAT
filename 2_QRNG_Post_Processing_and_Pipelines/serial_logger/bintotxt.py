INPUT_FILE = "qrng.bin"
OUTPUT_FILE = "qrng_bits.txt"


print("Reading binary file...")

with open(INPUT_FILE, "rb") as f:
    data = f.read()


print("Converting to bitstream...")

with open(OUTPUT_FILE, "w") as f:
    for byte in data:
        f.write(format(byte, "08b"))


print("Done ✅")
print(f"Saved ASCII bitstream to: {OUTPUT_FILE}")
print(f"Total bits written: {len(data) * 8:,}")