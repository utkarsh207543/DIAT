"""
Von Neumann Extractor
Classic debiasing algorithm that removes bias by comparing consecutive bit pairs.
"""

class VonNeumannExtractor:
    def __init__(self):
        pass
        
    def extract(self, raw_bits: str) -> str:
        """
        Apply Von Neumann extraction to remove bias.
        
        Args:
            raw_bits: Input binary string
            
        Returns:
            Debiased binary string
        """
        output_bits = []
        discarded_pairs = 0
        
        i = 0
        while i < len(raw_bits) - 1:
            a, b = raw_bits[i], raw_bits[i+1]
            if a != b:
                output_bits.append(b)
            else:
                discarded_pairs += 1
            i += 2
            
        result = ''.join(output_bits)
        efficiency = len(result) / (len(raw_bits) // 2) if raw_bits else 0
        
        print(f"   🎯 Von Neumann extraction complete")
        print(f"   📉 Discarded {discarded_pairs} identical pairs")
        print(f"   📈 Extraction efficiency: {efficiency:.3f}")
        
        return result
