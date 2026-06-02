"""
Hashing-Based Extractors
Various cryptographic hash functions for randomness extraction.
"""

import hashlib
from math import floor

class HashingExtractors:
    def __init__(self, chunk_size: int = 512):
        self.chunk_size = chunk_size
        
    def sha256_extract(self, bitstring: str) -> str:
        """Extract randomness using SHA-256."""
        return self._hash_extract(bitstring, hashlib.sha256, 256, "SHA-256")
        
    def sha3_extract(self, bitstring: str) -> str:
        """Extract randomness using SHA-3."""
        return self._hash_extract(bitstring, hashlib.sha3_256, 256, "SHA-3")
        
    def blake2_extract(self, bitstring: str) -> str:
        """Extract randomness using BLAKE2."""
        return self._hash_extract(bitstring, hashlib.blake2b, 512, "BLAKE2")
        
    def _hash_extract(self, bitstring: str, hash_func, output_bits: int, name: str) -> str:
        """Generic hash-based extraction."""
        output_bits_str = ""
        usable_length = floor(len(bitstring) / self.chunk_size) * self.chunk_size
        chunks_processed = 0
        
        for i in range(0, usable_length, self.chunk_size):
            chunk = bitstring[i:i+self.chunk_size]
            
            # Convert binary string to bytes
            byte_data = int(chunk, 2).to_bytes(self.chunk_size // 8, byteorder='big')
            
            # Hash the bytes
            if hash_func == hashlib.blake2b:
                hash_obj = hash_func(byte_data, digest_size=output_bits // 8)
            else:
                hash_obj = hash_func(byte_data)
                
            hash_hex = hash_obj.hexdigest()
            
            # Convert hash to binary
            hash_bits = bin(int(hash_hex, 16))[2:].zfill(output_bits)
            output_bits_str += hash_bits
            chunks_processed += 1
            
        compression_ratio = len(output_bits_str) / len(bitstring) if bitstring else 0
        
        print(f"   🔐 {name} extraction complete")
        print(f"   📦 Processed {chunks_processed} chunks of {self.chunk_size} bits")
        print(f"   📊 Compression ratio: {compression_ratio:.3f}")
        
        return output_bits_str
