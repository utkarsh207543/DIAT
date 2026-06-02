import urllib.request
import urllib.error
import json
import os

# Path to data.pi
# Path to data.pi
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../nist/data/data.pi'))

def read_data_pi():
    with open(DATA_PATH, 'r') as f:
        content = f.read().replace('\n', '').replace(' ', '')
    return content

def run_test():
    binary_data = read_data_pi()
    # Truncate to 1,000,000 bits to match manual "./assess 100000" with 10 streams
    limit = 100000 * 10
    if len(binary_data) > limit:
        print(f"Truncating data from {len(binary_data)} to {limit} bits for exact comparison.")
        binary_data = binary_data[:limit]
    
    # Payload
    selected_tests = list(range(15))
    
    payload = {
        'binary_data': binary_data,
        'selected_tests': selected_tests,
        'parameters': {},
        'bitstream_count': 10
    }
    
    json_data = json.dumps(payload).encode('utf-8')
    
    print(f"Sending request with {len(binary_data)} bits...")
    
    req = urllib.request.Request(
        'http://127.0.0.1:5000/execute_tests',
        data=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result_body = response.read().decode('utf-8')
            data = json.loads(result_body)
            
            if data['success']:
                print("Website Analysis Success!")
                results = data['results']
                print(f"Received {len(results)} result items.")
                
                # Verify specific values
                # Manual: Frequency P=0.534146, Prop=10/10
                freq_res = next((r for r in results if r['test_name'] == 'Frequency'), None)
                if freq_res:
                    print(f"Frequency Test JSON: {freq_res}")
                    # Allow small float diff
                    if abs(freq_res['p_value'] - 0.534146) < 0.0001 and freq_res['proportion'] == '10/10':
                        print("MATCH: Frequency Test data string match.")
                    else:
                        print("MISMATCH: Frequency Test data.")
                else:
                    print("MISSING: Frequency Test.")
                    
                 # Universal Test (Expected Fail)
                uni_res = next((r for r in results if r['test_name'] == 'Universal'), None)
                if uni_res:
                     print(f"Universal Test JSON: {uni_res}")
                     # Manual: P=0.000000, Prop=0/10 *
                     if uni_res['p_value'] == 0.0 and (uni_res['proportion'] == '0/10' or uni_res['proportion'] == '0/10 *'):
                         print("MATCH: Universal Test data match.")
                     else:
                         print("MISMATCH: Universal Test data.")

                # Serial Test (First component)
                # Manual: P=0.350485, Prop=9/10
                serial_res = next((r for r in results if r['test_name'] == 'Serial'), None)
                # Serial usually appears twice in detailed list but parse_summary might group or list separate?
                # My parser logic makes a list entry for every line.
                # In summary report:
                # Serial line 1: P=0.350485 Prop=9/10
                # Serial line 2: P=0.534146 Prop=9/10
                # Let's check simply if one matches
                
            else:
                print(f"Website Error: {data.get('error')}")
                
    except urllib.error.URLError as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    run_test()
