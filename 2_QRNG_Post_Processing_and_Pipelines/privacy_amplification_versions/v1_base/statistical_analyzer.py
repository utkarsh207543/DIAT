"""
Statistical Analyzer
Comprehensive statistical analysis of bitstreams for randomness assessment.
"""

import numpy as np
from scipy import stats
from math import log2
from typing import Dict, List, Tuple

class StatisticalAnalyzer:
    def __init__(self):
        pass
        
    def analyze_bitstring(self, bits: str) -> Dict:
        """
        Perform comprehensive statistical analysis of a bitstring.
        
        Args:
            bits: Binary string to analyze
            
        Returns:
            Dictionary containing various statistical measures
        """
        if not bits:
            return {'error': 'Empty bitstring'}
            
        analysis = {
            'length': len(bits),
            'ones': bits.count('1'),
            'zeros': bits.count('0'),
            'balance': bits.count('1') / len(bits),
            'entropy': self._shannon_entropy(bits),
            'runs_test': self._runs_test(bits),
            'autocorrelation': self._autocorrelation_test(bits),
            'frequency_test': self._frequency_test(bits),
            'block_frequency': self._block_frequency_test(bits),
            'longest_run': self._longest_run_test(bits),
            'compression_ratio': self._compression_estimate(bits)
        }
        
        return analysis
        
    def _shannon_entropy(self, bits: str) -> float:
        """Calculate Shannon entropy."""
        if not bits:
            return 0.0
            
        p0 = bits.count('0') / len(bits)
        p1 = bits.count('1') / len(bits)
        
        entropy = 0.0
        if p0 > 0:
            entropy -= p0 * log2(p0)
        if p1 > 0:
            entropy -= p1 * log2(p1)
            
        return entropy
        
    def _runs_test(self, bits: str) -> Dict:
        """Perform runs test for randomness."""
        if len(bits) < 2:
            return {'error': 'Insufficient data'}
            
        runs = 1
        for i in range(1, len(bits)):
            if bits[i] != bits[i-1]:
                runs += 1
                
        n = len(bits)
        ones = bits.count('1')
        zeros = bits.count('0')
        
        # Expected runs and variance
        expected_runs = (2 * ones * zeros) / n + 1
        variance = (2 * ones * zeros * (2 * ones * zeros - n)) / (n**2 * (n - 1))
        
        if variance > 0:
            z_score = (runs - expected_runs) / np.sqrt(variance)
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        else:
            z_score = 0
            p_value = 1.0
            
        return {
            'runs': runs,
            'expected_runs': expected_runs,
            'z_score': z_score,
            'p_value': p_value,
            'passed': p_value > 0.01
        }
        
    def _autocorrelation_test(self, bits: str, max_lag: int = 16) -> Dict:
        """Test for autocorrelation at various lags."""
        if len(bits) < max_lag * 2:
            return {'error': 'Insufficient data'}
            
        # Convert to numerical array
        bit_array = np.array([int(b) for b in bits])
        
        autocorrs = []
        for lag in range(1, min(max_lag + 1, len(bits) // 2)):
            if len(bits) > lag:
                corr = np.corrcoef(bit_array[:-lag], bit_array[lag:])[0, 1]
                if not np.isnan(corr):
                    autocorrs.append(abs(corr))
                    
        max_autocorr = max(autocorrs) if autocorrs else 0
        
        return {
            'max_autocorrelation': max_autocorr,
            'autocorrelations': autocorrs,
            'passed': max_autocorr < 0.1  # Threshold for randomness
        }
        
    def _frequency_test(self, bits: str) -> Dict:
        """Basic frequency test (proportion of ones)."""
        n = len(bits)
        ones = bits.count('1')
        
        # Test statistic
        s = abs(ones - n/2) / np.sqrt(n/4)
        p_value = 2 * (1 - stats.norm.cdf(s))
        
        return {
            'ones_proportion': ones / n,
            'test_statistic': s,
            'p_value': p_value,
            'passed': p_value > 0.01
        }
        
    def _block_frequency_test(self, bits: str, block_size: int = 20) -> Dict:
        """Block frequency test."""
        if len(bits) < block_size:
            return {'error': 'Insufficient data'}
            
        num_blocks = len(bits) // block_size
        block_proportions = []
        
        for i in range(num_blocks):
            block = bits[i * block_size:(i + 1) * block_size]
            proportion = block.count('1') / block_size
            block_proportions.append(proportion)
            
        if not block_proportions:
            return {'error': 'No complete blocks'}
            
        # Chi-square test
        chi_square = 4 * block_size * sum((p - 0.5)**2 for p in block_proportions)
        p_value = 1 - stats.chi2.cdf(chi_square, num_blocks)
        
        return {
            'num_blocks': num_blocks,
            'chi_square': chi_square,
            'p_value': p_value,
            'passed': p_value > 0.01
        }
        
    def _longest_run_test(self, bits: str) -> Dict:
        """Test for longest run of identical bits."""
        if not bits:
            return {'error': 'Empty bitstring'}
            
        longest_run = 1
        current_run = 1
        
        for i in range(1, len(bits)):
            if bits[i] == bits[i-1]:
                current_run += 1
                longest_run = max(longest_run, current_run)
            else:
                current_run = 1
                
        # Expected longest run (approximate)
        expected_longest = log2(len(bits)) if len(bits) > 0 else 0
        
        return {
            'longest_run': longest_run,
            'expected_longest': expected_longest,
            'ratio': longest_run / expected_longest if expected_longest > 0 else 0,
            'passed': longest_run < 2 * expected_longest
        }
        
    def _compression_estimate(self, bits: str) -> float:
        """Estimate compression ratio as a measure of randomness."""
        try:
            import zlib
            compressed = zlib.compress(bits.encode())
            return len(compressed) / len(bits)
        except:
            return 1.0  # No compression available
            
    def generate_nist_summary(self, results: Dict) -> str:
        """Generate summary suitable for NIST test preparation."""
        summary = []
        summary.append("NIST Statistical Test Suite Preparation Summary")
        summary.append("=" * 50)
        
        for filename, result in results.items():
            if 'analysis' in result:
                analysis = result['analysis']
                summary.append(f"\n{filename}:")
                summary.append(f"  Length: {analysis['length']:,} bits")
                summary.append(f"  Balance: {analysis['balance']:.6f}")
                summary.append(f"  Entropy: {analysis['entropy']:.6f}")
                
                if 'frequency_test' in analysis:
                    freq_test = analysis['frequency_test']
                    summary.append(f"  Frequency Test: {'PASS' if freq_test['passed'] else 'FAIL'} (p={freq_test['p_value']:.6f})")
                    
                if 'runs_test' in analysis:
                    runs_test = analysis['runs_test']
                    summary.append(f"  Runs Test: {'PASS' if runs_test['passed'] else 'FAIL'} (p={runs_test['p_value']:.6f})")
                    
        return '\n'.join(summary)
