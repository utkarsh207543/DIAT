#!/usr/bin/env python3
"""
QRNG Post-Processing Suite - Updated Workflow
1. Read raw data → Save raw QRNG file
2. Apply Von Neumann debiasing → Save debiased base
3. Apply all techniques to debiased data
4. Entropy amplification to 500K bits each
5. Save with postprocessing names
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
from entropy_amplifier import EntropyAmplifier
from statistical_analyzer import StatisticalAnalyzer

class QRNGPostProcessingSuite:
    def __init__(self, input_file: str, output_dir: str = "qrng_outputs", target_bits: int = 500000):
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.target_bits = target_bits  # 500K bits target
        
        # Initialize all processors
        self.parser = QRNGParser()
        self.von_neumann = VonNeumannExtractor()
        self.hashing = HashingExtractors()
        self.debiasing = DebiasingAlgorithms()
        self.trevisan = TrevisanExtractor()
        self.leftover_hash = LeftoverHashExtractor()
        self.lfsr = LFSRExtractor()
        self.xor_combiner = XORCombiner()
        self.amplifier = EntropyAmplifier()
        self.analyzer = StatisticalAnalyzer()
        
        self.results = {}
        
    def process_qrng_pipeline(self):
        """Execute the complete QRNG processing pipeline."""
        print("🔬 QRNG Post-Processing Pipeline")
        print("=" * 60)
        print(f"🎯 Target output: {self.target_bits:,} bits per technique")
        print(f"📁 Input file: {self.input_file}")
        print(f"📂 Output directory: {self.output_dir}")
        
        # Step 1: Read and save raw data
        print("\n" + "="*60)
        print("📖 STEP 1: Reading Raw QRNG Data")
        print("="*60)
        raw_bits = self.parser.parse_qrng_file(self.input_file)
        self._save_raw_data(raw_bits)
        
        # Step 2: Von Neumann debiasing (base for all other techniques)
        print("\n" + "="*60)
        print("⚖️  STEP 2: Von Neumann Debiasing (Base Processing)")
        print("="*60)
        debiased_base = self.von_neumann.extract(raw_bits)
        self._save_debiased_base(debiased_base)
        
        if len(debiased_base) < 1000:
            print("❌ Error: Insufficient debiased data for further processing")
            return
            
        # Step 3: Apply all post-processing techniques to debiased base
        print("\n" + "="*60)
        print("🔧 STEP 3: Applying Post-Processing Techniques")
        print("="*60)
        
        techniques = [
            ("SHA256", lambda x: self.hashing.sha256_extract(x)),
            ("SHA3", lambda x: self.hashing.sha3_extract(x)),
            ("BLAKE2", lambda x: self.hashing.blake2_extract(x)),
            ("Peres", lambda x: self.debiasing.peres_debiasing(x)),
            ("MultibitDebiasing", lambda x: self.debiasing.multibit_debiasing(x)),
            ("AdaptiveDebiasing", lambda x: self.debiasing.adaptive_debiasing(x)),
            ("TrevisanExtractor", lambda x: self.trevisan.extract(x)),
            ("LeftoverHashLemma", lambda x: self.leftover_hash.extract(x)),
            ("LFSRExtractor", lambda x: self.lfsr.extract(x)),
            ("XORCombiner", lambda x: self.xor_combiner.combine_delayed_streams(x)),
            ("FibonacciXOR", lambda x: self.xor_combiner.fibonacci_xor_combine(x)),
            ("AdaptiveXOR", lambda x: self.xor_combiner.adaptive_xor_combine(x))
        ]
        
        processed_data = {}
        
        for name, technique_func in techniques:
            print(f"\n🔄 Processing: {name}")
            try:
                processed_bits = technique_func(debiased_base)
                if processed_bits:
                    processed_data[name] = processed_bits
                    print(f"   ✅ {name}: {len(processed_bits):,} bits generated")
                else:
                    print(f"   ⚠️  {name}: No output generated")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
                
        # Step 4: Entropy amplification to 500K bits
        print("\n" + "="*60)
        print("🚀 STEP 4: Entropy Amplification to 500K Bits")
        print("="*60)
        
        final_results = {}
        
        for name, bits in processed_data.items():
            print(f"\n🔧 Amplifying {name}...")
            try:
                amplified_bits = self.amplifier.amplify_to_target(bits, self.target_bits)
                if len(amplified_bits) >= self.target_bits:
                    # Truncate to exact target
                    final_bits = amplified_bits[:self.target_bits]
                    final_results[name] = final_bits
                    print(f"   ✅ {name}: {len(final_bits):,} bits ready")
                else:
                    print(f"   ⚠️  {name}: Only {len(amplified_bits):,} bits generated")
                    final_results[name] = amplified_bits
            except Exception as e:
                print(f"   ❌ {name}: Amplification failed - {e}")
                
        # Step 5: Save final results with postprocessing names
        print("\n" + "="*60)
        print("💾 STEP 5: Saving Final Results")
        print("="*60)
        
        for name, bits in final_results.items():
            self._save_final_result(name, bits)
            
        # Step 6: Generate analysis report
        print("\n" + "="*60)
        print("📊 STEP 6: Generating Analysis Report")
        print("="*60)
        self._generate_final_report(final_results)
        
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"📁 All files saved in: {self.output_dir}")
        print(f"🧪 Ready for NIST Statistical Test Suite analysis")
        
    def _save_raw_data(self, raw_bits: str):
        """Save raw QRNG data."""
        filepath = self.output_dir / "Raw_QRNG.txt"
        with open(filepath, 'w') as f:
            f.write(raw_bits)
            
        print(f"💾 Raw QRNG data saved: {len(raw_bits):,} bits")
        print(f"📁 File: {filepath}")
        
        # Basic analysis
        analysis = self.analyzer.analyze_bitstring(raw_bits)
        print(f"📈 Raw data entropy: {analysis['entropy']:.6f}")
        print(f"⚖️  Raw data balance: {analysis['balance']:.6f}")
        
    def _save_debiased_base(self, debiased_bits: str):
        """Save Von Neumann debiased base data."""
        filepath = self.output_dir / "VonNeumann_Debiased_Base.txt"
        with open(filepath, 'w') as f:
            f.write(debiased_bits)
            
        print(f"💾 Debiased base saved: {len(debiased_bits):,} bits")
        print(f"📁 File: {filepath}")
        
        # Analysis
        analysis = self.analyzer.analyze_bitstring(debiased_bits)
        print(f"📈 Debiased entropy: {analysis['entropy']:.6f}")
        print(f"⚖️  Debiased balance: {analysis['balance']:.6f}")
        
        # This will be used as input for all other techniques
        self.debiased_base_analysis = analysis
        
    def _save_final_result(self, technique_name: str, bits: str):
        """Save final processed result with technique name."""
        filepath = self.output_dir / f"{technique_name}_500K.txt"
        
        with open(filepath, 'w') as f:
            f.write(bits)
            
        # Also save as .bin for NIST compatibility
        bin_filepath = self.output_dir / f"{technique_name}_500K.bin"
        with open(bin_filepath, 'w') as f:
            f.write(bits)
            
        print(f"💾 {technique_name}: {len(bits):,} bits saved")
        print(f"📁 Files: {filepath.name}, {bin_filepath.name}")
        
        # Quick analysis
        analysis = self.analyzer.analyze_bitstring(bits)
        print(f"   📈 Entropy: {analysis['entropy']:.6f}")
        print(f"   ⚖️  Balance: {analysis['balance']:.6f}")
        
        # Store for report
        self.results[technique_name] = {
            'bits': len(bits),
            'analysis': analysis,
            'files': [filepath.name, bin_filepath.name]
        }
        
    def _generate_final_report(self, final_results: Dict[str, str]):
        """Generate comprehensive final report."""
        report_path = self.output_dir / "Processing_Pipeline_Report.txt"
        
        with open(report_path, 'w') as f:
            f.write("QRNG POST-PROCESSING PIPELINE REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Input file: {self.input_file}\n")
            f.write(f"Processing time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target bits per technique: {self.target_bits:,}\n\n")
            
            f.write("PIPELINE WORKFLOW:\n")
            f.write("-" * 30 + "\n")
            f.write("1. Raw QRNG data parsed and saved\n")
            f.write("2. Von Neumann debiasing applied (base for all techniques)\n")
            f.write("3. All post-processing techniques applied to debiased base\n")
            f.write("4. Entropy amplification to 500K bits per technique\n")
            f.write("5. Final results saved with technique names\n\n")
            
            f.write("FINAL RESULTS SUMMARY:\n")
            f.write("-" * 30 + "\n")
            
            for technique, result in self.results.items():
                f.write(f"\n{technique}:\n")
                f.write(f"  Output bits: {result['bits']:,}\n")
                f.write(f"  Entropy: {result['analysis']['entropy']:.6f}\n")
                f.write(f"  Balance: {result['analysis']['balance']:.6f}\n")
                f.write(f"  Files: {', '.join(result['files'])}\n")
                
            f.write(f"\nNIST TEST PREPARATION:\n")
            f.write("-" * 30 + "\n")
            f.write("All .bin files are ready for NIST Statistical Test Suite\n")
            f.write("Each file contains exactly 500,000 bits (unless insufficient source data)\n")
            f.write("Use these files to compare randomness quality across techniques\n")
            
        print(f"📋 Final report saved: {report_path}")
        
        # Generate comparison visualization
        self._generate_comparison_plots(final_results)
        
    def _generate_comparison_plots(self, final_results: Dict[str, str]):
        """Generate comparison plots."""
        if not final_results:
            return
            
        techniques = list(self.results.keys())
        entropies = [self.results[t]['analysis']['entropy'] for t in techniques]
        balances = [self.results[t]['analysis']['balance'] for t in techniques]
        bit_counts = [self.results[t]['bits'] for t in techniques]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Entropy comparison
        bars1 = ax1.bar(range(len(techniques)), entropies, color='green', alpha=0.7)
        ax1.set_title('Shannon Entropy by Post-Processing Technique', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Entropy (bits/bit)')
        ax1.set_ylim(0.95, 1.0)
        ax1.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Perfect entropy')
        ax1.set_xticks(range(len(techniques)))
        ax1.set_xticklabels(techniques, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, entropy in zip(bars1, entropies):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{entropy:.4f}', ha='center', va='bottom', fontsize=8)
        
        # Balance comparison
        bars2 = ax2.bar(range(len(techniques)), balances, color='blue', alpha=0.7)
        ax2.set_title('Bit Balance by Post-Processing Technique', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Balance (0.5 = perfect)')
        ax2.set_ylim(0.45, 0.55)
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Perfect balance')
        ax2.set_xticks(range(len(techniques)))
        ax2.set_xticklabels(techniques, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, balance in zip(bars2, balances):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.002,
                    f'{balance:.4f}', ha='center', va='bottom', fontsize=8)
        
        # Output bit counts
        bars3 = ax3.bar(range(len(techniques)), bit_counts, color='orange', alpha=0.7)
        ax3.set_title('Output Bit Counts by Technique', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Number of Bits')
        ax3.axhline(y=self.target_bits, color='red', linestyle='--', alpha=0.7, 
                   label=f'Target: {self.target_bits:,} bits')
        ax3.set_xticks(range(len(techniques)))
        ax3.set_xticklabels(techniques, rotation=45, ha='right')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Quality score (entropy * balance proximity)
        quality_scores = [entropy * (1 - abs(balance - 0.5) * 2) 
                         for entropy, balance in zip(entropies, balances)]
        bars4 = ax4.bar(range(len(techniques)), quality_scores, color='purple', alpha=0.7)
        ax4.set_title('Overall Quality Score (Entropy × Balance)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Quality Score')
        ax4.set_xticks(range(len(techniques)))
        ax4.set_xticklabels(techniques, rotation=45, ha='right')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "Pipeline_Analysis_Report.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Analysis plots saved: Pipeline_Analysis_Report.png")

if __name__ == "__main__":
    import sys
    
    # Get input file from command line or use default
    input_file = sys.argv[1] if len(sys.argv) > 1 else "Utkarsh_QRNG_10.txt"
    
    # Create and run processor
    processor = QRNGPostProcessingSuite(input_file)
    processor.process_qrng_pipeline()
