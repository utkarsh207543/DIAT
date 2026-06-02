# app.py - Flask API backend for NIST 800-22 web interface

from flask import Flask, request, jsonify
from flask_cors import CORS

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

app = Flask(__name__)
CORS(app)

TEST_FUNCTIONS = {
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
    13: lambda data: cst.cumulative_sums_test(data, mode=1),
    14: ret.random_excursions_test,
    15: ret.variant_test
}

@app.route("/api/run_tests", methods=["POST"])
def run_tests():
    try:
        data = request.get_json()
        binary_data = data.get("binary_data", "")
        test_indices = data.get("tests", [])

        results = [None] * 16

        for idx in test_indices:
            try:
                if idx == 10:
                    r = TEST_FUNCTIONS[idx](binary_data)
                    results[idx] = {
                        "pValue": f"{r[0][0]:.6f}, {r[1][0]:.6f}",
                        "result": r[0][1] and r[1][1]
                    }
                elif idx in [14, 15]:
                    subresults = TEST_FUNCTIONS[idx](binary_data)
                    all_pass = all([r[-1] for r in subresults])
                    results[idx] = {
                        "pValue": "multiple",
                        "result": all_pass,
                        "details": subresults
                    }
                else:
                    r = TEST_FUNCTIONS[idx](binary_data)
                    results[idx] = {
                        "pValue": f"{r[0]:.6f}",
                        "result": r[1]
                    }
            except Exception as e:
                results[idx] = {
                    "pValue": "Error",
                    "result": False,
                    "error": str(e)
                }

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)