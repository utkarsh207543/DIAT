import pandas as pd

def process_qrng_with_threshold(input_file, output_file, threshold=10):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Filter valid data lines
    data_lines = [line for line in lines if not line.strip().startswith('%') and line.strip()]
    data = [list(map(int, line.strip().split())) for line in data_lines if len(line.strip().split()) >= 3]
    df = pd.DataFrame(data, columns=["ch1", "ch2", "ch3"])

    qrng_bits = []
    for ch1, ch2, _ in df.values:
        delta = ch1 - ch2
        if abs(delta) < threshold:
            continue  # Skip near-simultaneous events
        elif delta < 0:
            qrng_bits.append('0')
        else:
            qrng_bits.append('1')

    # Save result
    with open(output_file, "w") as f:
        f.write(''.join(qrng_bits))

# Example usage
process_qrng_with_threshold("Utkarsh_QRNG_10.txt", "QRNG_data_threshold.txt", threshold=10)
