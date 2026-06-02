
def parse_summary_report_logic(lines):
    results = []
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
            
        parts = line.split()
        if len(parts) < 12: 
            continue
            
        # Find prop
        prop_idx = -1
        for i in range(len(parts) - 1, -1, -1):
            if '/' in parts[i]:
                prop_idx = i
                break
        
        if prop_idx == -1:
            continue

        # Name
        name_start_idx = prop_idx + 1
        if name_start_idx < len(parts) and parts[name_start_idx] == '*':
            name_start_idx += 1
        
        test_name = " ".join(parts[name_start_idx:])
        proportion_str = parts[prop_idx]

        # P-val
        p_val_idx = prop_idx - 1
        if p_val_idx >= 0 and parts[p_val_idx] == '*':
            p_val_idx -= 1
        
        p_val_uniformity_str = parts[p_val_idx]
        
        # Logic from app.py
        is_uniform = True
        try:
            p_uni = float(p_val_uniformity_str)
            if p_uni < 0.0001: is_uniform = False
        except:
            p_uni = 0.0 
            
        passed = 0
        total = 0
        is_prop_pass = True
        try:
            num, den = proportion_str.split('/')
            passed = int(num)
            total = int(den)
            
            if total > 0:
                ratio = passed / total
                if ratio < 0.96: 
                    is_prop_pass = False
        except:
            pass

        status = 'PASS'
        if '*' in proportion_str:
            status = 'FAIL'
        elif not is_prop_pass:
            status = 'FAIL'
        elif not is_uniform and p_val_uniformity_str != '----':
            status = 'FAIL'

        results.append({
            'test_name': test_name,
            'p_value': p_uni, 
            'proportion': proportion_str, 
            'passed': passed,
            'total': total,
            'status': status
        })
    return results

report_content = """
------------------------------------------------------------------------------
RESULTS FOR THE UNIFORMITY OF P-VALUES AND THE PROPORTION OF PASSING SEQUENCES
------------------------------------------------------------------------------
   generator is </Users/utkarshkumarsingh/Desktop/nist/nist_gui/user_test.dat>
------------------------------------------------------------------------------
 C1  C2  C3  C4  C5  C6  C7  C8  C9 C10  P-VALUE  PROPORTION  STATISTICAL TEST
------------------------------------------------------------------------------
  0   0   0   0   0   0   1   0   0   0     ----       1/1       Frequency
  0   0   0   0   0   0   0   0   0   1     ----       1/1       BlockFrequency
  0   0   0   0   0   1   0   0   0   0     ----       1/1       CumulativeSums
  0   0   1   0   0   0   0   0   0   0     ----       1/1       CumulativeSums
  0   0   0   0   1   0   0   0   0   0     ----       1/1       Runs
  1   0   0   0   0   0   0   0   0   0     ----       0/1       LongestRun
"""

parsed = parse_summary_report_logic(report_content.split('\n'))
for res in parsed:
    print(f"{res['test_name']}: {res['status']} (Prop: {res['proportion']}, P: {res['p_value']})")
