import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

bits = "01100101"
pairs = [bits[i:i+2] for i in range(0, len(bits)-len(bits)%2, 2)]
rules = {"10":"→0","01":"→1","00":"→×","11":"→×"}
mapped = [rules[p] for p in pairs]
output = "".join([m[-1] for m in mapped if m[-1] in ("0","1")])  # extract unbiased bits
output = output[:3]  # keep 101

plt.style.use('grayscale')
fig, ax = plt.subplots(figsize=(10,2.8), dpi=300)

x0, w, h = 0.5, 0.6, 0.6

# Input row
for i, b in enumerate(bits):
    ax.add_patch(Rectangle((x0+i*w, 2.0), w, h, fill=False))
    ax.text(x0+i*w+w/2, 2.0+h/2, b, ha='center', va='center')
ax.text(x0-0.4, 2.0+h/2, "Input", ha='right', va='center')

# Pairs row
for i, p in enumerate(pairs):
    xx = x0 + (2*i)*w
    ax.add_patch(Rectangle((xx, 1.2), 2*w, h, fill=False))
    ax.text(xx+w, 1.2+h/2, p, ha='center', va='center')
    ax.add_patch(FancyArrowPatch((xx+w, 2.0), (xx+w, 1.2+h), arrowstyle='->', mutation_scale=10))
ax.text(x0-0.4, 1.2+h/2, "Pairs", ha='right', va='center')

# Rule row
for i, p in enumerate(pairs):
    xx = x0 + (2*i)*w
    ax.add_patch(Rectangle((xx, 0.5), 2*w, h, fill=False))
    ax.text(xx+w, 0.5+h/2, f"{p} {rules[p]}", ha='center', va='center')
    ax.add_patch(FancyArrowPatch((xx+w, 1.2), (xx+w, 0.5+h), arrowstyle='->', mutation_scale=10))
ax.text(x0-0.4, 0.5+h/2, "Rule", ha='right', va='center')

# Output row
y_out = -0.2
out_bits = list(output)
for i, m in enumerate(out_bits):
    xx = x0 + i*w
    ax.add_patch(Rectangle((xx, y_out), w, h, fill=False))
    ax.text(xx+w/2, y_out+h/2, m, ha='center', va='center')
ax.text(x0-0.4, y_out+h/2, "Output", ha='right', va='center')
ax.text(x0 + len(out_bits)*w + 1.0, y_out+h/2, f"Result: {output}", va='center', fontsize=12)

ax.set_xlim(0, x0 + max(len(bits), len(pairs)*2)*w + 2)
ax.set_ylim(-0.3, 3.0)
ax.axis('off')

# Save with transparent background
save_path = "/mnt/data/von_neumann_101_transparent.png"
fig.savefig(save_path, transparent=True, bbox_inches='tight')
save_path
