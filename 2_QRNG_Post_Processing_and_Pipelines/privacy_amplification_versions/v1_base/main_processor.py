#!/usr/bin/env python3
"""
QRNG Post-Processing Suite
Comprehensive implementation of various randomness extraction techniques
for Quantum Random Number Generator data analysis and NIST test preparation.
"""

import os
import time
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

# Import all post-processing modules
from qrng_parser import QRNGParser
from von_neumann_extractor import VonNeumannExtractor
from hashing_extractors import HashingExtractors
from debiasing_algorithms import DebiasingAlgorithms
from trevisan_extractor import TrevisanExtractor
from leftover_hash_lemma import LeftoverHashExtractor
from lfsr_extractor import LFSRExtractor
from xor_combiner import XORCombiner
from statistical_analyzer import StatisticalAnalyzer

class QRNGPostProcessingSuite:
    def __init__(self, input_file: str, output_dir: str = "qrng_outputs"):
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize all extractors
        self.parser = QRNGParser()
        self.von_neumann = VonNeumannExtractor()
        self.hashing = HashingExtractors()
        self.debiasing = DebiasingAlgorithms()
        self.trevisan = TrevisanExtractor()
        self.leftover_hash = LeftoverHashExtractor()
        self.lfsr = LFSRExtractor()
        self.xor_combiner = XORCombiner()
        self.analyzer = StatisticalAnalyzer()
        
        self.results = {}
        
    def process_all_techniques(self):
        """Process QRNG data through all post-processing techniques."""
        print("🔬 QRNG Post-Processing Suite")
        print("=" * 50)
        
        # Step 1: Parse raw QRNG data
        print("\n📁 Step 1: Parsing QRNG Data...")
        raw_bits = self.parser.parse_qrng_file(self.input_file)
        self._save_and_analyze("01_raw_qrng", raw_bits, "Raw QRNG data")
        
        # Step 2: Von Neumann Extractor
        print("\n⚖️  Step 2: Von Neumann Extraction...")
        vn_bits = self.von_neumann.extract(raw_bits)
        self._save_and_analyze("02_von_neumann", vn_bits, "Von Neumann extracted")
        
        # Step 3: Hashing-Based Extractors
        print("\n🔐 Step 3: Hashing-Based Extractors...")
        
        # SHA-256
        sha256_bits = self.hashing.sha256_extract(raw_bits)
        self._save_and_analyze("03a_sha256", sha256_bits, "SHA-256 extracted")
        
        # SHA-3
        sha3_bits = self.hashing.sha3_extract(raw_bits)
        self._save_and_analyze("03b_sha3", sha3_bits, "SHA-3 extracted")
        
        # BLAKE2
        blake2_bits = self.hashing.blake2_extract(raw_bits)
        self._save_and_analyze("03c_blake2", blake2_bits, "BLAKE2 extracted")
        
        # Step 4: Debiasing Algorithms
        print("\n🎯 Step 4: Debiasing Algorithms...")
        
        # Peres debiasing
        peres_bits = self.debiasing.peres_debiasing(raw_bits)
        self._save_and_analyze("04a_peres", peres_bits, "Peres debiased")
        
        # Multi-bit debiasing
        multibit_bits = self.debiasing.multibit_debiasing(raw_bits)
        self._save_and_analyze("04b_multibit", multibit_bits, "Multi-bit debiased")
        
        # Adaptive debiasing
        adaptive_bits = self.debiasing.adaptive_debiasing(raw_bits)
        self._save_and_analyze("04c_adaptive", adaptive_bits, "Adaptive debiased")
        
        # Step 5: Trevisan's Extractor
        print("\n🌟 Step 5: Trevisan's Extractor...")
        trevisan_bits = self.trevisan.extract(raw_bits)
        self._save_and_analyze("05_trevisan", trevisan_bits, "Trevisan extracted")
        
        # Step 6: Leftover Hash Lemma
        print("\n📊 Step 6: Leftover Hash Lemma...")
        lhl_bits = self.leftover_hash.extract(raw_bits)
        self._save_and_analyze("06_leftover_hash", lhl_bits, "Leftover Hash extracted")
        
        # Step 7: LFSR-based extraction
        print("\n🔄 Step 7: LFSR Extraction...")
        lfsr_bits = self.lfsr.extract(raw_bits)
        self._save_and_analyze("07_lfsr", lfsr_bits, "LFSR extracted")
        
        # Step 8: XOR Combining with delays
        print("\n⊕ Step 8: XOR Combining...")
        xor_bits = self.xor_combiner.combine_delayed_streams(raw_bits)
        self._save_and_analyze("08_xor_combined", xor_bits, "XOR combined")
        
        # Step 9: Generate summary report
        print("\n📋 Step 9: Generating Summary Report...")
        self._generate_summary_report()
        
        print(f"\n✅ All processing complete! Results saved in '{self.output_dir}'")
        print("📊 Files are ready for NIST Statistical Test Suite analysis")
        
    def _save_and_analyze(self, filename: str, bits: str, description: str):
        """Save bits to file and perform basic analysis."""
        if not bits:
            print(f"⚠️  Warning: {description} produced no output bits")
            return
            
        # Save binary data for NIST tests
        filepath = self.output_dir / f"{filename}.bin"
        with open(filepath, 'w') as f:
            f.write(bits)
            
        # Perform analysis
        analysis = self.analyzer.analyze_bitstring(bits)
        self.results[filename] = {
            'description': description,
            'length': len(bits),
            'analysis': analysis,
            'filepath': filepath
        }
        
        print(f"   💾 Saved {len(bits):,} bits to {filename}.bin")
        print(f"   📈 Entropy: {analysis['entropy']:.6f}")
        print(f"   ⚖️  Balance: {analysis['balance']:.6f}")
        
    def _generate_summary_report(self):
        """Generate comprehensive summary report."""
        report_path = self.output_dir / "processing_summary.txt"
        
        with open(report_path, 'w') as f:
            f.write("QRNG Post-Processing Suite - Summary Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Input file: {self.input_file}\n")
            f.write(f"Processing time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Processing Results:\n")
            f.write("-" * 30 + "\n")
            
            for filename, result in self.results.items():
                f.write(f"\n{filename}:\n")
                f.write(f"  Description: {result['description']}\n")
                f.write(f"  Output length: {result['length']:,} bits\n")
                f.write(f"  Entropy: {result['analysis']['entropy']:.6f}\n")
                f.write(f"  Balance: {result['analysis']['balance']:.6f}\n")
                f.write(f"  File: {result['filepath'].name}\n")
                
        # Generate comparison plot
        self._generate_comparison_plot()
        
    def _generate_comparison_plot(self):
        """Generate comparison plots of all techniques."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        techniques = list(self.results.keys())
        lengths = [self.results[t]['length'] for t in techniques]
        entropies = [self.results[t]['analysis']['entropy'] for t in techniques]
        balances = [self.results[t]['analysis']['balance'] for t in techniques]
        
        # Output lengths
        ax1.bar(range(len(techniques)), lengths)
        ax1.set_title('Output Lengths by Technique')
        ax1.set_ylabel('Bits')
        ax1.set_xticks(range(len(techniques)))
        ax1.set_xticklabels([t.replace('_', '\n') for t in techniques], rotation=45, ha='right')
        
        # Entropy comparison
        ax2.bar(range(len(techniques)), entropies, color='green', alpha=0.7)
        ax2.set_title('Shannon Entropy by Technique')
        ax2.set_ylabel('Entropy (bits/bit)')
        ax2.set_ylim(0, 1)
        ax2.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Perfect entropy')
        ax2.set_xticks(range(len(techniques)))
        ax2.set_xticklabels([t.replace('_', '\n') for t in techniques], rotation=45, ha='right')
        ax2.legend()
        
        # Balance comparison
        ax3.bar(range(len(techniques)), balances, color='blue', alpha=0.7)
        ax3.set_title('Bit Balance by Technique')
        ax3.set_ylabel('Balance (0.5 = perfect)')
        ax3.set_ylim(0, 1)
        ax3.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Perfect balance')
        ax3.set_xticks(range(len(techniques)))
        ax3.set_xticklabels([t.replace('_', '\n') for t in techniques], rotation=45, ha='right')
        ax3.legend()
        
        # Efficiency (output/input ratio)
        if self.results:
            raw_length = self.results['01_raw_qrng']['length']
            efficiencies = [self.results[t]['length'] / raw_length for t in techniques]
            ax4.bar(range(len(techniques)), efficiencies, color='orange', alpha=0.7)
            ax4.set_title('Extraction Efficiency')
            ax4.set_ylabel('Output/Input Ratio')
            ax4.set_xticks(range(len(techniques)))
            ax4.set_xticklabels([t.replace('_', '\n') for t in techniques], rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "technique_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    # Process the QRNG data
    processor = QRNGPostProcessingSuite("Utkarsh_QRNG_10.txt")
    processor.process_all_techniques()
