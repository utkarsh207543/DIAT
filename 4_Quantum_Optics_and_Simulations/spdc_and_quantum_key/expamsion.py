import hashlib

INPUT_FILE = "qrng_bits.txt"
OUTPUT_FILE = "expanded_500MB_bits.txt"

TARGET_SIZE_MB = 500
TARGET_BITS = TARGET_SIZE_MB * 1024 * 1024 * 8


def read_seed_bits(filename):
    with open(filename, "r") as f:
        data = f.read()

    # keep only valid bits
    data = ''.join(c for c in data if c in "01")
    return data


def sha256_expand(seed_bits, target_bits):

    seed_bytes = seed_bits.encode()
    output_bits = ""

    counter = 0

    while len(output_bits) < target_bits:

        counter_bytes = counter.to_bytes(8, 'big')

        digest = hashlib.sha256(seed_bytes + counter_bytes).digest()

        # convert digest to bitstring
        bits = ''.join(f"{byte:08b}" for byte in digest)

        output_bits += bits

        counter += 1

        if counter % 10000 == 0:
            print(f"Generated {len(output_bits)//8/1024/1024:.2f} MB")

    return output_bits[:target_bits]


def save_bits(bits, filename):

    with open(filename, "w") as f:
        f.write(bits)


def main():

    print("Reading QRNG seed...")
    seed = read_seed_bits(INPUT_FILE)

    print(f"Seed length: {len(seed)} bits")

    print("Expanding with SHA-256 counter mode...")

    expanded = sha256_expand(seed, TARGET_BITS)

    print("Saving output...")

    save_bits(expanded, OUTPUT_FILE)

    print("Done ✅ 500 MB bitstream generated.")


if __name__ == "__main__":
    main()