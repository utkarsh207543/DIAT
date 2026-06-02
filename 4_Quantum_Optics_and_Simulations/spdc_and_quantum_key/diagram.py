# Quantum well band diagram using Matplotlib (no seaborn, single plot, default colors)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, FancyArrowPatch
from matplotlib import patheffects

# Figure/axes
fig, ax = plt.subplots(figsize=(7, 5))

# --- Layout parameters (tweak here) ---
x_left, x_right = 0.5, 9.5           # full x-range
well_left, well_right = 3.0, 7.0     # quantum well boundaries
Lz_y = 0.7                           # y-position for Lz marker
Ec_barrier = 8.8                     # conduction band edge in barrier
Ec_well = 7.0                        # conduction band edge in well
Ev_well = 2.6                        # valence band edge in well (top of valence band)
Ev_barrier = 1.0                     # valence band edge in barrier
Delta_Ec = Ec_barrier - Ec_well
Delta_Ev = Ev_well - Ev_barrier
Eg = Ec_well - Ev_well               # bandgap reference inside well

# Subband energies (inside the well)
E1c, E2c, E3c = Ec_well + 0.6, Ec_well + 1.1, Ec_well + 1.55
E1hh, E2hh, E3hh = Ev_well - 0.5, Ev_well - 1.0, Ev_well - 1.45

# --- Draw barriers and well as band edges (piecewise constant) ---
# Conduction band edge
ax.plot([x_left, well_left], [Ec_barrier, Ec_barrier], lw=2)
ax.plot([well_left, well_right], [Ec_well, Ec_well], lw=2)
ax.plot([well_right, x_right], [Ec_barrier, Ec_barrier], lw=2)
# Steps showing band offset (ΔEc)
ax.plot([well_left, well_left], [Ec_well, Ec_barrier], lw=2)
ax.plot([well_right, well_right], [Ec_well, Ec_barrier], lw=2)

# Valence band edge
ax.plot([x_left, well_left], [Ev_barrier, Ev_barrier], lw=2)
ax.plot([well_left, well_right], [Ev_well, Ev_well], lw=2)
ax.plot([well_right, x_right], [Ev_barrier, Ev_barrier], lw=2)
# Steps showing band offset (ΔEv)
ax.plot([well_left, well_left], [Ev_barrier, Ev_well], lw=2)
ax.plot([well_right, well_right], [Ev_barrier, Ev_well], lw=2)

# Light gray fill to highlight the well region
ax.add_patch(Rectangle((well_left, Ev_barrier), well_right-well_left, Ec_barrier-Ev_barrier,
                       fill=False, lw=1, ls="--"))

# --- Subband levels inside the well ---
for y, label in [(E1c, r"$E_{1c}$"), (E2c, r"$E_{2c}$"), (E3c, r"$E_{3c}$")]:
    ax.plot([well_left+0.2, well_right-0.2], [y, y], lw=1.6)
    ax.text(well_left+0.25, y+0.12, label, va='bottom', ha='left', fontsize=10)

for y, label in [(E1hh, r"$E_{1hh}$"), (E2hh, r"$E_{2hh}$"), (E3hh, r"$E_{3hh}$")]:
    ax.plot([well_left+0.2, well_right-0.2], [y, y], lw=1.6, ls=(0, (2,2)))
    ax.text(well_left+0.25, y-0.12, label, va='top', ha='left', fontsize=10)

# --- Vertical interband transition and photon annotation ---
x_tr = (well_left + well_right) / 2.0
ax.plot([x_tr, x_tr], [E1hh, E1c], lw=1.4)
ax.text(x_tr+0.15, (E1hh+E1c)/2, r"$E_g$", rotation=90, va='center', ha='left', fontsize=10)

# Photon "emission" arrow (upward wiggle approximated by slanted arrow)
ph = FancyArrow(x_tr+1.0, (E1hh+E1c)/2, 0.0, E1c - (E1hh+E1c)/2 - 0.4,
                width=0.03, head_width=0.18, head_length=0.28, length_includes_head=True)
ax.add_patch(ph)
ax.text(x_tr+1.2, (E1hh+E1c)/2 + (E1c-E1hh)/2 - 0.4, r"$h\nu$", va='bottom', fontsize=11)

# Relation annotation: hν ~ Eg + E_{1c} + E_{1hh}
ax.text(x_tr-0.1, Ev_well + 0.2, r"$h\nu \sim E_g + E_{1c} + E_{1hh}$", fontsize=10)

# --- Band offsets ΔEc and ΔEv arrows ---
def bracket_arrow(x, y0, y1, label, side="right"):
    # Draw a vertical double-headed arrow with label
    dx = 0.35 if side=="right" else -0.35
    arr1 = FancyArrow(x, y0, 0, y1-y0, width=0.0, head_width=0.2, head_length=0.2, length_includes_head=True)
    ax.add_patch(arr1)
    ax.text(x+0.25* (1 if side=="right" else -1), (y0+y1)/2, label, rotation=90, va='center', ha='center', fontsize=10)

bracket_arrow(well_right+0.8, Ec_well, Ec_barrier, r"$\Delta E_c$", side="right")
bracket_arrow(well_right+0.8, Ev_barrier, Ev_well, r"$\Delta E_v$", side="right")

# --- Lz (well width) marker ---
ax.plot([well_left, well_right], [Lz_y, Lz_y], lw=1.2)
ax.add_patch(FancyArrow(well_left, Lz_y, (well_right-well_left), 0, width=0.0,
                        head_width=0.18, head_length=0.18, length_includes_head=True))
ax.add_patch(FancyArrow(well_right, Lz_y, -(well_right-well_left), 0, width=0.0,
                        head_width=0.18, head_length=0.18, length_includes_head=True))
ax.text((well_left+well_right)/2, Lz_y+0.18, r"$L_z$", ha='center', va='bottom', fontsize=11)

# --- Region labels ---
ax.text(1.1, (Ec_barrier+Ev_barrier)/2+0.4, "CONDUCTION\nBAND", va='center', ha='left', fontsize=10)
ax.text(1.1, (Ev_barrier+Ev_well)/2-0.6, "VALENCE\nBAND", va='center', ha='left', fontsize=10)

# --- Cleanup ---
ax.set_xlim(x_left, x_right)
ax.set_ylim(0.0, 10.0)
ax.set_xlabel("Position")
ax.set_ylabel("Energy")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Quantum Well Band Diagram with Subbands and Offsets")

# Add slight outline to important texts for clarity
for artist in ax.texts:
    artist.set_path_effects([patheffects.withStroke(linewidth=2, foreground="white")])

plt.tight_layout()
plt.show()
