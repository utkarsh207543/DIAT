def load_qrng_bits(filename):
    """
    Load threshold-filtered QRNG binary data from file and return as a string.
    """
    with open(filename, "r") as f:
        bits = f.read().strip()
    return bits

def save_as_txt_file(bits, output_filename):
    """
    Save QRNG binary string as 8-bit chunks (bytes) line-by-line to a .txt file.
    """
    with open(output_filename, "w") as f:
        for i in range(0, len(bits), 8):
            byte_chunk = bits[i:i+8]
            if len(byte_chunk) == 8:
                f.write(byte_chunk)

# --- Main Execution ---
if __name__ == "__main__":
    input_file = "QRNG_data_threshold.txt"
    output_file = "QRNG_output.txt"

    # Load QRNG bits from file
    qrng_bits = load_qrng_bits(input_file)

    # Save to QRNG_output.txt in byte-wise format
    save_as_txt_file(qrng_bits, output_file)

    print(f"QRNG data loaded from: {input_file}")
    print(f"Total bits loaded: {len(qrng_bits)}")
    print(f"Saved byte-wise QRNG output to: {output_file}")
