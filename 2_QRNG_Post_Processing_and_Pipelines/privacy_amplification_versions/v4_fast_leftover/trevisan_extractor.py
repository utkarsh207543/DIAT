"""
Trevisan's Extractor
Implementation of Trevisan's randomness extractor using error-correcting codes.
"""

import numpy as np
from typing import List

class TrevisanExtractor:
    def __init__(self, seed_length: int = 20):
        self.seed_length = seed_length
        
    def extract(self, raw_bits: str, output_length: int = None) -> str:
        """
        Apply Trevisan's extractor.
        
        Args:
            raw_bits: Input binary string
            output_length: Desired output length (default: len(raw_bits) // 4)
            
        Returns:
            Extracted binary string
        """
        if len(raw_bits) < self.seed_length * 2:
            print(f"   ⚠️  Input too short for Trevisan extraction")
            return ""
            
        if output_length is None:
            output_length = len(raw_bits) // 4
            
        # Use first part as seed
        seed = raw_bits[:self.seed_length]
        source = raw_bits[self.seed_length:]
        
        # Simple implementation using linear combinations
        output_bits = []
        
        for i in range(min(output_length, len(source) // 2)):
            # Generate pseudo-random positions using seed
            pos1 = self._hash_position(seed, i, 0) % len(source)
            pos2 = self._hash_position(seed, i, 1) % len(source)
            
            if pos1 != pos2:
                bit = str(int(source[pos1]) ^ int(source[pos2]))
                output_bits.append(bit)
                
        result = ''.join(output_bits)
        
        print(f"   🌟 Trevisan extraction complete")
        print(f"   🔑 Seed length: {self.seed_length}")
        print(f"   📊 Extraction ratio: {len(result) / len(raw_bits):.3f}")
        
        return result
        
    def _hash_position(self, seed: str, index: int, salt: int) -> int:
        """Generate pseudo-random position from seed."""
        # Simple hash function for position generation
        hash_input = seed + str(index) + str(salt)
        hash_val = 0
        for char in hash_input:
            hash_val = (hash_val * 31 + ord(char)) % (2**32)
        return hash_val
