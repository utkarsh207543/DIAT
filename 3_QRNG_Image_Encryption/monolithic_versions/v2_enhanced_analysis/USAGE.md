# Image Encryption & Security Analysis System - Usage Guide

## Quick Start (Default Files)

If you have the default files in the project directory:
- `mitu.png` (image to encrypt)
- `QRNG.txt` (random bits)

Simply run:
\`\`\`bash
python main.py
\`\`\`

Results will be saved to `results/` directory.

## Custom Configuration

You can specify custom paths for image, QRNG, and output directory:

### Example 1: Use different image
\`\`\`bash
python main.py --image path/to/your/image.png
\`\`\`

### Example 2: Use different QRNG file
\`\`\`bash
python main.py --qrng path/to/your/QRNG.txt
\`\`\`

### Example 3: Custom output directory
\`\`\`bash
python main.py --output path/to/save/results
\`\`\`

### Example 4: All custom paths
\`\`\`bash
python main.py --image path/to/image.png --qrng path/to/QRNG.txt --output path/to/results
\`\`\`

## Available Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--image` | Path to image file to encrypt | `mitu.png` |
| `--qrng` | Path to QRNG.txt file | `QRNG.txt` |
| `--output` | Directory to save results | `results/` |

## Output Files

The system generates the following files in the output directory:

### Key Stage Images
- `01_original.png` - Original image
- `02_encrypted_1.png` - Encrypted after block permutation
- `03_shuffled.png` - Image state after shuffling
- `04_encrypted_2_final.png` - Final encrypted image
- `05_decrypted.png` - Decrypted image
- `06_encrypted_differential.png` - Differential attack comparison

### Correlation Analysis
- `corr_orig_horizontal.png` - Original image horizontal correlation
- `corr_orig_vertical.png` - Original image vertical correlation
- `corr_orig_diagonal.png` - Original image diagonal correlation
- `corr_enc_horizontal.png` - Encrypted image horizontal correlation
- `corr_enc_vertical.png` - Encrypted image vertical correlation
- `corr_enc_diagonal.png` - Encrypted image diagonal correlation

### Histogram Analysis
- `hist_original.png` - Histogram of original image
- `hist_encrypted.png` - Histogram of encrypted image
- `hist_decrypted.png` - Histogram of decrypted image

### Metrics Report
- `metrics.txt` - Complete analysis report with all metrics

## Example Workflow

\`\`\`bash
# Encrypt image1.png with custom QRNG and save to results1/
python main.py --image images/image1.png --qrng keys/QRNG1.txt --output results1/

# Encrypt image2.png with custom QRNG and save to results2/
python main.py --image images/image2.png --qrng keys/QRNG2.txt --output results2/

# Use different image but default QRNG and output
python main.py --image myimage.jpg
\`\`\`

## Error Handling

If you get an error about missing files:

\`\`\`
ERROR: Image file not found: path/to/image.png
\`\`\`

Make sure the file path is correct and the file exists.

\`\`\`
ERROR: QRNG file not found: path/to/QRNG.txt
\`\`\`

Make sure QRNG.txt exists and the path is correct.

## Supported Image Formats

The system supports any image format that PIL can read:
- PNG (.png)
- JPG/JPEG (.jpg, .jpeg)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tif, .tiff)
- And others supported by PIL
