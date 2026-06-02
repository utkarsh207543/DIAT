def flatten_binary_file(input_file, output_file):
    """
    Reads binary data line by line from input_file, removes newlines, and writes a single-line string to output_file.
    """
    with open(input_file, "r") as f:
        lines = f.readlines()

    # Remove newline characters and concatenate
    flattened = ''.join(line.strip() for line in lines if line.strip())

    with open(output_file, "w") as f:
        f.write(flattened)

# Example usage
flatten_binary_file("pl.txt", "output_binary.txt")
