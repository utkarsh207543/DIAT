import hashlib

# =========================
# SETTINGS
# =========================
input_csv = "cleaned_timestamps.csv"
output_file = "qrng_bits.txt"


# =========================
# LOAD TIMESTAMPS
# =========================
print("Reading timestamps...")

timestamps = []

with open(input_csv, "r") as f:

    for line in f:

        if line.startswith("%"):
            continue

        parts = line.strip().split(",")

        if len(parts) != 2:
            continue

        try:
            timestamps.append(float(parts[1]))
        except:
            continue


print("Loaded timestamps:", len(timestamps))


# =========================
# GENERATE RAW BITS
# =========================
print("Generating raw QRNG bits...")

raw_bits = []

for i in range(len(timestamps) - 1):

    dt = timestamps[i+1] - timestamps[i]

    parity = int((dt * 1e12) % 2)

    raw_bits.append(str(parity))


print("Raw bits:", len(raw_bits))


# =========================
# VON NEUMANN EXTRACTOR
# =========================
print("Applying Von Neumann extractor...")

vn_bits = []

for i in range(0, len(raw_bits) - 1, 2):

    pair = raw_bits[i] + raw_bits[i+1]

    if pair == "01":
        vn_bits.append("0")

    elif pair == "10":
        vn_bits.append("1")


print("After Von Neumann:", len(vn_bits))


# =========================
# SHA256 POST-PROCESSING
# =========================
print("Applying SHA256 hashing...")

block_size = 256
final_bits = ""

for i in range(0, len(vn_bits), block_size):

    block = vn_bits[i:i + block_size]

    if len(block) < block_size:
        break

    bit_string = "".join(block)

    byte_data = int(bit_string, 2).to_bytes(block_size // 8, "big")

    digest = hashlib.sha256(byte_data).digest()

    digest_bits = bin(int.from_bytes(digest, "big"))[2:].zfill(256)

    final_bits += digest_bits


print("Final secure bits:", len(final_bits))


# =========================
# SAVE OUTPUT
# =========================
with open(output_file, "a") as f:

    f.write(final_bits)


print("Saved to:", output_file)
print("Done ✅")