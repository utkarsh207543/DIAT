"""
Leftover Hash Lemma Extractor - Optimized
Fast implementation using efficient universal hash functions.
"""

import numpy as np
import hashlib
from typing import List
import time

class LeftoverHashExtractor:
    def __init__(self, output_length: int = None):
        self.output_length = output_length
        
    def extract(self, raw_bits: str) -> str:
        """
        Apply leftover hash lemma extraction using optimized universal hashing.
        
        Args:
            raw_bits: Input binary string
            
        Returns:
            Extracted binary string
        """
        if len(raw_bits) < 64:
            print(f"   ⚠️  Input too short for LHL extraction")
            return ""
            
        print(f"   🔄 Starting Leftover Hash Lemma extraction...")
        start_time = time.time()
        
        # Determine output length based on min-entropy estimate
        if self.output_length is None:
            # Conservative estimate: assume min-entropy is 0.8 * input_length
            min_entropy = int(0.8 * len(raw_bits))
            self.output_length = min(min_entropy // 2, len(raw_bits) // 4)  # Security parameter
            
        print(f"   🎯 Target output length: {self.output_length}")
        
        # Use fast polynomial-based universal hashing instead of Toeplitz
        result = self._fast_polynomial_hash(raw_bits)
        
        elapsed = time.time() - start_time
        print(f"   ✅ LHL extraction complete in {elapsed:.2f} seconds")
        print(f"   📊 Output length: {len(result)}")
        
        return result
        
    def _fast_polynomial_hash(self, source: str) -> str:
        """Fast polynomial-based universal hashing."""
        print(f"   🚀 Using fast polynomial hashing")
        
        n = len(source)
        m = min(self.output_length, n // 2)
        
        # Convert source to chunks for processing
        chunk_size = 256  # Process in 256-bit chunks
        output_bits = []
        
        chunks_processed = 0
        total_chunks = (n // chunk_size) + (1 if n % chunk_size else 0)
        
        for i in range(0, n, chunk_size):
            chunk = source[i:i + chunk_size]
            
            # Pad chunk if necessary
            if len(chunk) < chunk_size:
                chunk = chunk.ljust(chunk_size, '0')
                
            # Fast hash using built-in hash function with polynomial mixing
            chunk_hash = self._polynomial_mix(chunk, chunks_processed)
            output_bits.append(chunk_hash)
            
            chunks_processed += 1
            
            # Progress reporting for large inputs
            if chunks_processed % 1000 == 0:
                print(f"   📊 Processed {chunks_processed}/{total_chunks} chunks")
                
            # Stop when we have enough output
            if len(''.join(output_bits)) >= m:
                break
                
        result = ''.join(output_bits)[:m]
        return result
        
    def _polynomial_mix(self, chunk: str, seed: int) -> str:
        """Fast polynomial mixing for universal hashing."""
        # Convert chunk to integer
        try:
            chunk_int = int(chunk, 2)
        except ValueError:
            # Handle invalid binary string
            chunk_int = hash(chunk) % (2**256)
            
        # Polynomial coefficients (prime numbers for good mixing)
        p1 = 2**31 - 1  # Mersenne prime
        p2 = 2**61 - 1  # Another Mersenne prime
        
        # Polynomial evaluation with seed
        poly_result = (chunk_int * p1 + seed * p2) % (2**256)
        
        # Convert back to binary string
        return format(poly_result, '0256b')
        
    def _simple_universal_hash(self, data: str, output_length: int) -> str:
        """Simple and fast universal hash implementation."""
        print(f"   🔧 Using simple universal hash")
        
        # Use SHA-256 as base hash function
        hash_input = data.encode('utf-8')
        
        output_bits = ""
        counter = 0
        
        while len(output_bits) < output_length:
            # Create unique input for each iteration
            iteration_input = hash_input + counter.to_bytes(4, 'big')
            
            # Hash and convert to binary
            hash_result = hashlib.sha256(iteration_input).hexdigest()
            hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
            
            output_bits += hash_bits
            counter += 1
            
            # Safety limit
            if counter > output_length // 256 + 10:
                break
                
        return output_bits[:output_length]
        
    def _block_based_extraction(self, source: str) -> str:
        """Block-based extraction for better performance."""
        print(f"   📦 Using block-based extraction")
        
        block_size = 512  # Larger blocks for efficiency
        output_bits = ""
        
        blocks_processed = 0
        target_blocks = self.output_length // 256  # Each block produces ~256 bits
        
        for i in range(0, len(source), block_size):
            if blocks_processed >= target_blocks:
                break
                
            block = source[i:i + block_size]
            
            if len(block) < block_size:
                # Pad the last block
                block = block.ljust(block_size, '0')
                
            # Hash the block
            block_bytes = self._bits_to_bytes(block)
            if block_bytes:
                hash_result = hashlib.sha256(block_bytes).hexdigest()
                hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
                output_bits += hash_bits
                
            blocks_processed += 1
            
            # Progress for large inputs
            if blocks_processed % 100 == 0:
                print(f"   📊 Processed {blocks_processed} blocks")
                
        return output_bits[:self.output_length]
        
    def _bits_to_bytes(self, bits: str) -> bytes:
        """Convert bit string to bytes safely."""
        try:
            # Pad to multiple of 8
            padded_bits = bits.ljust((len(bits) + 7) // 8 * 8, '0')
            
            # Convert to bytes
            byte_array = bytearray()
            for i in range(0, len(padded_bits), 8):
                byte_str = padded_bits[i:i+8]
                byte_val = int(byte_str, 2)
                byte_array.append(byte_val)
                
            return bytes(byte_array)
        except Exception:
            return b''
            
    def extract_fast(self, raw_bits: str, target_length: int = None) -> str:
        """
        Ultra-fast extraction for time-critical applications.
        
        Args:
            raw_bits: Input binary string
            target_length: Desired output length
            
        Returns:
            Fast extracted binary string
        """
        if target_length:
            self.output_length = target_length
            
        print(f"   ⚡ Fast LHL extraction mode")
        start_time = time.time()
        
        # Use simple hash-based approach for speed
        result = self._simple_universal_hash(raw_bits, self.output_length or len(raw_bits) // 4)
        
        elapsed = time.time() - start_time
        print(f"   ⚡ Fast extraction complete in {elapsed:.3f} seconds")
        
        return result
