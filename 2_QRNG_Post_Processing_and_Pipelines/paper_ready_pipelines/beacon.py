# Create a single "paper-ready" pipeline that:
# - reads your QRNG file (0/1 text, hex text, or raw bytes)
# - computes paper-usable metrics: sliding-window bias stability, CUSUM drift stats, short-lag autocorr, run-length distribution
# - builds a mini verifiable "beacon" from your data and summarizes first few epochs
# - writes: CSV summary, PNG figures, and ready-to-paste LaTeX tables (.tex)
#
# Usage (examples):
#   python paper_ready_qrng_pipeline_1.py --in data.txt --format bin --out outputs
#   python paper_ready_qrng_pipeline_1.py --in stream.hex --format hex --window 500000 --beacon_bits 2048
#
# Outputs in --out:
#   - results_summary.csv
#   - bias_over_time.png, drift_cusum.png, autocorr.png, run_lengths.png
#   - table_qrng_metrics.tex, table_beacon_epochs.tex
#
import os, pathlib, json, math, hashlib, argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SCRIPT = "/mnt/data/paper_ready_qrng_pipeline_1.py"

code = r'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, pathlib, json, math, hashlib, argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def read_bits(path: str, fmt: str = "auto") -> np.ndarray:
    p = pathlib.Path(path)
    data = p.read_bytes()
    if fmt == "auto":
        try:
            s = data.decode("utf-8", errors="ignore").strip()
        except Exception:
            s = ""
        if len(s) and all(ch in "01 \n\r\t" for ch in s[: min(10000, len(s))]):
            fmt = "bin"
        elif len(s) and all(ch in "0123456789abcdefABCDEF \n\r\t" for ch in s[: min(10000, len(s))]):
            fmt = "hex"
        else:
            fmt = "raw"
    if fmt == "bin":
        s = p.read_text().replace("\n", "").replace("\r", "").replace(" ", "")
        arr = np.frombuffer(s.encode("ascii"), dtype=np.uint8) - ord('0')
        arr = arr[(arr == 0) | (arr == 1)]
        return arr.astype(np.uint8)
    elif fmt == "hex":
        s = p.read_text().replace("\n", "").replace("\r", "").replace(" ", "")
        by = bytes.fromhex(s)
        return np.unpackbits(np.frombuffer(by, dtype=np.uint8)).astype(np.uint8)
    elif fmt == "raw":
        by = data
        return np.unpackbits(np.frombuffer(by, dtype=np.uint8)).astype(np.uint8)
    else:
        raise ValueError("Unknown format: " + fmt)

def sliding_windows(n: int, win: int, overlap: float = 0.5):
    if win >= n:
        yield slice(0, n)
        return
    step = max(1, int(win * (1 - overlap)))
    i = 0
    while i + win <= n:
        yield slice(i, i + win)
        i += step
    if i < n:
        yield slice(n - win, n)

