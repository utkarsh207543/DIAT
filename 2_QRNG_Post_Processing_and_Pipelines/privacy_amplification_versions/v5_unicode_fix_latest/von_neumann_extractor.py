"""
Von Neumann Extractor - Updated
Enhanced Von Neumann extractor with detailed statistics and quality metrics.
"""

class VonNeumannExtractor:
    def __init__(self):
        self.stats = {}
        
    def extract(self, raw_bits: str) -> str:
        """
        Apply Von Neumann extraction to remove bias.
        This will serve as the base for all other post-processing techniques.
        
        Args:
            raw_bits: Input binary string
            
        Returns:
            Debiased binary string
        """
        if len(raw_bits) < 2:
            print("   ⚠️  Insufficient data for Von Neumann extraction")
            return ""
            
        output_bits = []
        pair_stats = {'00': 0, '01': 0, '10': 0, '11': 0}
        discarded_pairs = 0
        accepted_pairs = 0
        
        print(f"   🔄 Processing {len(raw_bits):,} raw bits...")
        
        i = 0
        while i < len(raw_bits) - 1:
            a, b = raw_bits[i], raw_bits[i+1]
            pair = a + b
            pair_stats[pair] += 1
            
            if a != b:  # Accept different pairs
                output_bits.append(b)  # Use second bit
                accepted_pairs += 1
            else:  # Discard identical pairs
                discarded_pairs += 1
                
            i += 2
            
        result = ''.join(output_bits)
        
        # Calculate statistics
        total_pairs = accepted_pairs + discarded_pairs
        efficiency = accepted_pairs / total_pairs if total_pairs > 0 else 0
        compression_ratio = len(result) / len(raw_bits) if raw_bits else 0
        
        # Store statistics
        self.stats = {
            'input_bits': len(raw_bits),
            'output_bits': len(result),
            'total_pairs': total_pairs,
            'accepted_pairs': accepted_pairs,
            'discarded_pairs': discarded_pairs,
            'pair_distribution': pair_stats,
            'efficiency': efficiency,
            'compression_ratio': compression_ratio
        }
        
        # Print detailed results
        print(f"   📊 Von Neumann Extraction Results:")
        print(f"      Input bits: {len(raw_bits):,}")
        print(f"      Output bits: {len(result):,}")
        print(f"      Pairs processed: {total_pairs:,}")
        print(f"      Accepted pairs (01,10): {accepted_pairs:,}")
        print(f"      Discarded pairs (00,11): {discarded_pairs:,}")
        print(f"      Extraction efficiency: {efficiency:.3f}")
        print(f"      Compression ratio: {compression_ratio:.3f}")
        print(f"      Pair distribution: {pair_stats}")
        
        # Quality assessment
        if efficiency < 0.3:
            print(f"   ⚠️  Low efficiency - source may be heavily biased")
        elif efficiency > 0.6:
            print(f"   ✅ High efficiency - good source quality")
        else:
            print(f"   ℹ️  Moderate efficiency - acceptable source quality")
            
        return result
        
    def get_statistics(self) -> dict:
        """Return detailed extraction statistics."""
        return self.stats.copy()
        
    def extract_with_analysis(self, raw_bits: str) -> tuple:
        """
        Extract bits and return both result and detailed analysis.
        
        Returns:
            Tuple of (extracted_bits, analysis_dict)
        """
        result = self.extract(raw_bits)
        analysis = self.get_statistics()
        
        # Add additional analysis
        if result:
            from statistical_analyzer import StatisticalAnalyzer
            analyzer = StatisticalAnalyzer()
            bit_analysis = analyzer.analyze_bitstring(result)
            analysis['bit_analysis'] = bit_analysis
            
        return result, analysis
