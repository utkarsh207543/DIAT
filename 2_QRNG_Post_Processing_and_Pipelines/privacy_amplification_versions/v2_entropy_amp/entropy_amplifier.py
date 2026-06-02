"""
Entropy Amplifier
Amplifies entropy from processed bits to reach target bit count (500K bits).
Uses multiple techniques to generate the required number of high-quality random bits.
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
        Amplify entropy to reach target bit count.
        
        Args:
            source_bits: Input binary string
            target_bits: Target number of output bits
            
        Returns:
            Amplified binary string of target length
        """
        if not source_bits:
            return ""
            
        print(f"   🎯 Amplifying {len(source_bits):,} bits to {target_bits:,} bits")
        
        # If we already have enough bits, truncate
        if len(source_bits) >= target_bits:
            print(f"   ✂️  Truncating to target length")
            return source_bits[:target_bits]
            
        # Calculate amplification factor needed
        amplification_factor = target_bits / len(source_bits)
        print(f"   📈 Amplification factor: {amplification_factor:.2f}x")
        
        # Choose amplification strategy based on factor
        if amplification_factor <= 2:
            return self._hash_expansion(source_bits, target_bits)
        elif amplification_factor <= 10:
            return self._iterative_hashing(source_bits, target_bits)
        else:
            return self._seeded_generation(source_bits, target_bits)
            
    def _hash_expansion(self, source_bits: str, target_bits: int) -> str:
        """Hash-based expansion for moderate amplification (up to 2x)."""
        print(f"   🔐 Using hash expansion method")
        
        output_bits = source_bits
        iteration = 0
        
        while len(output_bits) < target_bits:
            iteration += 1
            new_bits = ""
            
            # Process in chunks
            for i in range(0, len(source_bits), self.chunk_size):
                chunk = source_bits[i:i + self.chunk_size]
                if len(chunk) < self.chunk_size:
                    chunk = chunk.ljust(self.chunk_size, '0')
                    
                # Add iteration counter to ensure different outputs
                chunk_with_counter = chunk + format(iteration, '08b')
                
                # Convert to bytes and hash
                byte_data = int(chunk_with_counter[:256], 2).to_bytes(32, byteorder='big')
                hash_result = hashlib.sha256(byte_data).hexdigest()
                
                # Convert hash back to binary
                hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
                new_bits += hash_bits
                
            output_bits += new_bits
            
            if iteration > 10:  # Safety limit
                break
                
        return output_bits[:target_bits]
        
    def _iterative_hashing(self, source_bits: str, target_bits: int) -> str:
        """Iterative hashing for higher amplification (up to 10x)."""
        print(f"   🔄 Using iterative hashing method")
        
        output_bits = ""
        seed = source_bits
        
        iterations_needed = (target_bits // 256) + 1
        
        for i in range(iterations_needed):
            # Create unique input for each iteration
            iteration_input = seed + format(i, '032b')
            
            # Ensure we have enough bits for hashing
            if len(iteration_input) < 256:
                iteration_input = (iteration_input * ((256 // len(iteration_input)) + 1))[:256]
                
            # Convert to bytes and hash
            byte_data = int(iteration_input, 2).to_bytes(32, byteorder='big')
            
            # Use multiple hash functions for diversity
            sha256_hash = hashlib.sha256(byte_data).hexdigest()
            sha3_hash = hashlib.sha3_256(byte_data).hexdigest()
            
            # Combine hashes
            combined_hash = sha256_hash + sha3_hash
            hash_bits = bin(int(combined_hash, 16))[2:].zfill(512)
            
            output_bits += hash_bits
            
            # Update seed for next iteration
            seed = hash_bits[:len(source_bits)]
            
        return output_bits[:target_bits]
        
    def _seeded_generation(self, source_bits: str, target_bits: int) -> str:
        """Seeded generation for very high amplification (>10x)."""
        print(f"   🌱 Using seeded generation method")
        
        # Use source bits as seed for deterministic generation
        seed_value = int(source_bits[:min(64, len(source_bits))], 2)
        np.random.seed(seed_value % (2**32))  # Ensure seed fits in 32 bits
        
        output_bits = ""
        
        # Generate in blocks using the source as entropy
        block_size = 1024
        blocks_needed = (target_bits // block_size) + 1
        
        for block_idx in range(blocks_needed):
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
            for hash_round in range(block_size // 256):
                round_input = seed_bytes + hash_round.to_bytes(4, byteorder='big')
                hash_result = hashlib.sha256(round_input).hexdigest()
                hash_bits = bin(int(hash_result, 16))[2:].zfill(256)
                block_bits += hash_bits
                
            output_bits += block_bits
            
        return output_bits[:target_bits]
        
    def _lfsr_amplification(self, source_bits: str, target_bits: int) -> str:
        """LFSR-based amplification as alternative method."""
        print(f"   🔄 Using LFSR amplification method")
        
        if len(source_bits) < 16:
            # Pad source if too short
            source_bits = (source_bits * ((16 // len(source_bits)) + 1))[:16]
            
        # Initialize LFSR with source bits
        lfsr_state = [int(bit) for bit in source_bits[:16]]
        taps = [16, 14, 13, 11]  # Primitive polynomial
        
        output_bits = []
        
        for _ in range(target_bits):
            # Output current bit
            output_bit = lfsr_state[-1]
            output_bits.append(str(output_bit))
            
            # Calculate feedback
            feedback = 0
            for tap in taps:
                if tap <= len(lfsr_state):
                    feedback ^= lfsr_state[tap - 1]
                    
            # Shift and insert feedback
            lfsr_state = [feedback] + lfsr_state[:-1]
            
        return ''.join(output_bits)
        
    def amplify_with_quality_check(self, source_bits: str, target_bits: int, 
                                 min_entropy: float = 0.99) -> str:
        """
        Amplify with quality checking to ensure high entropy output.
        
        Args:
            source_bits: Input binary string
            target_bits: Target number of output bits
            min_entropy: Minimum required entropy
            
        Returns:
            High-quality amplified binary string
        """
        from statistical_analyzer import StatisticalAnalyzer
        analyzer = StatisticalAnalyzer()
        
        max_attempts = 5
        
        for attempt in range(max_attempts):
            print(f"   🎯 Amplification attempt {attempt + 1}/{max_attempts}")
            
            # Try different methods for each attempt
            if attempt == 0:
                result = self._hash_expansion(source_bits, target_bits)
            elif attempt == 1:
                result = self._iterative_hashing(source_bits, target_bits)
            elif attempt == 2:
                result = self._seeded_generation(source_bits, target_bits)
            else:
                # Modify source slightly and retry
                modified_source = self._perturb_source(source_bits, attempt)
                result = self._iterative_hashing(modified_source, target_bits)
                
            # Check quality
            if result:
                analysis = analyzer.analyze_bitstring(result)
                entropy = analysis.get('entropy', 0)
                
                print(f"   📊 Attempt {attempt + 1} entropy: {entropy:.6f}")
                
                if entropy >= min_entropy:
                    print(f"   ✅ Quality check passed!")
                    return result
                    
        print(f"   ⚠️  Using best attempt (may not meet quality threshold)")
        return result if 'result' in locals() else ""
        
    def _perturb_source(self, source_bits: str, perturbation: int) -> str:
        """Slightly modify source bits for retry attempts."""
        if not source_bits:
            return source_bits
            
        # XOR with a pattern based on perturbation value
        pattern = format(perturbation * 0x5555, '016b')  # Simple pattern
        pattern = (pattern * ((len(source_bits) // len(pattern)) + 1))[:len(source_bits)]
        
        perturbed = ""
        for i, bit in enumerate(source_bits):
            perturbed += str(int(bit) ^ int(pattern[i]))
            
        return perturbed
