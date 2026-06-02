import os
import subprocess
import shutil
import tempfile
import json
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
NIST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../nist'))
if os.name == 'nt':
    ASSESS_EXEC = os.path.join(NIST_ROOT, 'assess.exe')
else:
    ASSESS_EXEC = os.path.join(NIST_ROOT, 'assess')
DATA_DIR = os.path.join(NIST_ROOT, 'data')
EXPERIMENTS_DIR = os.path.join(NIST_ROOT, 'experiments', 'AlgorithmTesting')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

TEST_NAME_MAP = {
    0: "Frequency",
    1: "BlockFrequency",
    2: "CumulativeSums",
    3: "Runs",
    4: "LongestRun",
    5: "Rank",
    6: "FFT",
    7: "NonOverlappingTemplate",
    8: "OverlappingTemplate",
    9: "Universal",
    10: "ApproximateEntropy",
    11: "RandomExcursions",
    12: "RandomExcursionsVariant",
    13: "Serial",
    14: "LinearComplexity"
}

TEST_TYPES = [TEST_NAME_MAP[i] for i in range(15)]

@app.route('/')
def index():
    return render_template('index.html', test_types=TEST_TYPES)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    file_type = request.form.get('file_type', 'binary')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})

    if file:
        try:
            # Read file content
            content = file.read()
            binary_data = ""
            
            if file_type == 'binary':
                try:
                    # Try interpreting as simple text first if users upload "10101" as a .txt
                    text_content = content.decode('utf-8').strip()
                    if all(c in '01' for c in text_content):
                        binary_data = text_content
                    else:
                        raise ValueError("Not text binary")
                except:
                    # Actual binary file conversion
                    # byte -> 8 bits
                    binary_data = "".join(f"{byte:08b}" for byte in content)
            else:
                # String file (assuming '0's and '1's)
                binary_data = content.decode('utf-8').strip().replace('\n', '').replace(' ', '')
                if not all(c in '01' for c in binary_data):
                     return jsonify({'success': False, 'error': 'File contains non-binary characters'})

            return jsonify({
                'success': True,
                'binary_data': binary_data[:1000000], # Limit preview/return to frontend to avoid crash
                'binary_length': len(binary_data),
                'message': 'File processed. (Preview limited to 1MB)' if len(binary_data) > 1000000 else 'File processed.'
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'Unknown error'})