def plot_bias_over_time(bits: np.ndarray, outpng: str, window: int, bias_tol: float) -> dict:
    centers, biases = [], []
    n = len(bits)
    for s in sliding_windows(n, window, overlap=0.5):
        centers.append((s.start + s.stop)//2)
        biases.append(float(bits[s].mean()))
    biases = np.array(biases, dtype=float)
    centers = np.array(centers, dtype=int)
    dev = np.abs(biases - 0.5)
    frac_within = float(np.mean(dev <= bias_tol)) if len(dev) else float('nan')
    max_dev = float(np.max(dev)) if len(dev) else float('nan')

    plt.figure()
    plt.plot(centers, biases)
    plt.axhline(0.5)
    plt.axhline(0.5 + bias_tol, linestyle="--")
    plt.axhline(0.5 - bias_tol, linestyle="--")
    plt.xlabel("Sample index")
    plt.ylabel("Proportion of 1s")
    plt.title("Sliding-window bias")
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()
    return {"frac_windows_within_tol": frac_within, "max_abs_deviation": max_dev, "num_windows": int(len(biases))}

def cusum_two_sided(x: np.ndarray, k: float = 0.005):
    gp = np.zeros_like(x, dtype=float)
    gn = np.zeros_like(x, dtype=float)
    Sp = 0.0; Sn = 0.0
    for i, xi in enumerate(x):
        Sp = max(0.0, Sp + xi - k)
        Sn = min(0.0, Sn + xi + k)
        gp[i] = Sp; gn[i] = Sn
    return gp, gn

def plot_cusum(bits: np.ndarray, outpng: str, k: float, h: float) -> dict:
    x = bits.astype(float) - 0.5
    gp, gn = cusum_two_sided(x, k=k)
    gp_max = float(np.max(gp)); gn_min = float(np.min(gn))
    alarms = int((gp_max >= h) or (abs(gn_min) >= h))
    plt.figure()
    plt.plot(gp)
    plt.plot(gn)
    plt.axhline(h, linestyle="--")
    plt.axhline(-h, linestyle="--")
    plt.xlabel("Sample index")
    plt.ylabel("CUSUM statistic")
    plt.title("CUSUM drift detection")
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()
    return {"gp_max": gp_max, "gn_min": gn_min, "alarms": alarms}

def plot_autocorr(bits: np.ndarray, outpng: str, max_lag: int = 64) -> dict:
    x = bits.astype(float)
    x = (x - x.mean()) / (x.std() + 1e-12)
    n = len(x)
    ac = np.zeros(max_lag+1, dtype=float)
    ac[0] = 1.0
    for k in range(1, max_lag+1):
        ac[k] = float(np.dot(x[:-k], x[k:]) / (n - k))
    plt.figure()
    plt.stem(range(len(ac)), ac, use_line_collection=True)
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.title("Short-lag autocorrelation")
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()
    return {"autocorr_lag1": float(ac[1]) if len(ac)>1 else float('nan'),
            "autocorr_lag2": float(ac[2]) if len(ac)>2 else float('nan')}

def plot_run_lengths(bits: np.ndarray, outpng: str, max_show: int = 64) -> dict:
    if len(bits) == 0:
        return {}
    diffs = np.diff(np.where(np.concatenate(([bits[0]], bits[:-1] != bits[1:], [True])))[0])
    vals, counts = np.unique(diffs, return_counts=True)
    mask = vals <= max_show
    vals, counts = vals[mask], counts[mask]
    plt.figure()
    plt.bar(vals, counts, width=0.8)
    plt.xlabel("Run length")
    plt.ylabel("Count")
    plt.title("Run-length distribution")
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()
    return {"run_lengths": int(len(vals)), "max_run_len_shown": int(max(vals) if len(vals) else 0)}

def bits_to_bytes(bits: np.ndarray) -> bytes:
    if len(bits) == 0: return b""
    pad = (-len(bits)) % 8
    if pad: bits = np.concatenate([bits, np.zeros(pad, dtype=np.uint8)])
    bits = bits.reshape(-1, 8)
    vals = (bits * (1 << np.arange(7, -1, -1, dtype=np.uint8))).sum(axis=1).astype(np.uint8)
    return vals.tobytes()

def sha256(*chunks: bytes) -> bytes:
    h = hashlib.sha256()
    for c in chunks: h.update(c)
    return h.digest()

def mini_beacon(bits: np.ndarray, bits_per_epoch: int, context: str, epochs_out: int = 10):
    total = int(bits.size)
    epochs = total // bits_per_epoch
    init = sha256(b"QRB-1", bits_per_epoch.to_bytes(8,"big"), context.encode())
    prev = init
    rows = []
    for i in range(min(epochs, epochs_out)):
        s = i*bits_per_epoch; e=s+bits_per_epoch
        chunk = bits[s:e]
        out = sha256(prev, bits_to_bytes(chunk), i.to_bytes(8,"big"), context.encode()).hex()
        bias = float(chunk.mean())
        rows.append({"epoch": i, "start_bit": s, "end_bit": e, "bias": bias, "output_hex": out})
        prev = bytes.fromhex(out)
    return rows, epochs

def write_latex_table_metrics(path: str, metrics: dict):
    tex = r'''\begin{table}[t]
\centering
\caption{SPDC-QRNG stability and drift metrics.}
\label{tab:qrng_metrics}
\begin{tabular}{l r}
\hline
Total bits & %(num_bits)s \\
Overall bias $p(1)$ & %(overall_bias).6f \\
Window size & %(window)d \\
Bias tolerance & $\pm$%(bias_tol).4f \\
Windows within tol & %(frac_within_tol).2f\%% \\
Max $|p-0.5|$ & %(max_abs_dev).6f \\
CUSUM $k$ & %(cusum_k).4f \\
CUSUM $h$ & %(cusum_h).4f \\
$\max(G^+)$ & %(gp_max).4f \\
$\min(G^-)$ & %(gn_min).4f \\
Alarms & %(alarms)d \\
Autocorr lag 1 & %(ac1).6f \\
Autocorr lag 2 & %(ac2).6f \\
\hline
\end{tabular}
\end{table}
''' % {
        "num_bits": f"{metrics['num_bits']:,}",
        "overall_bias": metrics["overall_bias"],
        "window": metrics["window"],
        "bias_tol": metrics["bias_tol"],
        "frac_within_tol": 100.0*metrics["frac_within_tol"],
        "max_abs_dev": metrics["max_abs_dev"],
        "cusum_k": metrics["cusum_k"],
        "cusum_h": metrics["cusum_h"],
        "gp_max": metrics["gp_max"],
        "gn_min": metrics["gn_min"],
        "alarms": metrics["alarms"],
        "ac1": metrics["ac1"],
        "ac2": metrics["ac2"],
    }
    with open(path, "w", encoding="utf-8") as f:
        f.write(tex)

def write_latex_table_beacon(path: str, rows: list, bits_per_epoch: int, epochs_total: int):
    def short(h): return h[:16] + "…" + h[-8:] if len(h) > 24 else h
    lines = [r'\begin{table}[t]',
             r'\centering',
             r'\caption{Verifiable quantum randomness beacon (first epochs, %d bits/epoch; total epochs = %d).}' % (bits_per_epoch, epochs_total),
             r'\label{tab:qrng_beacon}',
             r'\begin{tabular}{r r r l}',
             r'\hline',
             r'Epoch & Start & End & Output (SHA-256 hex) \\',
             r'\hline']
    for r in rows:
        lines.append(f"{r['epoch']} & {r['start_bit']} & {r['end_bit']} & {short(r['output_hex'])} \\\\")
    lines += [r'\hline', r'\end{tabular}', r'\end{table}']
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="QRNG file path")
    ap.add_argument("--format", dest="fmt", default="auto", choices=["auto","bin","hex","raw"], help="Input format")
    ap.add_argument("--out", dest="outdir", default="outputs", help="Output directory")
    ap.add_argument("--window", type=int, default=1_000_000, help="Sliding window size")
    ap.add_argument("--bias_tol", type=float, default=0.005, help="Bias tolerance per window")
    ap.add_argument("--cusum_k", type=float, default=0.005, help="CUSUM reference value")
    ap.add_argument("--cusum_h", type=float, default=0.05, help="CUSUM decision threshold")
    ap.add_argument("--beacon_bits", type=int, default=2048, help="Bits per beacon epoch")
    ap.add_argument("--context", type=str, default="SPDC-QRNG Beacon", help="Beacon context string")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    bits = read_bits(args.inp, args.fmt)
    n = int(bits.size)
    overall_bias = float(bits.mean()) if n else float('nan')

    # Figures + metrics
    bias_info = plot_bias_over_time(bits, os.path.join(args.outdir, "bias_over_time.png"), args.window, args.bias_tol)
    cusum_info = plot_cusum(bits, os.path.join(args.outdir, "drift_cusum.png"), args.cusum_k, args.cusum_h)
    ac_info = plot_autocorr(bits, os.path.join(args.outdir, "autocorr.png"), max_lag=64)
    rl_info = plot_run_lengths(bits, os.path.join(args.outdir, "run_lengths.png"), max_show=64)

    # Beacon preview
    beacon_rows, beacon_total = mini_beacon(bits, args.beacon_bits, args.context, epochs_out=10)

    # CSV summary
    summary = {
        "num_bits": n,
        "overall_bias": overall_bias,
        "window": args.window,
        "bias_tol": args.bias_tol,
        "frac_within_tol": bias_info.get("frac_windows_within_tol", float('nan')),
        "max_abs_dev": bias_info.get("max_abs_deviation", float('nan')),
        "cusum_k": args.cusum_k,
        "cusum_h": args.cusum_h,
        "gp_max": cusum_info.get("gp_max", float('nan')),
        "gn_min": cusum_info.get("gn_min", float('nan')),
        "alarms": cusum_info.get("alarms", 0),
        "autocorr_lag1": ac_info.get("autocorr_lag1", float('nan')),
        "autocorr_lag2": ac_info.get("autocorr_lag2", float('nan')),
        "beacon_bits_per_epoch": args.beacon_bits,
        "beacon_epochs_total": beacon_total
    }
    pd.DataFrame([summary]).to_csv(os.path.join(args.outdir, "results_summary.csv"), index=False)

    # LaTeX tables
    write_latex_table_metrics(os.path.join(args.outdir, "table_qrng_metrics.tex"), {
        "num_bits": n,
        "overall_bias": overall_bias,
        "window": args.window,
        "bias_tol": args.bias_tol,
        "frac_within_tol": bias_info.get("frac_windows_within_tol", float('nan')),
        "max_abs_dev": bias_info.get("max_abs_deviation", float('nan')),
        "cusum_k": args.cusum_k,
        "cusum_h": args.cusum_h,
        "gp_max": cusum_info.get("gp_max", float('nan')),
        "gn_min": cusum_info.get("gn_min", float('nan')),
        "alarms": cusum_info.get("alarms", 0),
        "ac1": ac_info.get("autocorr_lag1", float('nan')),
        "ac2": ac_info.get("autocorr_lag2", float('nan')),
    })

    write_latex_table_beacon(os.path.join(args.outdir, "table_beacon_epochs.tex"), beacon_rows, args.beacon_bits, beacon_total)

    # Console summary
    print("=== Paper-Ready QRNG Pipeline ===")
    print(f"Bits: {n:,} | Overall bias p(1)={overall_bias:.6f}")
    print(f"Windows within ±{args.bias_tol:.4f}: {100.0*summary['frac_within_tol']:.2f}% | Max |p-0.5|={summary['max_abs_dev']:.6f}")
    print(f"CUSUM: k={args.cusum_k:.4f}, h={args.cusum_h:.4f} | gp_max={summary['gp_max']:.4f}, gn_min={summary['gn_min']:.4f}, alarms={summary['alarms']}")
    print(f"Beacon: bits/epoch={args.beacon_bits} | total epochs={beacon_total} (showing first 10 in table_beacon_epochs.tex)")
    print(f"Artifacts written to: {args.outdir}")

if __name__ == "__main__":
    main()
'''
with open(SCRIPT, "w", encoding="utf-8") as f:
    f.write(code)

SCRIPT
