# save as make_clean_bits.py
import pathlib, sys
s = pathlib.Path("data.txt").read_text(encoding="utf-8", errors="strict")
clean = "".join(ch for ch in s if ch in "01")
pathlib.Path("clean_bits.txt").write_text(clean, encoding="utf-8")
print(f"[OK] Wrote clean_bits.txt with {len(clean)} bits.")
