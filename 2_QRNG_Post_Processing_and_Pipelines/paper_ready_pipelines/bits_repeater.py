import os

def repeat_bits_to_length(input_file, output_file, min_length=400_000):
    # Step 1: Read original bitstring
    with open(input_file, 'r') as f:
        original_bits = f.read().strip()

    original_len = len(original_bits)
    if original_len == 0:
        print("❌ Error: Input bitstring is empty.")
        return

    # Step 2: Calculate repetitions
    repeats = (min_length + original_len - 1) // original_len
    repeated_bits = (original_bits * repeats)[:min_length]

    # Step 3: Write to new file
    with open(output_file, 'w') as f:
        f.write(repeated_bits)

    print(f"✅ Padded file saved to '{output_file}' with {len(repeated_bits)} bits.")
    print(f"Original bitstream length: {original_len} | Repeated {repeats}x")

# Usage
repeat_bits_to_length("qrng_sha256_extracted_bits.txt", "qrng_sha256_padded_400k.txt")
