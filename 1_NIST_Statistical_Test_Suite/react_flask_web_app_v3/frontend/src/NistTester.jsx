
import React, { useState } from "react";

export default function NistTester() {
  const [binaryData, setBinaryData] = useState("");
  const [results, setResults] = useState(Array(16).fill({ pValue: "", result: "" }));
  const [selectedTests, setSelectedTests] = useState(Array(16).fill(false));

  const testNames = [
    "Frequency (Monobit) Test",
    "Frequency Test within a Block",
    "Runs Test",
    "Test for the Longest Run of Ones in a Block",
    "Binary Matrix Rank Test",
    "Discrete Fourier Transform (Spectral) Test",
    "Non-overlapping Template Matching Test",
    "Overlapping Template Matching Test",
    "Maurer's 'Universal Statistical' Test",
    "Linear Complexity Test",
    "Serial Test",
    "Approximate Entropy Test",
    "Cumulative Sums Test (Forward)",
    "Cumulative Sums Test (Backward)",
    "Random Excursions Test",
    "Random Excursions Variant Test",
  ];

  const toggleSelectAll = (selectAll) => {
    setSelectedTests(Array(16).fill(selectAll));
  };

  const executeTests = async () => {
    const selected = selectedTests
      .map((val, idx) => (val ? idx : null))
      .filter((v) => v !== null);

    const response = await fetch("/api/run_tests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ binary_data: binaryData, tests: selected }),
    });
    const data = await response.json();
    setResults(data);
  };

  return (
    <div className="bg-gray-100 min-h-screen p-8">
      <header className="bg-white shadow rounded-xl px-6 py-4 mb-8">
        <h1 className="text-3xl font-bold text-blue-800">NIST 800-22 Randomness Test Suite</h1>
        <p className="text-sm text-gray-600 mt-1">Developed by DRDO DIAT • Web Interface</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <textarea
          rows={4}
          value={binaryData}
          onChange={(e) => setBinaryData(e.target.value)}
          placeholder="Paste binary data here..."
          className="col-span-2 p-3 border border-gray-300 rounded-xl shadow-sm focus:outline-blue-400"
        />
        <div className="flex flex-col gap-2">
          <button className="bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700">Upload Binary File</button>
          <button className="bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700">Upload Text File</button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-y-2">
          <thead className="text-left text-sm text-gray-600">
            <tr>
              <th className="pr-4">Test</th>
              <th className="text-center">P-Value</th>
              <th className="text-center">Result</th>
              <th className="text-center">Run?</th>
            </tr>
          </thead>
          <tbody className="text-sm text-gray-800">
            {testNames.map((name, i) => (
              <tr key={i} className="bg-gray-50 hover:bg-gray-100 rounded-xl">
                <td className="py-2 pr-4 font-medium">{`${(i + 1).toString().padStart(2, "0")}. ${name}`}</td>
                <td className="text-center">{results[i].pValue}</td>
                <td className={`text-center font-semibold ${
                    results[i].result === true ? "text-green-600" :
                    results[i].result === false ? "text-red-500" : "text-gray-400"
                }`}>
                  {results[i].result === true ? "Random" :
                   results[i].result === false ? "Non-Random" : "-"}
                </td>
                <td className="text-center">
                  <input
                    type="checkbox"
                    checked={selectedTests[i]}
                    onChange={() => {
                      const updated = [...selectedTests];
                      updated[i] = !updated[i];
                      setSelectedTests(updated);
                    }}
                    className="w-4 h-4"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap gap-3 mt-8">
        <button onClick={() => toggleSelectAll(true)} className="bg-blue-700 text-white px-5 py-2 rounded-xl hover:bg-blue-800">
          Select All
        </button>
        <button onClick={() => toggleSelectAll(false)} className="bg-yellow-500 text-white px-5 py-2 rounded-xl hover:bg-yellow-600">
          Deselect All
        </button>
        <button onClick={executeTests} className="bg-green-600 text-white px-5 py-2 rounded-xl hover:bg-green-700">
          Execute Test
        </button>
        <button className="bg-gray-700 text-white px-5 py-2 rounded-xl hover:bg-gray-800">
          Export Results
        </button>
        <button onClick={() => window.location.reload()} className="bg-red-500 text-white px-5 py-2 rounded-xl hover:bg-red-600">
          Reset
        </button>
      </div>

      <footer className="mt-12 text-sm text-center text-gray-500">
        &copy; 2024 DRDO DIAT • Web Version of NIST 800-22 Suite
      </footer>
    </div>
  );
}
