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
        Amplify entropy to reach exact target bit count.
        
        Args:
            source_bits: Input binary string
            target_bits: Target number of output bits
            
        Returns:
            Amplified binary string of target length
        """
        if not source_bits:
            print(f"   ❌ No source bits provided for amplification")
            return ""
            
        print(f"   🎯 Amplifying {len(source_bits):,} → {target_bits:,} bits")
        
        # If we already have enough bits, truncate to exact target
        if len(source_bits) >= target_bits:
            print(f"   ✂️  Truncating to exact target length")
            return source_bits[:target_bits]
            
        # Calculate amplification factor needed
        amplification_factor = target_bits / len(source_bits)
        print(f"   📈 Amplification factor: {amplification_factor:.2f}x")
        
        # Choose amplification strategy based on factor
        if amplification_factor <= 2:
            result = self._hash_expansion(source_bits, target_bits)
        elif amplification_factor <= 10:
            result = self._iterative_hashing(source_bits, target_bits)
        else:
            result = self._seeded_generation(source_bits, target_bits)
            
        # Ensure exact target length
        if len(result) > target_bits:
            result = result[:target_bits]
            print(f"   ✂️  Truncated to exact target: {len(result):,} bits")
        elif len(result) < target_bits:
            print(f"   ⚠️  Generated {len(result):,} bits (short of target)")
            
        return result
            
    def _hash_expansion(self, source_bits: str, target_bits: int) -> str:
        """Hash-based expansion for moderate amplification (up to 2x)."""
        print(f"   🔐 Using hash expansion method")
        
        output_bits = source_bits
        iteration = 0
        
        while len(output_bits) < target_bits and iteration < 10:
            iteration += 1
            print(f"   🔄 Hash expansion iteration {iteration}")
            
            new_bits = ""
            
            # Process source in chunks
            for i in range(0, len(source_bits), self.chunk_size):
                chunk = source_bits[i:i + self.chunk_size]
                if len(chunk) < self.chunk_size:
                    chunk = chunk.ljust(self.chunk_size, '0')
                    
                # Add iteration counter to ensure different outputs
                chunk_with_counter = chunk + format(iteration, '08b')
                
                # Convert to bytes and hash
                try:
                    byte_data = int(chunk_with_counter[:256], 2).to_bytes(32, byteorder='big')
                    hash_result = hashlib.sha256(byte_data).hexdigest()
                    
                    # Convert hash back to binary
                    hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
                    new_bits += hash_bits
                except ValueError as e:
                    print(f"   ⚠️  Hash expansion error: {e}")
                    break
                    
            output_bits += new_bits
            
            if len(new_bits) == 0:  # Safety check
                break
                
        print(f"   ✅ Hash expansion complete: {len(output_bits):,} bits")
        return output_bits[:target_bits]
        
    def _iterative_hashing(self, source_bits: str, target_bits: int) -> str:
        """Iterative hashing for higher amplification (up to 10x)."""
        print(f"   🔄 Using iterative hashing method")
        
        output_bits = ""
        seed = source_bits
        
        iterations_needed = (target_bits // 512) + 1  # 512 bits per iteration (SHA256 + SHA3)
        print(f"   📊 Planning {iterations_needed} iterations")
        
        for i in range(iterations_needed):
            if i % 100 == 0 and i > 0:
                print(f"   🔄 Completed {i}/{iterations_needed} iterations")
                
            # Create unique input for each iteration
            iteration_input = seed + format(i, '032b')
            
            # Ensure we have enough bits for hashing
            if len(iteration_input) < 256:
                iteration_input = (iteration_input * ((256 // len(iteration_input)) + 1))[:256]
                
            try:
                # Convert to bytes and hash
                byte_data = int(iteration_input, 2).to_bytes(32, byteorder='big')
                
                # Use multiple hash functions for diversity
                sha256_hash = hashlib.sha256(byte_data).hexdigest()
                sha3_hash = hashlib.sha3_256(byte_data).hexdigest()
                
                # Combine hashes
                combined_hash = sha256_hash + sha3_hash
                hash_bits = bin(int(combined_hash, 16))[2:].zfill(512)
                
                output_bits += hash_bits
                
                # Update seed for next iteration (use last 256 bits)
                if len(hash_bits) >= 256:
                    seed = hash_bits[-256:]
                    
            except ValueError as e:
                print(f"   ⚠️  Iteration {i} error: {e}")
                continue
                
            # Check if we have enough bits
            if len(output_bits) >= target_bits:
                break
                
        print(f"   ✅ Iterative hashing complete: {len(output_bits):,} bits")
        return output_bits[:target_bits]
        
    def _seeded_generation(self, source_bits: str, target_bits: int) -> str:
        """Seeded generation for very high amplification (>10x)."""
        print(f"   🌱 Using seeded generation method")
        
        # Use source bits as seed for deterministic generation
        if len(source_bits) >= 64:
            seed_value = int(source_bits[:64], 2)
        else:
            # Pad short source
            padded_source = (source_bits * ((64 // len(source_bits)) + 1))[:64]
            seed_value = int(padded_source, 2)
            
        # Ensure seed fits in 32 bits for numpy
        np.random.seed(seed_value % (2**32))
        
        output_bits = ""
        
        # Generate in blocks using the source as entropy
        block_size = 1024
        blocks_needed = (target_bits // block_size) + 1
        print(f"   📊 Generating {blocks_needed} blocks of {block_size} bits each")
        
        for block_idx in range(blocks_needed):
            if block_idx % 100 == 0 and block_idx > 0:
                print(f"   🔄 Generated {block_idx}/{blocks_needed} blocks")
                
            # Create block-specific seed
            block_seed = source_bits + format(block_idx, '032b')
            
            # Hash the block seed
            if len(block_seed) >= 256:
                seed_bytes = int(block_seed[:256], 2).to_bytes(32, byteorder='big')
            else:
                padded_seed = (block_seed * ((256 // len(block_seed)) + 1))[:256]
                seed_bytes = int(padded_seed, 2).to_bytes(32, byteorder='big')
                
            # Generate multiple hashes for this block
            block_bits = ""
            hashes_per_block = (block_size // 256) + 1
            
            for hash_round in range(hashes_per_block):
                try:
                    round_input = seed_bytes + hash_round.to_bytes(4, byteorder='big')
                    hash_result = hashlib.sha256(round_input).hexdigest()
                    hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
                    block_bits += hash_bits
                except Exception as e:
                    print(f"   ⚠️  Block {block_idx}, round {hash_round} error: {e}")
                    continue
                    
            output_bits += block_bits[:block_size]  # Truncate to block size
            
            # Check if we have enough bits
            if len(output_bits) >= target_bits:
                break
                
        print(f"   ✅ Seeded generation complete: {len(output_bits):,} bits")
        return output_bits[:target_bits]
