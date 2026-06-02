"""
Leftover Hash Lemma Extractor
Implementation based on universal hash functions and the leftover hash lemma.
"""

import numpy as np
import hashlib
from typing import List

class LeftoverHashExtractor:
    def __init__(self, output_length: int = None):
        self.output_length = output_length
        
    def extract(self, raw_bits: str) -> str:
        """
        Apply leftover hash lemma extraction using universal hashing.
        
        Args:
            raw_bits: Input binary string
            
        Returns:
            Extracted binary string
        """
        if len(raw_bits) < 64:
            print(f"   ⚠️  Input too short for LHL extraction")
            return ""
            
        # Determine output length based on min-entropy estimate
        if self.output_length is None:
            # Conservative estimate: assume min-entropy is 0.8 * input_length
            min_entropy = int(0.8 * len(raw_bits))
            self.output_length = min_entropy // 2  # Security parameter
            
        # Use Toeplitz matrix construction for universal hashing
        return self._toeplitz_extract(raw_bits)
        
    def _toeplitz_extract(self, source: str) -> str:
        """Extract using Toeplitz matrix multiplication."""
        n = len(source)
        m = min(self.output_length, n // 2)
        
        # Generate random Toeplitz matrix seed
        seed_length = n + m - 1
        np.random.seed(42)  # Fixed seed for reproducibility
        toeplitz_seed = np.random.randint(0, 2, seed_length)
        
        # Convert source to numpy array
        source_array = np.array([int(bit) for bit in source])
        
        # Perform Toeplitz matrix multiplication
        output_bits = []
        
        for i in range(m):
            # Compute dot product with i-th row of Toeplitz matrix
            row_sum = 0
            for j in range(n):
                row_sum ^= source_array[j] * toeplitz_seed[i + j]
            output_bits.append(str(row_sum % 2))
            
        result = ''.join(output_bits)
        
        print(f"   📊 Leftover Hash Lemma extraction complete")
        print(f"   🎯 Target output length: {self.output_length}")
        print(f"   📈 Actual output length: {len(result)}")
        
        return result
        
    def _universal_hash(self, data: str, hash_key: str) -> str:
        """Apply universal hash function."""
        # Combine data with hash key
        combined = data + hash_key
        
        # Use SHA-256 as underlying hash
        hash_obj = hashlib.sha256(combined.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to binary and truncate to desired length
        hash_bits = bin(int(hash_hex, 16))[2:].zfill(256)
        return hash_bits[:self.output_length]
