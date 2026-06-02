# helper_epoch_hex.py
import argparse, hashlib, sys
from paper_ready_qrng_pipeline import read_bits, bits_to_bytes

def u64be(x: int) -> bytes:
    return x.to_bytes(8, "big")

def main():
    ap = argparse.ArgumentParser(description="Print payload_hex and expected SHA-256 for a given epoch")
    ap.add_argument("--in", dest="inp", required=True, help="QRNG file path")
    ap.add_argument("--format", dest="fmt", default="auto", choices=["auto","bin","hex","raw"], help="Input format")
    ap.add_argument("--beacon_bits", type=int, required=True, help="Bits per epoch")
    ap.add_argument("--context", default="SPDC-QRNG Beacon", help="Context string")
    ap.add_argument("--epoch", type=int, required=True, help="Epoch index (0-based)")
    args = ap.parse_args()

    bits = read_bits(args.inp, args.fmt)
    need = (args.epoch + 1) * args.beacon_bits
    if bits.size < need:
        print(f"Error: need at least {(args.epoch+1)*args.beacon_bits} bits, but file has {bits.size}.", file=sys.stderr)
        sys.exit(1)

    # init = SHA256("QRB-1" || u64be(beacon_bits) || context)
    init = hashlib.sha256(b"QRB-1" + u64be(args.beacon_bits) + args.context.encode()).digest()

    # compute prev for this epoch (epoch 0 uses init)
    prev = init
    for i in range(args.epoch):
        ci = bits[i*args.beacon_bits:(i+1)*args.beacon_bits]
        prev = hashlib.sha256(prev + bits_to_bytes(ci) + u64be(i) + args.context.encode()).digest()

    # chunk for the epoch
    start = args.epoch * args.beacon_bits
    chunk = bits[start:start + args.beacon_bits]

    # payload = prev || chunk_bytes || u64be(epoch) || context
    chunk_bytes = bits_to_bytes(chunk)
    payload = prev + chunk_bytes + u64be(args.epoch) + args.context.encode()

    payload_hex = payload.hex()
    expected_sha256 = hashlib.sha256(payload).hexdigest()

    print("payload_hex:")
    print(payload_hex)
    print("\nexpected_sha256:")
    print(expected_sha256)

if __name__ == "__main__":
    main()