def parse_summary_report():
    report_path = os.path.join(EXPERIMENTS_DIR, 'finalAnalysisReport.txt')
    results = []
    
    if not os.path.exists(report_path):
        return []

    try:
        with open(report_path, 'r') as f:
            lines = f.readlines()
        
        # NIST Summary Report Format:
        # C1 C2 ... C10 P-VALUE PROPORTION STATISTICAL TEST
        # Fixed width parsing is most reliable here
        
        start_parsing = False
        for line in lines:
            line = line.strip()
            if "STATISTICAL TEST" in line and "PROPORTION" in line:
                start_parsing = True
                continue
            
            if not start_parsing:
                continue
                
            if "------" in line or not line:
                continue
                
            # Parse columns
            # The columns are usually separated by spaces, but can be messy.
            # Example:
            # 1 0 0 ... 0 0.123456 99/100 Frequency
            # Or if stars exist: 0.123456 * 99/100
            
            parts = line.split()
            if len(parts) < 12: # 10 bins + P-val + Prop + Name
                continue
                
            # Last part is Name (or Name + variants)
            # Second to last is Proportion
            # Third to last is P-Value (Uniformity)
            # First 10 are bins
            
            # Find the proportion column (contains '/')
            prop_idx = -1
            for i in range(len(parts) - 1, -1, -1):
                if '/' in parts[i]:
                    prop_idx = i
                    break
            
            if prop_idx == -1:
                continue

            # Extract Test Name
            # Everything after prop_idx is potentially part of name, UNLESS the immediate next item is '*' which is a failure marker for proportion
            name_start_idx = prop_idx + 1
            if name_start_idx < len(parts) and parts[name_start_idx] == '*':
                name_start_idx += 1
            
            test_name = " ".join(parts[name_start_idx:])
            proportion_str = parts[prop_idx]

            # Extract P-Value
            # Value is before proportion. If immediate prev is '*', skip it (failure marker)
            p_val_idx = prop_idx - 1
            if p_val_idx >= 0 and parts[p_val_idx] == '*':
                p_val_idx -= 1
            
            p_val_uniformity_str = parts[p_val_idx]
            
            # Normalize
            # Normalize P-Value (Uniformity)
            is_uniform = True
            try:
                p_uni = float(p_val_uniformity_str)
                if p_uni < 0.0001: is_uniform = False
            except:
                p_uni = 0.0 # Default for "----" or errors
                # If P-value is missing (----), it usually means insufficient streams for uniformity test.
                # In this case, we shouldn't fail based on uniformity, but rely on proportion.
                
            # Calculate Proportion coverage
            passed = 0
            total = 0
            is_prop_pass = True
            try:
                num, den = proportion_str.split('/')
                passed = int(num)
                total = int(den)
                
                # NIST Standard: Pass rate should be high (e.g., > 96% typically)
                # For single stream (1/1), it must be 1.0. For 0/1 it is 0.0.
                # NIST Standard: Pass rate is defined by the confidence interval
                # Formula: (1 - alpha) +/- 3 * sqrt((1 - alpha) * alpha / k)
                # where alpha = 0.01 and k = total (sample size)
                # We use the lower bound for the pass threshold.
                
                if total > 0:
                    ratio = passed / total
                    alpha = 0.01
                    expected = 1.0 - alpha
                    sigma = (expected * alpha / total) ** 0.5
                    lower_bound = expected - 3 * sigma
                    
                    # For small samples (like 10), the formula gives ~0.895.
                    # 9/10 (0.9) > 0.895 -> PASS
                    # 8/10 (0.8) < 0.895 -> FAIL (Technically)
                    # However, NIST documentation textual summary often states "approx 8 for 10".
                    # To align with the "approximate" note and avoid strict edge case failures for 8/10,
                    # we can use a slightly looser bound or just the formula.
                    # Given the standard is strictly the formula, 0.9 is definitely a PASS.
                    # The previous fixed 0.96 was definitely wrong for k=10.
                    
                    if ratio < lower_bound: 
                        is_prop_pass = False
            except:
                pass

            # Comprehensive Status Check
            # 1. Check for NIST asterisk (* in string)
            # 2. Check calculated proportion (is_prop_pass)
            # 3. Check uniformity P-value (only if valid number parsed)
            
            status = 'PASS'
            if '*' in proportion_str:
                status = 'FAIL'
            elif not is_prop_pass:
                status = 'FAIL'
            elif not is_uniform and p_val_uniformity_str != '----':
                 # Only fail on uniformity if we actually had a valid p-value that was low
                 # "----" means "not computed", so don't fail on it.
                status = 'FAIL'

            results.append({
                'test_name': test_name,
                'p_value': p_uni, 
                'proportion': proportion_str, 
                'passed': passed,
                'total': total,
                'status': status
            })
            
    except Exception as e:
        print(f"Parsing Error: {e}")
        return []

    # Post-Processing: Group Results by Test Name
    grouped_map = {}
    final_output = []
    
    # Tests known to have multiple outputs
    MULTI_OUTPUT_TESTS = [
        "NonOverlappingTemplate", 
        "RandomExcursions", 
        "RandomExcursionsVariant",
        "CumulativeSums",
        "Serial"
    ]

    # First pass: Grouping
    for res in results:
        name = res['test_name']
        # Check if this test type usually has multiple outputs or if we just want to group by name
        if name in MULTI_OUTPUT_TESTS or any(m in name for m in MULTI_OUTPUT_TESTS):
            # Clean name for grouping (remove specific params if needed, but NIST usually uses same name)
            # Actually, let's group strictly by the test_name string returned.
            # But wait, RandomExcursions usually comes as "RandomExcursions (x=-1)". 
            # The parser above returns "RandomExcursions" from my logic? 
            # Looking at parser: `test_name = " ".join(parts[name_start_idx:])`.
            # If the file says "RandomExcursions (x= -1)", test_name is that.
            # We want to group by the BASE name.
            
            base_name = name.split('(')[0].strip()
            if base_name in grouped_map:
                grouped_map[base_name].append(res)
            else:
                grouped_map[base_name] = [res]
        else:
            # Single items go directly to output (or we can group everything? Let's group everything cleanly)
            base_name = name
            if base_name in grouped_map:
                grouped_map[base_name].append(res)
            else:
                grouped_map[base_name] = [res]
                
    # Second pass: Aggregate
    for base_name, group in grouped_map.items():
        if len(group) == 1:
            final_output.append(group[0])
        else:
            # Calculate Averages/Aggregates
            total_sub = len(group)
            pass_count = sum(1 for r in group if r['status'] == 'PASS')
            avg_p = sum(r['p_value'] for r in group) / total_sub
            
            # Aggregate Proportion (average of percentages)
            # Parse proportions "10/10" -> 1.0
            prop_sum = 0
            valid_props = 0
            for r in group:
                try:
                    passed, total = map(int, r['proportion'].split('/'))
                    if total > 0:
                        prop_sum += (passed / total)
                        valid_props += 1
                except:
                    pass
            
            avg_prop_val = (prop_sum / valid_props) if valid_props > 0 else 0.0
            # Represent as "x/y" style average? No, maybe just percent 99%
            
            overall_status = 'PASS'
            if pass_count < total_sub:
                overall_status = 'PARTIAL' if pass_count > 0 else 'FAIL'
            
            # Create Summary Object
            summary = {
                'test_name': base_name,
                'is_aggregated': True,
                'count': total_sub,
                'pass_count': pass_count,
                'p_value': avg_p,  # Average P-Value
                'proportion': f"{int(avg_prop_val * 100)}%", # Simplified display
                'status': overall_status,
                'sub_results': group
            }
            final_output.append(summary)

    return final_output
    
