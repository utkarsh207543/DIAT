from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash
import os
import tempfile
import json
import uuid
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

# Load configuration
from config_loader import load_config, get_google_config

# Import authentication and database modules
from auth import GoogleAuth
from database import DatabaseManager
from large_file_handler import LargeFileHandler

# Import all the test modules
from ApproximateEntropy import ApproximateEntropy as aet
from Complexity import ComplexityTest as ct
from CumulativeSum import CumulativeSums as cst
from FrequencyTest import FrequencyTest as ft
from Matrix import Matrix as mt
from RandomExcursions import RandomExcursions as ret
from RunTest import RunTest as rt
from Serial import Serial as serial
from Spectral import SpectralTest as st
from TemplateMatching import TemplateMatching as tm
from Universal import Universal as ut
from Tools import Tools

# Load configuration and check if all required variables are present
if not load_config():
    print("❌ Configuration error. Please check your .env file.")
    exit(1)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 1024  # 100GB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Get Google OAuth configuration
google_config = get_google_config()

# Initialize components
google_auth = GoogleAuth(
    google_config['client_id'], 
    google_config['client_secret'], 
    google_config['redirect_uri']
)
db_manager = DatabaseManager()
file_handler = LargeFileHandler()

# Create results directory
RESULTS_DIR = 'results'
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

class NISTTestSuite:
    def __init__(self):
        self.test_types = [
            '01. Frequency (Monobit) Test',
            '02. Frequency Test within a Block',
            '03. Runs Test',
            '04. Test for the Longest Run of Ones in a Block',
            '05. Binary Matrix Rank Test',
            '06. Discrete Fourier Transform (Spectral) Test',
            '07. Non-overlapping Template Matching Test',
            '08. Overlapping Template Matching Test',
            '09. Maurer\'s "Universal Statistical" Test',
            '10. Linear Complexity Test',
            '11. Serial Test',
            '12. Approximate Entropy Test',
            '13. Cumulative Sums Test (Forward)',
            '14. Cumulative Sums Test (Backward)',
            '15. Random Excursions Test',
            '16. Random Excursions Variant Test'
        ]
        
        self.test_functions = {
            0: ft.monobit_test,
            1: ft.block_frequency,
            2: rt.run_test,
            3: rt.longest_one_block_test,
            4: mt.binary_matrix_rank_text,
            5: st.spectral_test,
            6: tm.non_overlapping_test,
            7: tm.overlapping_patterns,
            8: ut.statistical_test,
            9: ct.linear_complexity_test,
            10: serial.serial_test,
            11: aet.approximate_entropy_test,
            12: cst.cumulative_sums_test,
            13: cst.cumulative_sums_test,
            14: ret.random_excursions_test,
            15: ret.variant_test
        }

    def execute_tests(self, binary_data, selected_tests):
        results = []
        
        for test_index in selected_tests:
            try:
                if test_index == 13:  # Cumulative Sums Test (Backward)
                    result = self.test_functions[test_index](binary_data, mode=1)
                else:
                    result = self.test_functions[test_index](binary_data)
                
                test_result = {
                    'test_name': self.test_types[test_index],
                    'test_index': test_index,
                    'result': result,
                    'success': True
                }
                results.append(test_result)
                
            except Exception as e:
                test_result = {
                    'test_name': self.test_types[test_index],
                    'test_index': test_index,
                    'result': None,
                    'error': str(e),
                    'success': False
                }
                results.append(test_result)
        
        return results

    def format_result(self, result, test_index):
        if not result:
            return {'p_value': 'N/A', 'conclusion': 'Error', 'details': ''}
        
        if test_index == 10:  # Serial Test
            return {
                'p_value_1': f"{result[0][0]:.6f}" if result[0][0] else 'N/A',
                'conclusion_1': 'Random' if result[0][1] else 'Non-Random',
                'p_value_2': f"{result[1][0]:.6f}" if result[1][0] else 'N/A',
                'conclusion_2': 'Random' if result[1][1] else 'Non-Random',
                'details': 'Serial Test has two components'
            }
        elif test_index in [14, 15]:  # Random Excursions Tests
            formatted_results = []
            for item in result:
                formatted_results.append({
                    'state': item[0],
                    'statistic': f"{item[2]:.6f}" if len(item) > 2 else 'N/A',
                    'p_value': f"{item[3]:.6f}" if len(item) > 3 else 'N/A',
                    'conclusion': 'Random' if item[4] else 'Non-Random'
                })
            return {'excursion_results': formatted_results}
        else:
            return {
                'p_value': f"{result[0]:.6f}" if result[0] else 'N/A',
                'conclusion': 'Random' if result[1] else 'Non-Random',
                'details': ''
            }

