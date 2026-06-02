#!/usr/bin/env python3
"""
Run all QRNG post-processing techniques
Execute this script to process your QRNG data through all implemented techniques.
"""

from main_processor import QRNGPostProcessingSuite
import sys
import os

def main():
    # Check if input file is provided
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "Utkarsh_QRNG_10.txt"
        
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found!")
        print("Please ensure your QRNG data file is in the current directory.")
        return
        
    print("🚀 Starting QRNG Post-Processing Suite")
    print(f"📁 Input file: {input_file}")
    
    try:
        # Create and run processor
        processor = QRNGPostProcessingSuite(input_file)
        processor.process_all_techniques()
        
        print("\n🎉 Processing completed successfully!")
        print("\n📋 Next steps for NIST testing:")
        print("1. Navigate to the 'qrng_outputs' directory")
        print("2. Use the .bin files with the NIST Statistical Test Suite")
        print("3. Compare results across different techniques")
        print("4. Review the processing_summary.txt for detailed analysis")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
