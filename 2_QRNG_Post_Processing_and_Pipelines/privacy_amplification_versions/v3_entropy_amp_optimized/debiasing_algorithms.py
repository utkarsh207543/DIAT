"""
Advanced Debiasing Algorithms
Implementation of various debiasing techniques beyond Von Neumann.
"""

import numpy as np
from typing import List

class DebiasingAlgorithms:
    def __init__(self):
        pass
        
    def peres_debiasing(self, raw_bits: str) -> str:
        """
        Peres debiasing algorithm - more efficient than Von Neumann.
        Processes bits in groups of 3.
        """
        output_bits = []
        i = 0
        
        while i < len(raw_bits) - 2:
            a, b, c = raw_bits[i], raw_bits[i+1], raw_bits[i+2]
            
            # Peres extraction rules
            if a == b and b != c:
                output_bits.append(c)
            elif a != b and b == c:
                output_bits.append(a)
            # Discard other combinations
            
            i += 3
            
        result = ''.join(output_bits)
        efficiency = len(result) / (len(raw_bits) // 3) if raw_bits else 0
        
        print(f"   🎯 Peres debiasing complete")
        print(f"   📈 Extraction efficiency: {efficiency:.3f}")
        
        return result
        
    def multibit_debiasing(self, raw_bits: str, block_size: int = 4) -> str:
        """
        Multi-bit debiasing using block-based approach.
        """
        output_bits = []
        
        for i in range(0, len(raw_bits) - block_size + 1, block_size):
            block = raw_bits[i:i+block_size]
            
            # Count ones and zeros
            ones = block.count('1')
            zeros = block.count('0')
            
            # Extract based on majority with tie-breaking
            if ones > zeros:
                output_bits.append('1')
            elif zeros > ones:
                output_bits.append('0')
            # Discard ties
            
        result = ''.join(output_bits)
        compression_ratio = len(result) / len(raw_bits) if raw_bits else 0
        
        print(f"   🔢 Multi-bit debiasing complete (block size: {block_size})")
        print(f"   📊 Compression ratio: {compression_ratio:.3f}")
        
        return result
        
    def adaptive_debiasing(self, raw_bits: str, window_size: int = 1000) -> str:
        """
        Adaptive debiasing that adjusts based on local bias estimation.
        """
        output_bits = []
        
        for i in range(0, len(raw_bits) - 1, 2):
            # Estimate local bias in sliding window
            start = max(0, i - window_size // 2)
            end = min(len(raw_bits), i + window_size // 2)
            window = raw_bits[start:end]
            
            if len(window) > 0:
                bias = window.count('1') / len(window)
                
                # Apply Von Neumann if bias is significant
                if abs(bias - 0.5) > 0.1:  # Threshold for bias detection
                    a, b = raw_bits[i], raw_bits[i+1]
                    if a != b:
                        output_bits.append(b)
                else:
                    # Use direct bits if unbiased
                    output_bits.append(raw_bits[i])
                    
        result = ''.join(output_bits)
        
        print(f"   🎯 Adaptive debiasing complete (window: {window_size})")
        print(f"   📈 Output length: {len(result)}")
        
        return result
