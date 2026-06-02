import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, FancyArrowPatch
from matplotlib import patheffects

fig, ax = plt.subplots(figsize=(8, 5.5))

x_left, x_right = 0.5, 10.5
well_left, well_right = 3.0, 7.5
Lz_y = 0.7
Ec_barrier = 8.8
Ec_well = 7.0
Ev_well = 2.6
Ev_barrier = 1.0

E1c, E2c, E3c = Ec_well + 0.6, Ec_well + 1.1, Ec_well + 1.55
E1hh, E2hh, E3hh = Ev_well - 0.5, Ev_well - 1.0, Ev_well - 1.45

# Band edges as before
ax.plot([x_left, well_left], [Ec_barrier, Ec_barrier], lw=2)
ax.plot([well_left, well_right], [Ec_well, Ec_well], lw=2)
ax.plot([well_right, x_right], [Ec_barrier, Ec_barrier], lw=2)
ax.plot([well_left, well_left], [Ec_well, Ec_barrier], lw=2)
ax.plot([well_right, well_right], [Ec_well, Ec_barrier], lw=2)

ax.plot([x_left, well_left], [Ev_barrier, Ev_barrier], lw=2)
ax.plot([well_left, well_right], [Ev_well, Ev_well], lw=2)
ax.plot([well_right, x_right], [Ev_barrier, Ev_barrier], lw=2)
ax.plot([well_left, well_left], [Ev_barrier, Ev_well], lw=2)
ax.plot([well_right, well_right], [Ev_barrier, Ev_well], lw=2)

ax.add_patch(Rectangle((well_left, Ev_barrier), well_right-well_left, Ec_barrier-Ev_barrier,
                       fill=False, lw=1, ls="--"))

subband_pad = 0.65
for y, label in [(E1c, r"$E_{1c}$"), (E2c, r"$E_{2c}$"), (E3c, r"$E_{3c}$")]:
    ax.plot([well_left+subband_pad, well_right-subband_pad], [y, y], lw=1.6)
    ax.text(well_right-subband_pad+0.18, y, label, va='center', ha='left', fontsize=11)

for y, label in [(E1hh, r"$E_{1hh}$"), (E2hh, r"$E_{2hh}$"), (E3hh, r"$E_{3hh}$")]:
    ax.plot([well_left+subband_pad, well_right-subband_pad], [y, y], lw=1.6, ls=(0, (2,2)))
    ax.text(well_right-subband_pad+0.18, y, label, va='center', ha='left', fontsize=11)

# Conduction band label ABOVE the line
ax.text(well_left, Ec_barrier+0.30, "CONDUCTION BAND", va='bottom', ha='left', fontsize=12)

# Valence band label below as before
ax.text(well_left, Ev_barrier-0.70, "VALENCE BAND", va='top', ha='left', fontsize=12)

# Eg double-headed arrow between well edges, label in middle
eg_x = well_left - 0.5  # left of the well
arr_eg = FancyArrowPatch((eg_x, Ec_well), (eg_x, Ev_well),
                         arrowstyle="<->", mutation_scale=18, lw=2, color="purple", zorder=10)
ax.add_patch(arr_eg)
ax.text(eg_x-0.05, (Ec_well+Ev_well)/2, r"$E_g$", color="purple", va='center', ha='right', fontsize=13)

# Arrow from Ec1 to HH1 within well (vertical or diagonal)
arr_e1c_e1hh = FancyArrowPatch((well_right-0.2, E1c), (well_right-0.2, E1hh),
                               arrowstyle='->', mutation_scale=18, lw=2, color="red", zorder=10)
ax.add_patch(arr_e1c_e1hh)
ax.text(well_right-0.1, (E1c+E1hh)/2, r"", color="red", va='center', ha='left', fontsize=12)

# Lz marker as before (below line)
lz_pad = 0.12
lz_y_below = Lz_y - lz_pad
ax.plot([well_left, well_right], [Lz_y, Lz_y], lw=1.2)
ax.add_patch(FancyArrow(well_left, Lz_y, (well_right-well_left), 0, width=0.0,
                        head_width=0.18, head_length=0.18, length_includes_head=True))
ax.add_patch(FancyArrow(well_right, Lz_y, -(well_right-well_left), 0, width=0.0,
                        head_width=0.18, head_length=0.18, length_includes_head=True))
ax.text((well_left+well_right)/2, lz_y_below-0.04, r"$L_z$", ha='center', va='top', fontsize=12)

ax.set_xlim(x_left, x_right)
ax.set_ylim(0.0, 10.0)
ax.set_xlabel("Position")
ax.set_ylabel("Energy")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Quantum Well Band Diagram with Subbands and Offsets")

for artist in ax.texts:
    artist.set_path_effects([patheffects.withStroke(linewidth=2, foreground="white")])

plt.tight_layout()
plt.show()
