"""
Entropy Amplifier - Enhanced
Improved amplification with better progress reporting and quality control.
"""

import hashlib
import numpy as np
from typing import List
import itertools

class EntropyAmplifier:
    def __init__(self):
        self.chunk_size = 256  # Process in 256-bit chunks
        
    def amplify_to_target(self, source_bits: str, target_bits: int) -> str:
        """
        Amplify entropy to reach exact target bit count with safe integer handling.
        
        Args:
            source_bits: Input binary string
            target_bits: Target number of output bits
            
        Returns:
            Amplified binary string of target length
        """
        if not source_bits:
            print(f"   No source bits provided for amplification")
            return ""
            
        print(f"   Amplifying {len(source_bits):,} -> {target_bits:,} bits")
        
        # If we already have enough bits, truncate to exact target
        if len(source_bits) >= target_bits:
            print(f"   Truncating to exact target length")
            return source_bits[:target_bits]
            
        # Calculate amplification factor needed
        amplification_factor = target_bits / len(source_bits)
        print(f"   Amplification factor: {amplification_factor:.2f}x")
        
        # Choose amplification strategy based on factor
        if amplification_factor <= 2:
            result = self._hash_expansion_safe(source_bits, target_bits)
        elif amplification_factor <= 10:
            result = self._iterative_hashing_safe(source_bits, target_bits)
        else:
            result = self._seeded_generation_safe(source_bits, target_bits)
            
        # Ensure exact target length
        if len(result) > target_bits:
            result = result[:target_bits]
            print(f"   Truncated to exact target: {len(result):,} bits")
        elif len(result) < target_bits:
            print(f"   Generated {len(result):,} bits (short of target)")
            
        return result
            
    def _hash_expansion_safe(self, source_bits: str, target_bits: int) -> str:
        """Safe hash-based expansion that avoids integer overflow."""
        print(f"   Using safe hash expansion method")
        
        output_bits = source_bits
        iteration = 0
        
        while len(output_bits) < target_bits and iteration < 10:
            iteration += 1
            print(f"   Hash expansion iteration {iteration}")
            
            new_bits = ""
            
            # Process source in safe chunks
            for i in range(0, len(source_bits), 32):  # Use smaller chunks (32 bits)
                chunk = source_bits[i:i + 32]
                if len(chunk) < 32:
                    chunk = chunk.ljust(32, '0')
                    
                # Add iteration counter safely
                iteration_bits = format(iteration, '08b')
                safe_input = chunk + iteration_bits  # Max 40 bits
                
                # Convert safely to bytes
                try:
                    # Pad to byte boundary
                    padded_input = safe_input.ljust(48, '0')  # 6 bytes
                    byte_data = self._safe_bits_to_bytes(padded_input)
                    
                    if byte_data:
                        hash_result = hashlib.sha256(byte_data).hexdigest()
                        hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
                        new_bits += hash_bits
                        
                except Exception as e:
                    print(f"   Warning: Hash expansion error: {e}")
                    continue
                    
            output_bits += new_bits
            
            if len(new_bits) == 0:  # Safety check
                break
                
        print(f"   Hash expansion complete: {len(output_bits):,} bits")
        return output_bits[:target_bits]
        
    def _iterative_hashing_safe(self, source_bits: str, target_bits: int) -> str:
        """Safe iterative hashing that avoids overflow."""
        print(f"   Using safe iterative hashing method")
        
        output_bits = ""
        
        # Use source in manageable chunks
        seed_chunk = source_bits[:min(64, len(source_bits))]  # Max 64 bits for seed
        
        iterations_needed = (target_bits // 512) + 1
        print(f"   Planning {iterations_needed} iterations")
        
        for i in range(iterations_needed):
            if i % 100 == 0 and i > 0:
                print(f"   Completed {i}/{iterations_needed} iterations")
                
            try:
                # Create safe iteration input
                iteration_bits = format(i, '032b')  # 32 bits for iteration
                safe_input = seed_chunk + iteration_bits  # Max 96 bits
                
                # Convert to bytes safely
                byte_data = self._safe_bits_to_bytes(safe_input)
                
                if byte_data:
                    # Use multiple hash functions for diversity
                    sha256_hash = hashlib.sha256(byte_data).hexdigest()
                    
                    # Create second hash with different input
                    byte_data2 = byte_data + b'\x01'  # Add single byte difference
                    sha3_hash = hashlib.sha3_256(byte_data2).hexdigest()
                    
                    # Combine hashes
                    combined_hash = sha256_hash + sha3_hash
                    hash_bits = bin(int(combined_hash, 16))[2:].zfill(512)
                    
                    output_bits += hash_bits
                    
                    # Update seed for next iteration (use last 64 bits)
                    if len(hash_bits) >= 64:
                        seed_chunk = hash_bits[-64:]
                        
            except Exception as e:
                print(f"   Warning: Iteration {i} error: {e}")
                continue
                
            # Check if we have enough bits
            if len(output_bits) >= target_bits:
                break
                
        print(f"   Iterative hashing complete: {len(output_bits):,} bits")
        return output_bits[:target_bits]
        
    def _seeded_generation_safe(self, source_bits: str, target_bits: int) -> str:
        """Safe seeded generation for very high amplification."""
        print(f"   Using safe seeded generation method")
        
        # Use source bits as seed safely
        if len(source_bits) >= 32:
            seed_bits = source_bits[:32]  # Use only 32 bits for seed
        else:
            # Pad short source
            seed_bits = (source_bits * ((32 // len(source_bits)) + 1))[:32]
            
        seed_value = int(seed_bits, 2)
        np.random.seed(seed_value % (2**31))  # Safe seed value
        
        output_bits = ""
        
        # Generate in blocks
        block_size = 1024
        blocks_needed = (target_bits // block_size) + 1
        print(f"   Generating {blocks_needed} blocks of {block_size} bits each")
        
        for block_idx in range(blocks_needed):
            if block_idx % 100 == 0 and block_idx > 0:
                print(f"   Generated {block_idx}/{blocks_needed} blocks")
                
            try:
                # Create safe block seed
                block_bits = format(block_idx, '032b')  # 32 bits for block index
                block_seed = seed_bits + block_bits  # Max 64 bits
                
                # Convert to bytes safely
                seed_bytes = self._safe_bits_to_bytes(block_seed)
                
                if seed_bytes:
                    # Generate multiple hashes for this block
                    block_bits_output = ""
                    hashes_per_block = (block_size // 256) + 1
                    
                    for hash_round in range(hashes_per_block):
                        try:
                            round_input = seed_bytes + hash_round.to_bytes(4, byteorder='big')
                            hash_result = hashlib.sha256(round_input).hexdigest()
                            hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
                            block_bits_output += hash_bits
                        except Exception as e:
                            print(f"   Warning: Block {block_idx}, round {hash_round} error: {e}")
                            continue
                            
                    output_bits += block_bits_output[:block_size]  # Truncate to block size
                    
            except Exception as e:
                print(f"   Warning: Block {block_idx} error: {e}")
                continue
                
            # Check if we have enough bits
            if len(output_bits) >= target_bits:
                break
                
        print(f"   Seeded generation complete: {len(output_bits):,} bits")
        return output_bits[:target_bits]
        
    def _safe_bits_to_bytes(self, bits: str) -> bytes:
        """Safely convert bit string to bytes without overflow."""
        try:
            # Ensure bits string is valid
            if not all(c in '01' for c in bits):
                return b''
                
            # Pad to byte boundary
            padded_bits = bits.ljust((len(bits) + 7) // 8 * 8, '0')
            
            # Convert to bytes in chunks to avoid overflow
            byte_array = bytearray()
            for i in range(0, len(padded_bits), 8):
                byte_str = padded_bits[i:i+8]
                if len(byte_str) == 8:
                    byte_val = int(byte_str, 2)
                    byte_array.append(byte_val)
                    
            return bytes(byte_array)
            
        except Exception:
            return b''
