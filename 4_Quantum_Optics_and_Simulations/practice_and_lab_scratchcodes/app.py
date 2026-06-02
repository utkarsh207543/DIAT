from flask import Flask, render_template, request
import tests  # Assuming your test functions are in tests.py

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        test_data = request.form['test_data']
        # Assuming a simple test function 'run_test' in tests.py
        result = tests.run_test(test_data)
        return render_template('index.html', result=result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)        #localhost:5000
    app.run(host='192.168.22.78', port=5000,debug=True)
