#!/usr/bin/env python3
"""
QRNG Pipeline Runner
Execute the complete QRNG post-processing pipeline following the specified workflow.
"""

from main_processor import QRNGPostProcessingSuite
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='QRNG Post-Processing Pipeline')
    parser.add_argument('input_file', nargs='?', default='Utkarsh_QRNG_10.txt',
                       help='Input QRNG data file (default: Utkarsh_QRNG_10.txt)')
    parser.add_argument('--output-dir', default='qrng_outputs',
                       help='Output directory (default: qrng_outputs)')
    parser.add_argument('--target-bits', type=int, default=500000,
                       help='Target bits per technique (default: 500000)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found!")
        print("Please ensure your QRNG data file is in the current directory.")
        print("\nUsage examples:")
        print(f"  python {sys.argv[0]} your_qrng_file.txt")
        print(f"  python {sys.argv[0]} --target-bits 1000000 your_file.txt")
        return 1
        
    print("🚀 QRNG Post-Processing Pipeline")
    print("=" * 50)
    print(f"📁 Input file: {args.input_file}")
    print(f"📂 Output directory: {args.output_dir}")
    print(f"🎯 Target bits per technique: {args.target_bits:,}")
    print("\n🔄 Pipeline workflow:")
    print("1. Read raw data → Save Raw_QRNG.txt")
    print("2. Apply Von Neumann debiasing → Save base")
    print("3. Apply all techniques to debiased base")
    print("4. Entropy amplification to target bits")
    print("5. Save with postprocessing names")
    
    try:
        # Create and run processor
        processor = QRNGPostProcessingSuite(
            input_file=args.input_file,
            output_dir=args.output_dir,
            target_bits=args.target_bits
        )
        processor.process_qrng_pipeline()
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"\n📋 Output files in '{args.output_dir}':")
        print("   • Raw_QRNG.txt - Original parsed data")
        print("   • VonNeumann_Debiased_Base.txt - Debiased base")
        print("   • [Technique]_500K.txt/.bin - Final results")
        print("   • Processing_Pipeline_Report.txt - Analysis")
        print("   • Pipeline_Analysis_Report.png - Visualizations")
        print("\n🧪 Next steps:")
        print("1. Use .bin files with NIST Statistical Test Suite")
        print("2. Compare randomness quality across techniques")
        print("3. Review the pipeline report for detailed analysis")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
