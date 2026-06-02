"""
Statistical Analyzer - Enhanced
Comprehensive statistical analysis with NIST-style tests preparation.
"""

import numpy as np
from scipy import stats
from math import log2, sqrt
from typing import Dict, List, Tuple
import time

class StatisticalAnalyzer:
    def __init__(self):
        pass
        
    def analyze_bitstring(self, bits: str) -> Dict:
        """
        Perform comprehensive statistical analysis optimized for NIST preparation.
        
        Args:
            bits: Binary string to analyze
            
        Returns:
            Dictionary containing various statistical measures
        """
        if not bits:
            return {'error': 'Empty bitstring'}
            
        n = len(bits)
        ones = bits.count('1')
        zeros = bits.count('0')
        
        analysis = {
            'length': n,
            'ones': ones,
            'zeros': zeros,
            'balance': ones / n if n > 0 else 0,
            'entropy': self._shannon_entropy(bits),
            'min_entropy_estimate': self._min_entropy_estimate(bits),
            'frequency_test': self._frequency_test(bits),
            'runs_test': self._runs_test(bits),
            'longest_run_test': self._longest_run_test(bits),
            'block_frequency_test': self._block_frequency_test(bits),
            'autocorrelation_test': self._autocorrelation_test(bits),
            'compression_estimate': self._compression_estimate(bits),
            'nist_readiness': self._assess_nist_readiness(bits)
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
        
    def _min_entropy_estimate(self, bits: str, block_size: int = 8) -> float:
        """Estimate min-entropy using block-based approach."""
        if len(bits) < block_size:
            return self._shannon_entropy(bits)
            
        # Count frequency of each block
        block_counts = {}
        for i in range(0, len(bits) - block_size + 1, block_size):
            block = bits[i:i + block_size]
            block_counts[block] = block_counts.get(block, 0) + 1
            
        if not block_counts:
            return 0.0
            
        # Find most frequent block
        max_count = max(block_counts.values())
        total_blocks = sum(block_counts.values())
        
        # Min-entropy = -log2(max_probability)
        max_prob = max_count / total_blocks
        min_entropy = -log2(max_prob) if max_prob > 0 else 0
        
        # Normalize by block size
        return min_entropy / block_size
        
    def _frequency_test(self, bits: str) -> Dict:
        """NIST-style frequency test."""
        n = len(bits)
        if n == 0:
            return {'error': 'Empty bitstring'}
            
        ones = bits.count('1')
        
        # Test statistic
        s = abs(ones - n/2) / sqrt(n/4)
        
        # P-value using complementary error function
        p_value = 2 * (1 - stats.norm.cdf(s))
        
        return {
            'ones_proportion': ones / n,
            'test_statistic': s,
            'p_value': p_value,
            'passed': p_value >= 0.01,
            'significance_level': 0.01
        }
        
    def _runs_test(self, bits: str) -> Dict:
        """NIST-style runs test."""
        n = len(bits)
        if n < 2:
            return {'error': 'Insufficient data'}
            
        ones = bits.count('1')
        zeros = bits.count('0')
        
        # Pre-test: check if proportion is reasonable
        prop = ones / n
        if abs(prop - 0.5) >= 2/sqrt(n):
            return {
                'error': 'Pre-test failed',
                'proportion': prop,
                'threshold': 2/sqrt(n),
                'passed': False
            }
            
        # Count runs
        runs = 1
        for i in range(1, n):
            if bits[i] != bits[i-1]:
                runs += 1
                
        # Test statistic
        expected_runs = (2 * ones * zeros) / n + 1
        variance = (2 * ones * zeros * (2 * ones * zeros - n)) / (n**2 * (n - 1))
        
        if variance <= 0:
            return {'error': 'Invalid variance'}
            
        test_stat = abs(runs - expected_runs) / sqrt(variance)
        p_value = 2 * (1 - stats.norm.cdf(test_stat))
        
        return {
            'runs': runs,
            'expected_runs': expected_runs,
            'test_statistic': test_stat,
            'p_value': p_value,
            'passed': p_value >= 0.01
        }
        
    def _longest_run_test(self, bits: str) -> Dict:
        """Test for longest run of identical bits."""
        if not bits:
            return {'error': 'Empty bitstring'}
            
        n = len(bits)
        
        # Find longest runs of 0s and 1s
        longest_0_run = 0
        longest_1_run = 0
        current_0_run = 0
        current_1_run = 0
        
        for bit in bits:
            if bit == '0':
                current_0_run += 1
                current_1_run = 0
                longest_0_run = max(longest_0_run, current_0_run)
            else:
                current_1_run += 1
                current_0_run = 0
                longest_1_run = max(longest_1_run, current_1_run)
                
        longest_run = max(longest_0_run, longest_1_run)
        
        # Expected longest run (approximation)
        expected_longest = log2(n) + 0.5 if n > 0 else 0
        
        # Simple pass/fail based on reasonable bounds
        upper_bound = 2 * expected_longest
        passed = longest_run <= upper_bound
        
        return {
            'longest_run_0s': longest_0_run,
            'longest_run_1s': longest_1_run,
            'longest_run_overall': longest_run,
            'expected_longest': expected_longest,
            'upper_bound': upper_bound,
            'passed': passed
        }
        
    def _block_frequency_test(self, bits: str, block_size: int = 128) -> Dict:
        """NIST block frequency test."""
        n = len(bits)
        if n < block_size:
            return {'error': f'Insufficient data (need >= {block_size} bits)'}
            
        num_blocks = n // block_size
        if num_blocks == 0:
            return {'error': 'No complete blocks'}
            
        # Calculate proportion of 1s in each block
        proportions = []
        for i in range(num_blocks):
            block = bits[i * block_size:(i + 1) * block_size]
            prop = block.count('1') / block_size
            proportions.append(prop)
            
        # Chi-square test statistic
        chi_square = 4 * block_size * sum((p - 0.5)**2 for p in proportions)
        
        # Degrees of freedom
        df = num_blocks
        
        # P-value
        p_value = 1 - stats.chi2.cdf(chi_square, df)
        
        return {
            'block_size': block_size,
            'num_blocks': num_blocks,
            'proportions': proportions,
            'chi_square': chi_square,
            'degrees_of_freedom': df,
            'p_value': p_value,
            'passed': p_value >= 0.01
        }
        
    def _autocorrelation_test(self, bits: str, max_lag: int = 16) -> Dict:
        """Test for autocorrelation at various lags."""
        n = len(bits)
        if n < max_lag * 2:
            return {'error': 'Insufficient data for autocorrelation test'}
            
        # Convert to numerical array (-1, 1 instead of 0, 1)
        bit_array = np.array([1 if b == '1' else -1 for b in bits])
        
        autocorrs = []
        significant_lags = []
        
        for lag in range(1, min(max_lag + 1, n // 2)):
            if n > lag:
                # Calculate autocorrelation
                c_lag = np.sum(bit_array[:-lag] * bit_array[lag:]) / (n - lag)
                autocorrs.append(abs(c_lag))
                
                # Check significance (approximate)
                threshold = 2 / sqrt(n - lag)
                if abs(c_lag) > threshold:
                    significant_lags.append(lag)
                    
        max_autocorr = max(autocorrs) if autocorrs else 0
        
        return {
            'max_autocorrelation': max_autocorr,
            'autocorrelations': autocorrs,
            'significant_lags': significant_lags,
            'passed': len(significant_lags) == 0,
            'threshold_used': 2 / sqrt(n) if n > 0 else 0
        }
        
    def _compression_estimate(self, bits: str) -> float:
        """Estimate compressibility as randomness indicator."""
        try:
            import zlib
            compressed = zlib.compress(bits.encode('utf-8'))
            return len(compressed) / len(bits) if bits else 1.0
        except ImportError:
            # Fallback: simple run-length encoding estimate
            runs = 1
            for i in range(1, len(bits)):
                if bits[i] != bits[i-1]:
                    runs += 1
            return runs / len(bits) if bits else 1.0
            
    def _assess_nist_readiness(self, bits: str) -> Dict:
        """Assess readiness for NIST Statistical Test Suite."""
        n = len(bits)
        
        # NIST requirements
        min_length = 1000000  # 1M bits recommended
        recommended_length = 1000000
        
        # Basic quality checks
        balance = bits.count('1') / n if n > 0 else 0
        entropy = self._shannon_entropy(bits)
        
        # Readiness assessment
        length_ok = n >= min_length
        balance_ok = 0.45 <= balance <= 0.55
        entropy_ok = entropy >= 0.99
        
        overall_ready = length_ok and balance_ok and entropy_ok
        
        recommendations = []
        if not length_ok:
            recommendations.append(f"Increase length to at least {min_length:,} bits")
        if not balance_ok:
            recommendations.append("Improve bit balance (should be ~0.5)")
        if not entropy_ok:
            recommendations.append("Increase entropy (should be ~1.0)")
            
        return {
            'length_sufficient': length_ok,
            'balance_acceptable': balance_ok,
            'entropy_sufficient': entropy_ok,
            'overall_ready': overall_ready,
            'current_length': n,
            'required_length': min_length,
            'current_balance': balance,
            'current_entropy': entropy,
            'recommendations': recommendations
        }
        
    def generate_nist_report(self, analysis: Dict, filename: str) -> str:
        """Generate a report suitable for NIST test preparation."""
        report_lines = [
            "NIST Statistical Test Suite Preparation Report",
            "=" * 50,
            f"File: {filename}",
            f"Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "BASIC STATISTICS:",
            f"  Length: {analysis['length']:,} bits",
            f"  Ones: {analysis['ones']:,} ({analysis['balance']:.4f})",
            f"  Zeros: {analysis['zeros']:,} ({1-analysis['balance']:.4f})",
            f"  Shannon Entropy: {analysis['entropy']:.6f}",
            f"  Min-Entropy Estimate: {analysis.get('min_entropy_estimate', 'N/A'):.6f}",
            "",
            "PRELIMINARY TESTS:",
        ]
        
        # Add test results
        for test_name in ['frequency_test', 'runs_test', 'longest_run_test', 'block_frequency_test']:
            if test_name in analysis:
                test_result = analysis[test_name]
                if 'passed' in test_result:
                    status = "PASS" if test_result['passed'] else "FAIL"
                    p_val = test_result.get('p_value', 'N/A')
                    report_lines.append(f"  {test_name.replace('_', ' ').title()}: {status} (p={p_val})")
                    
        # NIST readiness
        if 'nist_readiness' in analysis:
            readiness = analysis['nist_readiness']
            report_lines.extend([
                "",
                "NIST READINESS ASSESSMENT:",
                f"  Overall Ready: {'YES' if readiness['overall_ready'] else 'NO'}",
                f"  Length Sufficient: {'YES' if readiness['length_sufficient'] else 'NO'}",
                f"  Balance Acceptable: {'YES' if readiness['balance_acceptable'] else 'NO'}",
                f"  Entropy Sufficient: {'YES' if readiness['entropy_sufficient'] else 'NO'}",
            ])
            
            if readiness['recommendations']:
                report_lines.extend([
                    "",
                    "RECOMMENDATIONS:",
                ] + [f"  • {rec}" for rec in readiness['recommendations']])
                
        return '\n'.join(report_lines)
