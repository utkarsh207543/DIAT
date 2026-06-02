def concatenate_binary_file(input_file, output_file):
    binary_string = ""

    # Read the input file line by line
    with open(input_file, 'r') as f:
        for line in f:
            binary_string += line.strip()  # remove newline and whitespace

    # Save to output file
    with open(output_file, 'w') as f:
        f.write(binary_string)

    print("Concatenated binary string:")
    print(binary_string)

# Example usage
concatenate_binary_file("input_binary.txt", "output_binary.txt")
