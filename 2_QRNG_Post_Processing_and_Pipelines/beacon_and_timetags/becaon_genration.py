#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Make publicly verifiable beacon epochs from a 0/1 bitstring file.

Definition (explicit for reproducibility):
- We remove all whitespace from data.txt and require the remaining characters
  to be only '0' or '1'. (Any other character -> error.)
- Epoch e (0-based) uses bits [start:end) where:
    start = e * epoch_bits,  end = start + epoch_bits
- Epoch output (epoch_hash_hex) = SHA-256( ASCII("0/1" epoch bits) ), hex-encoded
  (i.e., we hash the ASCII text of the bits, not bytes parsed *from* the bits).
- Optional hash-chain (chain_hex) = SHA-256( epoch_hash_bytes || prev_chain_bytes ),
  with prev_chain_bytes = 32 zero bytes for epoch 0.

Outputs a tab-delimited table: Epoch, Start, End, Bits, SHA256_hex[, Chain_hex]
"""

import argparse
import hashlib
import pathlib
import sys
from typing import Iterable, Tuple, Optional

def load_bitstring(path: str) -> str:
    p = pathlib.Path(path)
    s = p.read_text(encoding="utf-8", errors="strict")
    # Keep only 0/1; allow arbitrary whitespace in the file.
    cleaned = "".join(ch for ch in s if ch in "01")
    # Verify no non-binary, non-whitespace chars:
    stripped = "".join(ch for ch in s if not ch.isspace())
    if any(ch not in "01" for ch in stripped):
        bad = {ch for ch in stripped if ch not in "01"}
        raise ValueError(f"Found non-binary characters in input: {sorted(bad)}")
    if len(cleaned) == 0:
        raise ValueError("No bits found after removing whitespace.")
    return cleaned

def iter_epochs(bits: str,
                epoch_bits: int,
                start_epoch: int = 0,
                max_epochs: Optional[int] = None,
                chain: bool = False
               ) -> Iterable[Tuple[int,int,int,int,str,Optional[str]]]:
    """
    Yields tuples:
      (epoch, start, end, bits_len, epoch_hash_hex, chain_hex_or_None)
    """
    # Compute how many full epochs we have starting at start_epoch
    total_full = (len(bits) - start_epoch*epoch_bits) // epoch_bits
    if total_full < 0:
        total_full = 0
    if max_epochs is not None:
        total_full = min(total_full, max_epochs)

    prev_chain = b"\x00" * 32  # genesis for chain
    for i in range(total_full):
        e = start_epoch + i
        start = e * epoch_bits
        end = start + epoch_bits
        chunk = bits[start:end]  # ASCII '0'/'1' text

        # Epoch hash over ASCII epoch bits:
        epoch_hash_bytes = hashlib.sha256(chunk.encode("ascii")).digest()
        epoch_hash_hex = epoch_hash_bytes.hex()

        if chain:
            chain_bytes = hashlib.sha256(epoch_hash_bytes + prev_chain).digest()
            chain_hex = chain_bytes.hex()
            prev_chain = chain_bytes
        else:
            chain_hex = None

        yield (e, start, end, len(chunk), epoch_hash_hex, chain_hex)

def write_table(rows: Iterable[Tuple[int,int,int,int,str,Optional[str]]],
                out_path: str,
                include_chain: bool) -> int:
    out = pathlib.Path(out_path)
    with out.open("w", encoding="utf-8") as f:
        if include_chain:
            f.write("Epoch\tStart\tEnd\tBits\tSHA256_hex\tChain_hex\n")
        else:
            f.write("Epoch\tStart\tEnd\tBits\tSHA256_hex\n")
        n = 0
        for e, s, t, blen, h, ch in rows:
            if include_chain:
                f.write(f"{e}\t{s}\t{t}\t{blen}\t{h}\t{ch}\n")
            else:
                f.write(f"{e}\t{s}\t{t}\t{blen}\t{h}\n")
            n += 1
    return n

def main():
    ap = argparse.ArgumentParser(description="Build verifiable beacon epochs from a 0/1 bitstring.")
    ap.add_argument("-i", "--in", dest="infile", required=True, help="Path to data.txt containing 0/1 with arbitrary whitespace.")
    ap.add_argument("-o", "--out", dest="outfile", default="table_beacon_epochs.txt",
                    help="Output table path (tab-delimited). Default: table_beacon_epochs.txt")
    ap.add_argument("--epoch-bits", type=int, default=2048, help="Bits per epoch. Default: 2048")
    ap.add_argument("--start-epoch", type=int, default=0, help="0-based start epoch index. Default: 0")
    ap.add_argument("--max-epochs", type=int, default=None, help="Limit number of epochs emitted. Default: all available")
    ap.add_argument("--chain", action="store_true", help="Also compute hash-chain column Chain_hex.")
    args = ap.parse_args()

    try:
        bits = load_bitstring(args.infile)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    rows = list(iter_epochs(bits,
                            epoch_bits=args.epoch_bits,
                            start_epoch=args.start_epoch,
                            max_epochs=args.max_epochs,
                            chain=args.chain))
    if not rows:
        print("[WARN] No full epochs found with given parameters.", file=sys.stderr)

    count = write_table(rows, args.outfile, include_chain=args.chain)
    print(f"[OK] Wrote {count} epoch(s) to: {args.outfile}")
    print(f"[INFO] Source bits: {len(bits)}; Epoch size: {args.epoch_bits}; Start epoch: {args.start_epoch}")

if __name__ == "__main__":
    main()
