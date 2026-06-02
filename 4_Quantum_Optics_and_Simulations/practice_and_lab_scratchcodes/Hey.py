import os
import random
from tqdm import tqdm  # Make sure you have tqdm installed: pip install tqdm

def generate_random_binary_file(filename, size_in_mb):
    size_in_bytes = size_in_mb * 1024 * 1024
    chunk_size = 1024 * 1024  # 1 MB per chunk
    total_chunks = size_in_bytes // chunk_size

    with open(filename, 'w') as f, tqdm(total=total_chunks, unit='MB', desc="Generating File") as pbar:
        for _ in range(total_chunks):
            chunk = ''.join(random.choices('01', k=chunk_size))
            f.write(chunk)
            pbar.update(1)

    print(f"\n✅ File '{filename}' generated with size approximately {size_in_mb} MB.")

# Prompt user for size input
try:
    user_input = int(input("Enter desired file size in MB: "))
    generate_random_binary_file("random_binary.txt", user_input)
except ValueError:
    print("❌ Please enter a valid integer value for file size.")
