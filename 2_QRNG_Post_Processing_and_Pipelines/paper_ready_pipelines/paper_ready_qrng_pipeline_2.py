#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, pathlib, argparse, hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------
# I/O: read bits in bin/hex/raw
# ------------------------------
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
        return np.unpackbits(np.frombuffer(by, dtype=np.uint8), bitorder='big').astype(np.uint8)

    elif fmt == "raw":
        by = data
        return np.unpackbits(np.frombuffer(by, dtype=np.uint8), bitorder='big').astype(np.uint8)

    else:
        raise ValueError("Unknown format: " + fmt)

# ------------------------------
# Helpers
# ------------------------------
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

# ------------------------------
# Plots & metrics
# ------------------------------
def plot_bias_over_time(bits: np.ndarray, outpng: str, window: int, bias_tol: float) -> dict:
    centers, biases = [], []
    n = len(bits)
    for s in sliding_windows(n, window, overlap=0.5):
        centers.append((s.start + s.stop) // 2)
        biases.append(float(bits[s].mean()))
    biases = np.array(biases, dtype=float)
    centers = np.array(centers, dtype=int)
    dev = np.abs(biases - 0.5)
    frac_within = float(np.mean(dev <= bias_tol)) if len(dev) else float('nan')
    max_dev = float(np.max(dev)) if len(dev) else float('nan')

    # downsample for plotting performance if needed
    max_points = 20000
    if len(biases) > max_points:
        idx = np.linspace(0, len(biases) - 1, max_points).astype(int)
        plot_x = centers[idx]; plot_y = biases[idx]
    else:
        plot_x = centers; plot_y = biases

    plt.figure()
    plt.plot(plot_x, plot_y)
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
    if x.size == 0:
        plt.figure(); plt.title("CUSUM drift detection (no data)")
        plt.savefig(outpng, dpi=200); plt.close()
        return {"gp_max": float('nan'), "gn_min": float('nan'), "alarms": 0}
    gp, gn = cusum_two_sided(x, k=k)
    gp_max = float(np.max(gp)) if gp.size else float('nan')
    gn_min = float(np.min(gn)) if gn.size else float('nan')
    alarms = int((gp_max >= h) or (abs(gn_min) >= h))
    plt.figure()
    plt.plot(gp, label="G+")
    plt.plot(gn, label="G-")
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
    if x.size == 0:
        plt.figure(); plt.title("Autocorrelation (no data)")
        plt.savefig(outpng, dpi=200); plt.close()
        return {"autocorr_lag1": float('nan'), "autocorr_lag2": float('nan')}
    x = (x - x.mean()) / (x.std() + 1e-12)
    n = len(x)
    ac = np.zeros(max_lag + 1, dtype=float)
    ac[0] = 1.0
    for k in range(1, max_lag + 1):
        ac[k] = float(np.dot(x[:-k], x[k:]) / (n - k))
    plt.figure()
    plt.stem(range(len(ac)), ac)
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.title("Short-lag autocorrelation")
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()
    return {
        "autocorr_lag1": float(ac[1]) if len(ac) > 1 else float('nan'),
        "autocorr_lag2": float(ac[2]) if len(ac) > 2 else float('nan')
    }

def plot_run_lengths(bits: np.ndarray, outpng: str, max_show: int = 64) -> dict:
    if len(bits) == 0:
        plt.figure(); plt.title("Run-length distribution (no data)")
        plt.savefig(outpng, dpi=200); plt.close()
        return {"run_lengths": 0, "max_run_len_shown": 0}
    # BUGFIX: correct sentinels—always start & end a run
    boundaries = np.where(np.concatenate(([True], bits[1:] != bits[:-1], [True])))[0]
    diffs = np.diff(boundaries)
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

# ------------------------------
# Hashing / beacon
# ------------------------------
def bits_to_bytes(bits: np.ndarray) -> bytes:
    """Fast & robust bits->bytes using packbits (big-endian within each byte)."""
    if bits.size == 0:
        return b""
    pad = (-bits.size) % 8
    if pad:
        bits = np.concatenate([bits, np.zeros(pad, dtype=np.uint8)])
    return np.packbits(bits.reshape(-1, 8), axis=1, bitorder='big').ravel().tobytes()

def sha256(*chunks: bytes) -> bytes:
    h = hashlib.sha256()
    for c in chunks:
        h.update(c)
    return h.digest()

def mini_beacon(bits: np.ndarray, bits_per_epoch: int, context: str, epochs_out: int = 10):
    """Returns (preview_rows, total_epochs) while computing full rows on demand."""
    total = int(bits.size)
    epochs = total // bits_per_epoch
    init = sha256(b"QRB-1", bits_per_epoch.to_bytes(8, "big"), context.encode())
    prev = init
    rows_preview = []
    for i in range(epochs):
        s = i * bits_per_epoch
        e = s + bits_per_epoch
        chunk = bits[s:e]
        out = sha256(prev, bits_to_bytes(chunk), i.to_bytes(8, "big"), context.encode()).hex()
        if i < epochs_out:
            bias = float(chunk.mean())
            rows_preview.append({"epoch": i, "start_bit": s, "end_bit": e, "bias": bias, "output_hex": out})
        prev = bytes.fromhex(out)
    return rows_preview, epochs

def iterate_beacon_rows(bits: np.ndarray, bits_per_epoch: int, context: str):
    """Generator yielding all beacon rows (epoch,start,end,output_hex) with full hashes."""
    total = int(bits.size)
    epochs = total // bits_per_epoch
    init = sha256(b"QRB-1", bits_per_epoch.to_bytes(8, "big"), context.encode())
    prev = init
    for i in range(epochs):
        s = i * bits_per_epoch
        e = s + bits_per_epoch
        chunk = bits[s:e]
        out = sha256(prev, bits_to_bytes(chunk), i.to_bytes(8, "big"), context.encode()).hex()
        yield {"epoch": i, "start_bit": s, "end_bit": e, "output_hex": out}
        prev = bytes.fromhex(out)

# ------------------------------
# LaTeX writers
# ------------------------------
def write_latex_table_metrics(path: str, m: dict):
    lines = []
    lines.append("\\begin{table}[t]")
    lines.append("\\centering")
    lines.append("\\caption{SPDC-QRNG stability and drift metrics.}")
    lines.append("\\label{tab:qrng_metrics}")
    lines.append("\\begin{tabular}{l r}")
    lines.append("\\hline")
    lines.append(f"Total bits & {m['num_bits']:,} \\\\")
    lines.append(f"Overall bias $p(1)$ & {m['overall_bias']:.6f} \\\\")
    lines.append(f"Window size & {m['window']} \\\\")
    lines.append(f"Bias tolerance & $\\pm${m['bias_tol']:.4f} \\\\")
    lines.append(f"Windows within tol & {100.0*m['frac_within_tol']:.2f}\\% \\\\")
    lines.append(f"Max $|p-0.5|$ & {m['max_abs_dev']:.6f} \\\\")
    lines.append(f"CUSUM $k$ & {m['cusum_k']:.4f} \\\\")
    lines.append(f"CUSUM $h$ & {m['cusum_h']:.4f} \\\\")
    lines.append(f"$\\max(G^+)$ & {m['gp_max']:.4f} \\\\")
    lines.append(f"$\\min(G^-)$ & {m['gn_min']:.4f} \\\\")
    lines.append(f"Alarms & {m['alarms']} \\\\")
    lines.append(f"Autocorr lag 1 & {m['ac1']:.6f} \\\\")
    lines.append(f"Autocorr lag 2 & {m['ac2']:.6f} \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_latex_table_beacon(path: str, rows: list, bits_per_epoch: int, epochs_total: int):
    def short(h): return h[:16] + "…" + h[-8:] if len(h) > 24 else h
    lines = []
    lines.append("\\begin{table}[t]")
    lines.append("\\centering")
    lines.append(f"\\caption{{Verifiable quantum randomness beacon (first epochs, {bits_per_epoch} bits/epoch; total epochs = {epochs_total}).}}")
    lines.append("\\label{tab:qrng_beacon}")
    lines.append("\\begin{tabular}{r r r l}")
    lines.append("\\hline")
    lines.append("Epoch & Start & End & Output (SHA-256 hex) \\\\")
    lines.append("\\hline")
    for r in rows:
        lines.append(f"{r['epoch']} & {r['start_bit']} & {r['end_bit']} & {short(r['output_hex'])} \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_latex_table_beacon_full(path: str, bits: np.ndarray, bits_per_epoch: int, context: str):
    """
    Writes ALL epochs with FULL hashes using longtable for appendix use.
    Requires \\usepackage{longtable} in your LaTeX preamble.
    """
    lines = []
    lines.append("% Auto-generated full epoch table for appendix")
    lines.append("\\setlength{\\tabcolsep}{6pt}")
    lines.append("\\renewcommand{\\arraystretch}{1.1}")
    lines.append("\\begin{longtable}{r r r l}")
    # Escape braces in f-string for LaTeX \caption and \label
    lines.append(
        f"\\caption{{Complete beacon epochs ({bits_per_epoch} bits per epoch; full SHA-256 outputs).}}"
        f"\\label{{{{tab:beacon_full}}}}\\\\"
    )
    lines.append("\\hline")
    lines.append("Epoch & Start & End & Output (SHA-256 hex) \\\\")
    lines.append("\\hline")
    lines.append("\\endfirsthead")
    lines.append("\\hline Epoch & Start & End & Output (SHA-256 hex) \\\\ \\hline")
    lines.append("\\endhead")
    lines.append("\\hline \\multicolumn{4}{r}{Continued on next page} \\\\ \\hline")
    lines.append("\\endfoot")
    lines.append("\\hline")
    lines.append("\\endlastfoot")

    for r in iterate_beacon_rows(bits, bits_per_epoch, context):
        lines.append(f"{r['epoch']} & {r['start_bit']} & {r['end_bit']} & {r['output_hex']} \\\\")

    lines.append("\\end{longtable}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ------------------------------
# Main
# ------------------------------
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
    ap.add_argument("--max_lag", type=int, default=64, help="Max lag for autocorrelation plot")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    bits = read_bits(args.inp, args.fmt)
    n = int(bits.size)
    overall_bias = float(bits.mean()) if n else float('nan')

    bias_info = plot_bias_over_time(bits, os.path.join(args.outdir, "bias_over_time.png"), args.window, args.bias_tol)
    cusum_info = plot_cusum(bits, os.path.join(args.outdir, "drift_cusum.png"), args.cusum_k, args.cusum_h)
    ac_info = plot_autocorr(bits, os.path.join(args.outdir, "autocorr.png"), max_lag=args.max_lag)
    rl_info = plot_run_lengths(bits, os.path.join(args.outdir, "run_lengths.png"), max_show=64)

    # Beacon preview (first 10) and totals
    beacon_rows_preview, beacon_total = mini_beacon(bits, args.beacon_bits, args.context, epochs_out=10)

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

    # LaTeX artifacts
    write_latex_table_metrics(os.path.join(args.outdir, "table_qrng_metrics.tex"), {
        "num_bits": n,
        "overall_bias": overall_bias,
        "window": args.window,
        "bias_tol": args.bias_tol,
        "frac_within_tol": summary["frac_within_tol"],
        "max_abs_dev": summary["max_abs_dev"],
        "cusum_k": args.cusum_k,
        "cusum_h": args.cusum_h,
        "gp_max": summary["gp_max"],
        "gn_min": summary["gn_min"],
        "alarms": summary["alarms"],
        "ac1": summary["autocorr_lag1"],
        "ac2": summary["autocorr_lag2"],
    })

    write_latex_table_beacon(
        os.path.join(args.outdir, "table_beacon_epochs.tex"),
        beacon_rows_preview,
        args.beacon_bits,
        beacon_total
    )

    # Full appendix table with ALL epochs (requires \usepackage{longtable})
    write_latex_table_beacon_full(
        os.path.join(args.outdir, "table_beacon_epochs_full.tex"),
        bits,
        args.beacon_bits,
        args.context
    )

    print("=== Paper-Ready QRNG Pipeline ===")
    print(f"Bits: {n:,} | Overall bias p(1)={overall_bias:.6f}")
    print(f"Windows within ±{args.bias_tol:.4f}: {100.0*summary['frac_within_tol']:.2f}% | Max |p-0.5|={summary['max_abs_dev']:.6f}")
    print(f"CUSUM: k={args.cusum_k:.4f}, h={args.cusum_h:.4f} | gp_max={summary['gp_max']:.4f}, gn_min={summary['gn_min']:.4f}, alarms={summary['alarms']}")
    print(f"Beacon: bits/epoch={args.beacon_bits} | total epochs={beacon_total} (first 10 summarized)")
    print(f"Artifacts written to: {args.outdir}")
    if beacon_total > 0:
        print("Appendix table created: table_beacon_epochs_full.tex (use with \\usepackage{longtable})")

if __name__ == "__main__":
    main()