nist_suite = NISTTestSuite()

def require_authentication(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/auth/google')
def google_login():
    """Initiate Google OAuth"""
    try:
        authorization_url, state = google_auth.get_authorization_url()
        session['oauth_state'] = state
        print(f"🔗 Redirecting to Google OAuth: {authorization_url}")
        return redirect(authorization_url)
    except Exception as e:
        print(f"❌ Google OAuth error: {str(e)}")
        flash(f'OAuth configuration error: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            print(f"❌ OAuth error from Google: {error}")
            flash(f'Google authentication error: {error}', 'error')
            return redirect(url_for('login'))
        
        if not code or state != session.get('oauth_state'):
            print(f"❌ Invalid OAuth state or missing code")
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('login'))
        
        # Exchange code for user info
        user_info = google_auth.exchange_code_for_token(code, state)
        
        if not user_info:
            print(f"❌ Failed to get user info from Google")
            flash('Failed to get user information from Google.', 'error')
            return redirect(url_for('login'))
        
        print(f"✅ Successfully authenticated user: {user_info.get('email')}")
        
        # Check if user exists
        user = db_manager.get_user_by_google_id(user_info['sub'])
        
        if user:
            # User exists, log them in
            session['user'] = user
            session['google_user_info'] = user_info
            return redirect(url_for('index'))
        else:
            # New user, show institution form
            session['google_user_info'] = user_info
            return render_template('login.html', 
                                 show_institution_form=True,
                                 user_data={
                                     'email': user_info.get('email'),
                                     'name': user_info.get('name')
                                 })
    
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/complete_profile', methods=['POST'])
def complete_profile():
    """Complete user profile with institution details"""
    try:
        google_user_info = session.get('google_user_info')
        if not google_user_info:
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('login'))
        
        # Get form data
        institution = request.form.get('institution', '').strip()
        department = request.form.get('department', '').strip()
        position = request.form.get('position', '').strip()
        country = request.form.get('country', '').strip()
        
        if not institution or not position or not country:
            flash('Please fill in all required fields.', 'error')
            return render_template('login.html', 
                                 show_institution_form=True,
                                 user_data={
                                     'email': google_user_info.get('email'),
                                     'name': google_user_info.get('name'),
                                     'institution': institution,
                                     'department': department,
                                     'position': position,
                                     'country': country
                                 })
        
        # Create user account
        user_id = db_manager.add_user(
            google_id=google_user_info['sub'],
            email=google_user_info['email'],
            name=google_user_info['name'],
            institution=institution,
            department=department,
            position=position,
            country=country
        )
        
        # Get complete user data
        user = db_manager.get_user_by_google_id(google_user_info['sub'])
        session['user'] = user
        
        flash('Registration completed successfully!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Registration error: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@require_authentication
def index():
    """Main application page"""
    return render_template('index.html', test_types=nist_suite.test_types, user=session['user'])

# Add debug route to check configuration
@app.route('/debug/config')
def debug_config():
    """Debug route to check OAuth configuration"""
    if app.debug:
        config = get_google_config()
        return jsonify({
            'client_id': config['client_id'][:20] + '...' if config['client_id'] else 'Not set',
            'client_secret': 'Set' if config['client_secret'] else 'Not set',
            'redirect_uri': config['redirect_uri']
        })
    return "Debug mode disabled", 404

@app.route('/execute_tests', methods=['POST'])
@require_authentication
def execute_tests():
    try:
        start_time = time.time()
        data = request.get_json()
        
        # Get binary data
        binary_data = data.get('binary_data', '').strip()
        selected_tests = data.get('selected_tests', [])
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not binary_data:
            return jsonify({'error': 'No binary data provided'}), 400
        
        if not selected_tests:
            return jsonify({'error': 'No tests selected'}), 400
        
        # Validate binary data
        if not all(bit in '01' for bit in binary_data):
            return jsonify({'error': 'Binary data must contain only 0s and 1s'}), 400
        
        # Execute tests
        results = nist_suite.execute_tests(binary_data, selected_tests)
        
        # Format results for display
        formatted_results = []
        for result in results:
            if result['success']:
                formatted = nist_suite.format_result(result['result'], result['test_index'])
                formatted['test_name'] = result['test_name']
                formatted['test_index'] = result['test_index']
                formatted_results.append(formatted)
            else:
                formatted_results.append({
                    'test_name': result['test_name'],
                    'test_index': result['test_index'],
                    'error': result['error']
                })
        
        # Calculate statistics
        execution_time = time.time() - start_time
        total_tests = len(formatted_results)
        passed_tests = 0
        failed_tests = 0
        
        for result in formatted_results:
            if 'error' in result:
                failed_tests += 1
            elif 'excursion_results' in result:
                any_passed = any(exc['conclusion'] == 'Random' for exc in result['excursion_results'])
                if any_passed:
                    passed_tests += 1
                else:
                    failed_tests += 1
            elif 'p_value_1' in result:
                if result['conclusion_1'] == 'Random' and result['conclusion_2'] == 'Random':
                    passed_tests += 1
                else:
                    failed_tests += 1
            else:
                if result['conclusion'] == 'Random':
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Determine overall assessment
        if pass_rate >= 80:
            overall_assessment = "EXCELLENT"
        elif pass_rate >= 60:
            overall_assessment = "GOOD"
        elif pass_rate >= 40:
            overall_assessment = "FAIR"
        else:
            overall_assessment = "POOR"
        
        # Save results to file
        result_filename = f"nist_results_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        result_file_path = os.path.join(RESULTS_DIR, result_filename)
        
        with open(result_file_path, 'w', encoding='utf-8') as f:
            f.write(generate_comprehensive_report(
                formatted_results, binary_data, session['user'], 
                execution_time, total_tests, passed_tests, failed_tests, 
                pass_rate, overall_assessment, session_id
            ))
        
        # Log test execution
        test_log_data = {
            'original_filename': data.get('original_filename', 'Manual Input'),
            'file_size': data.get('file_size', len(binary_data)),
            'data_length': len(binary_data),
            'file_type': data.get('file_type', 'manual'),
            'selected_tests': selected_tests,
            'execution_time': execution_time,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'pass_rate': pass_rate,
            'overall_assessment': overall_assessment,
            'result_file_path': result_file_path
        }
        
        db_manager.log_test_execution(session['user']['id'], session_id, test_log_data)
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'data_length': len(binary_data),
            'session_id': session_id,
            'execution_time': execution_time,
            'statistics': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'pass_rate': pass_rate,
                'overall_assessment': overall_assessment
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_file', methods=['POST'])
@require_authentication
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        file_type = request.form.get('file_type', 'binary')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate session ID for this upload
        session_id = file_handler.generate_session_id()
        
        # Process large file upload
        result = file_handler.process_large_file_upload(file, file_type, session_id, db_manager)
        
        if result['success']:
            return jsonify({
                'success': True,
                'binary_data': result['binary_data'],
                'original_filename': result['original_filename'],
                'file_size': result['file_size'],
                'binary_length': len(result['binary_data']),
                'session_id': session_id
            })
        else:
            return jsonify({'error': result['error']}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_results', methods=['POST'])
@require_authentication
def download_results():
    try:
        data = request.get_json()
        results = data.get('results', [])
        binary_data = data.get('binary_data', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not results:
            return jsonify({'error': 'No results to download'}), 400
        
        # Calculate statistics
        total_tests = len(results)
        passed_tests = 0
        failed_tests = 0
        
        for result in results:
            if 'error' in result:
                failed_tests += 1
            elif 'excursion_results' in result:
                any_passed = any(exc['conclusion'] == 'Random' for exc in result['excursion_results'])
                if any_passed:
                    passed_tests += 1
                else:
                    failed_tests += 1
            elif 'p_value_1' in result:
                if result['conclusion_1'] == 'Random' and result['conclusion_2'] == 'Random':
                    passed_tests += 1
                else:
                    failed_tests += 1
            else:
                if result['conclusion'] == 'Random':
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Determine overall assessment
        if pass_rate >= 80:
            overall_assessment = "EXCELLENT"
        elif pass_rate >= 60:
            overall_assessment = "GOOD"
        elif pass_rate >= 40:
            overall_assessment = "FAIR"
        else:
            overall_assessment = "POOR"
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        
        # Write comprehensive results
        report_content = generate_comprehensive_report(
            results, binary_data, session['user'], 
            0, total_tests, passed_tests, failed_tests, 
            pass_rate, overall_assessment, session_id
        )
        
        temp_file.write(report_content)
        temp_file.close()
        
        filename = f'nist_comprehensive_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        return send_file(
            temp_file.name, 
            as_attachment=True, 
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

def generate_comprehensive_report(results, binary_data, user, execution_time, 
                                total_tests, passed_tests, failed_tests, 
                                pass_rate, overall_assessment, session_id):
    """Generate comprehensive test report"""
    
    report = []
    report.append('='*80)
    report.append('NIST 800-22 STATISTICAL TEST SUITE - COMPREHENSIVE RESULTS')
    report.append('='*80)
    report.append(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    report.append(f'Institution: Defence Institute of Advanced Technology (DIAT)')
    report.append(f'Test Suite Version: NIST SP 800-22 Rev. 1a')
    report.append(f'Session ID: {session_id}')
    report.append('='*80)
    report.append('')
    
    # User Information
    report.append('USER INFORMATION')
    report.append('-'*50)
    report.append(f'Name: {user["name"]}')
    report.append(f'Email: {user["email"]}')
    report.append(f'Institution: {user.get("institution", "N/A")}')
    report.append(f'Department: {user.get("department", "N/A")}')
    report.append(f'Position: {user.get("position", "N/A")}')
    report.append(f'Country: {user.get("country", "N/A")}')
    report.append('')
    
    # Assessment Summary
    report.append('ASSESSMENT SUMMARY')
    report.append('-'*50)
    report.append(f'Data Length: {len(binary_data):,} bits')
    report.append(f'Total Tests Executed: {total_tests}')
    report.append(f'Tests Passed: {passed_tests}')
    report.append(f'Tests Failed: {failed_tests}')
    report.append(f'Pass Rate: {pass_rate:.1f}%')
    report.append(f'Overall Assessment: {overall_assessment}')
    if execution_time > 0:
        report.append(f'Execution Time: {execution_time:.2f} seconds')
    report.append('')
    
    # Binary Data Section
    report.append('UPLOADED BINARY DATA')
    report.append('-'*50)
    report.append(f'Total Length: {len(binary_data):,} bits')
    report.append(f'Data Preview (First 500 bits):')
    preview_length = min(500, len(binary_data))
    report.append(binary_data[:preview_length])
    if len(binary_data) > preview_length:
        report.append(f'... (showing first {preview_length} of {len(binary_data):,} total bits)')
    report.append('')
    
    # Detailed Results
    report.append('DETAILED TEST RESULTS WITH P-VALUES')
    report.append('-'*50)
    report.append(f'{"Test Name":<50} {"P-Value":<15} {"Result":<15} {"Status":<10}')
    report.append('-'*90)
    
    for result in results:
        if 'error' in result:
            report.append(f'{result["test_name"]:<50} {"ERROR":<15} {"N/A":<15} {"FAILED":<10}')
        elif 'excursion_results' in result:
            report.append(f'{result["test_name"]}:')
            for exc_result in result['excursion_results']:
                status = "PASSED" if exc_result["conclusion"] == "Random" else "FAILED"
                report.append(f'  State {exc_result["state"]:<10} {exc_result["p_value"]:<15} {exc_result["conclusion"]:<15} {status:<10}')
        elif 'p_value_1' in result:
            status1 = "PASSED" if result["conclusion_1"] == "Random" else "FAILED"
            status2 = "PASSED" if result["conclusion_2"] == "Random" else "FAILED"
            report.append(f'{(result["test_name"] + " (1)"):<50} {result["p_value_1"]:<15} {result["conclusion_1"]:<15} {status1:<10}')
            report.append(f'{(result["test_name"] + " (2)"):<50} {result["p_value_2"]:<15} {result["conclusion_2"]:<15} {status2:<10}')
        else:
            status = "PASSED" if result["conclusion"] == "Random" else "FAILED"
            report.append(f'{result["test_name"]:<50} {result["p_value"]:<15} {result["conclusion"]:<15} {status:<10}')
    
    # Assessment and Recommendations
    report.append('')
    report.append('='*80)
    report.append('ASSESSMENT LEVELS AND INTERPRETATION')
    report.append('='*80)
    report.append('Pass Rate Interpretation:')
    report.append('• EXCELLENT (≥80%): High quality randomness, suitable for cryptographic use')
    report.append('• GOOD (≥60%): Acceptable randomness, suitable for most applications')
    report.append('• FAIR (≥40%): Moderate randomness, review generator implementation')
    report.append('• POOR (<40%): Significant randomness deficiencies, not suitable for security')
    report.append('')
    
    report.append('P-Value Interpretation:')
    report.append('• P-Value ≥ 0.01: Test PASSED (sequence appears random)')
    report.append('• P-Value < 0.01: Test FAILED (sequence shows non-random patterns)')
    report.append('')
    
    report.append('Current Assessment Details:')
    report.append(f'• Your data achieved a {pass_rate:.1f}% pass rate')
    report.append(f'• Assessment Level: {overall_assessment}')
    
    # Recommendations based on assessment
    report.append('')
    if pass_rate >= 80:
        report.append('RECOMMENDATIONS:')
        report.append('✓ Excellent randomness quality detected')
        report.append('✓ Data is suitable for cryptographic applications')
        report.append('✓ Random number generator appears to be functioning correctly')
    elif pass_rate >= 60:
        report.append('RECOMMENDATIONS:')
        report.append('• Good randomness quality with room for improvement')
        report.append('• Investigate failed tests for potential optimizations')
        report.append('• Suitable for most non-critical applications')
    elif pass_rate >= 40:
        report.append('RECOMMENDATIONS:')
        report.append('⚠ Moderate randomness concerns detected')
        report.append('⚠ Review random number generator implementation')
        report.append('⚠ Not recommended for security-critical applications')
    else:
        report.append('RECOMMENDATIONS:')
        report.append('✗ Significant randomness deficiencies detected')
        report.append('✗ Random number generator requires immediate attention')
        report.append('✗ Do not use for any security or cryptographic applications')
    
    report.append('')
    report.append('='*80)
    report.append('Report generated by NIST 800-22 Test Suite Web Interface')
    report.append('Defence Institute of Advanced Technology (DIAT)')
    report.append('Made by Utkarsh Kumar Singh')
    report.append('='*80)
    
    return '\n'.join(report)

if __name__ == '__main__':
    print("🚀 Starting NIST Test Suite Application...")
    print(f"📊 Google Client ID: {google_config['client_id'][:20]}..." if google_config['client_id'] else "❌ Google Client ID not set")
    print(f"🔗 Redirect URI: {google_config['redirect_uri']}")
    app.run(host='0.0.0.0', port=5000, debug=True)
