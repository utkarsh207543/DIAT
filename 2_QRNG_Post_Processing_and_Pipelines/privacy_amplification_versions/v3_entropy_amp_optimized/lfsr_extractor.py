"""
Linear Feedback Shift Register (LFSR) Extractor
Uses LFSR sequences for randomness extraction and whitening.
"""

import numpy as np
from typing import List

class LFSRExtractor:
    def __init__(self, lfsr_length: int = 16):
        self.lfsr_length = lfsr_length
        # Primitive polynomial for 16-bit LFSR: x^16 + x^14 + x^13 + x^11 + 1
        self.taps = [16, 14, 13, 11]
        
    def extract(self, raw_bits: str) -> str:
        """
        Extract randomness using LFSR-based whitening.
        
        Args:
            raw_bits: Input binary string
            
        Returns:
            LFSR-processed binary string
        """
        if len(raw_bits) < self.lfsr_length:
            print(f"   ⚠️  Input too short for LFSR extraction")
            return ""
            
        # Initialize LFSR with first bits
        lfsr_state = [int(bit) for bit in raw_bits[:self.lfsr_length]]
        output_bits = []
        
        # Process remaining bits
        for i in range(self.lfsr_length, len(raw_bits)):
            input_bit = int(raw_bits[i])
            
            # Generate LFSR output bit
            lfsr_output = lfsr_state[-1]  # Output is the last bit
            
            # Calculate feedback bit
            feedback = 0
            for tap in self.taps:
                if tap <= len(lfsr_state):
                    feedback ^= lfsr_state[tap - 1]
                    
            # XOR input with LFSR output
            output_bit = input_bit ^ lfsr_output
            output_bits.append(str(output_bit))
            
            # Shift LFSR and insert feedback
            lfsr_state = [feedback] + lfsr_state[:-1]
            
        result = ''.join(output_bits)
        
        print(f"   🔄 LFSR extraction complete")
        print(f"   📏 LFSR length: {self.lfsr_length}")
        print(f"   🎯 Taps: {self.taps}")
        print(f"   📊 Processing efficiency: {len(result) / len(raw_bits):.3f}")
        
        return result
        
    def _galois_lfsr(self, state: List[int]) -> int:
        """Galois LFSR implementation for better performance."""
        output = state[-1]
        
        # Galois configuration
        new_state = [0] * len(state)
        new_state[0] = state[-1]  # Feedback
        
        for i in range(1, len(state)):
            new_state[i] = state[i-1]
            if i in [tap - 1 for tap in self.taps]:
                new_state[i] ^= state[-1]
                
        state[:] = new_state
        return output