@app.route('/execute_tests', methods=['POST'])
def execute_tests():
    data = request.json
    binary_data = data.get('binary_data', '')
    selected_tests = data.get('selected_tests', [])
    parameters = data.get('parameters', {}) # e.g., {'blockFrequencyBlockLength': 128}

    if not binary_data:
        return jsonify({'success': False, 'error': 'No data provided'})

    temp_input_path = os.path.join(DATA_DIR, 'temp_input.dat')
    with open(temp_input_path, 'w') as f:
        f.write(binary_data)
        
    stream_length = len(binary_data)
    
    # Selected Tests Vector
    test_vector = ['0'] * 15
    for idx in selected_tests:
        if 0 <= idx < 15:
            test_vector[idx] = '1'
    test_vector_str = "".join(test_vector)

    # Construct Inputs
    inputs = [
        "0",                # Input File
        temp_input_path,    # Path
        "0",                # Select specific tests
        test_vector_str     # Selection string
    ]

    # Parameter Adjustments
    # Map from parameter names to Assess Test IDs and format inputs
    # 1: BlockFrequency (128)
    # 2: NonOverlapping (9)
    # 3: Overlapping (9)
    # 4: ApproxEntropy (10)
    # 5: Serial (16)
    # 6: LinearComplexity (500)
    
    # Check if parameters are provided. If standard defaults are modified, send them.
    # parameters dict e.g. {'block_freq': 128, 'non_overlap': 9, etc.}
    
    if parameters:
         # Block Frequency (Test ID 1 for parameter adjustment, but ID ~1 in test vector)
         if 'block_frequency' in parameters and int(parameters['block_frequency']) != 128:
             inputs.append("1")
             inputs.append(str(parameters['block_frequency']))
             
         if 'non_overlapping' in parameters and int(parameters['non_overlapping']) != 9:
             inputs.append("2")
             inputs.append(str(parameters['non_overlapping']))
             
         if 'overlapping' in parameters and int(parameters['overlapping']) != 9:
             inputs.append("3")
             inputs.append(str(parameters['overlapping']))
             
         if 'approx_entropy' in parameters and int(parameters['approx_entropy']) != 10:
             inputs.append("4")
             inputs.append(str(parameters['approx_entropy']))
             
         if 'serial' in parameters and int(parameters['serial']) != 16:
             inputs.append("5")
             inputs.append(str(parameters['serial']))
             
         if 'linear_complexity' in parameters and int(parameters['linear_complexity']) != 500:
             inputs.append("6")
             inputs.append(str(parameters['linear_complexity']))
    
    # Detect if any parameterized tests are selected
    # Indices: 1 (BlockFrequency), 7 (NonOverlapping), 8 (Overlapping), 
    # 10 (ApproxEntropy), 13 (Serial), 14 (LinearComplexity)
    PARAMETERIZED_TESTS = {1, 7, 8, 10, 13, 14}
    has_parameterized = any(idx in PARAMETERIZED_TESTS for idx in selected_tests)

    if has_parameterized:
        inputs.append("0") # Continue (finish parameter adjustments)
    
    # Calculate stream length based on bitstream count
    bitstream_count = int(data.get('bitstream_count', 1))
    if bitstream_count < 1: bitstream_count = 1
    
    # assess expects the length of A SINGLE stream as the argument
    stream_length = len(binary_data) // bitstream_count
    
    inputs.append(str(bitstream_count)) # Bitstreams
    inputs.append("0") # Format (ASCII)
    
    input_str = "\n".join(inputs) + "\n"

    try:
        cmd = [ASSESS_EXEC, str(stream_length)]
        subprocess.run(
            cmd,
            input=input_str,
            cwd=NIST_ROOT,
            text=True,
            capture_output=True
        )
        
        # New Parsing Logic: Read Summary Report
        results = parse_summary_report()
        
        return jsonify({
            'success': True,
            'results': results,
            'data_length': stream_length
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_results', methods=['GET'])
def download_results_file():
    report_path = os.path.join(EXPERIMENTS_DIR, 'finalAnalysisReport.txt')
    
    if not os.path.exists(report_path):
        return jsonify({'success': False, 'error': 'Report file not found. Run analysis first.'})
        
    try:
        return send_file(
            report_path, 
            as_attachment=True, 
            download_name='finalAnalysisReport.txt',
            mimetype='text/plain'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
