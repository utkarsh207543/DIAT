"""
XOR Combiner with Multiple Delayed Streams
Combines multiple delayed versions of the input stream using XOR operations.
"""

import numpy as np
from typing import List

class XORCombiner:
    def __init__(self, delays: List[int] = None):
        if delays is None:
            self.delays = [1, 3, 7, 15, 31]  # Prime-like delays
        else:
            self.delays = delays
            
    def combine_delayed_streams(self, raw_bits: str) -> str:
        """
        Combine multiple delayed streams using XOR.
        
        Args:
            raw_bits: Input binary string
            
        Returns:
            XOR-combined binary string
        """
        max_delay = max(self.delays)
        
        if len(raw_bits) <= max_delay:
            print(f"   ⚠️  Input too short for XOR combining (need > {max_delay})")
            return ""
            
        output_bits = []
        
        # Process bits starting after maximum delay
        for i in range(max_delay, len(raw_bits)):
            combined_bit = int(raw_bits[i])  # Start with current bit
            
            # XOR with delayed versions
            for delay in self.delays:
                if i - delay >= 0:
                    combined_bit ^= int(raw_bits[i - delay])
                    
            output_bits.append(str(combined_bit))
            
        result = ''.join(output_bits)
        
        print(f"   ⊕ XOR combining complete")
        print(f"   🕐 Delays used: {self.delays}")
        print(f"   📊 Output length: {len(result)}")
        
        return result
        
    def adaptive_xor_combine(self, raw_bits: str, window_size: int = 100) -> str:
        """
        Adaptive XOR combining that adjusts delays based on local statistics.
        """
        output_bits = []
        current_delays = self.delays.copy()
        
        for i in range(max(self.delays), len(raw_bits)):
            # Analyze local window for bias
            start = max(0, i - window_size)
            window = raw_bits[start:i]
            
            if len(window) > 0:
                bias = window.count('1') / len(window)
                
                # Adjust delays based on bias
                if abs(bias - 0.5) > 0.1:
                    # Use more delays for biased regions
                    current_delays = self.delays + [d * 2 for d in self.delays[:3]]
                else:
                    current_delays = self.delays
                    
            # Combine with current delays
            combined_bit = int(raw_bits[i])
            for delay in current_delays:
                if i - delay >= 0:
                    combined_bit ^= int(raw_bits[i - delay])
                    
            output_bits.append(str(combined_bit))
            
        result = ''.join(output_bits)
        
        print(f"   ⊕ Adaptive XOR combining complete")
        print(f"   📊 Output length: {len(result)}")
        
        return result
        
    def fibonacci_xor_combine(self, raw_bits: str) -> str:
        """
        XOR combining using Fibonacci sequence delays.
        """
        # Generate Fibonacci delays
        fib_delays = [1, 1]
        while fib_delays[-1] < len(raw_bits) // 4:
            fib_delays.append(fib_delays[-1] + fib_delays[-2])
            
        fib_delays = fib_delays[2:]  # Remove initial 1,1
        
        max_delay = max(fib_delays)
        output_bits = []
        
        for i in range(max_delay, len(raw_bits)):
            combined_bit = int(raw_bits[i])
            
            for delay in fib_delays:
                if i - delay >= 0:
                    combined_bit ^= int(raw_bits[i - delay])
                    
            output_bits.append(str(combined_bit))
            
        result = ''.join(output_bits)
        
        print(f"   ⊕ Fibonacci XOR combining complete")
        print(f"   🔢 Fibonacci delays: {fib_delays}")
        print(f"   📊 Output length: {len(result)}")
        
        return result
