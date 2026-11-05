"""
Figures for the CISC7204 team project presentation.

    python make_figures.py

Reads out/*.csv + out/results.json, writes figures/*.png at 200 dpi.
Every label is in English so the figures can be dropped straight into the
slide deck or the written report.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "out"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# ---------------------------------------------------------------- style
INK = "#1c1c1c"
MUTED = "#6b6b6b"
GRID = "#d8d8d8"
BLUE = "#2b5797"
TERRA = "#c65f2e"
GOLD = "#c99a2e"
GREEN = "#3f7d5a"
PALE = "#eef2f8"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.titlesize": 13,
    "axes.titleweight": "regular",
    "axes.labelsize": 10.5,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": GRID,
    "grid.linestyle": ":",
    "grid.linewidth": 0.7,
    "legend.frameon": False,
    "figure.dpi": 200,
})

res = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
cs = pd.read_csv(OUT / "cross_section.csv")
chg = pd.read_csv(OUT / "changes.csv")
off = pd.read_csv(OUT / "offence_types.csv")


def tidy(ax, grid_axis="both"):
    ax.grid(True, axis=grid_axis, alpha=0.85)
    ax.set_axisbelow(True)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.9)
        ax.spines[s].set_color(MUTED)


def save(fig, name):
    fig.savefig(FIG / name, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def ols(x, y):
    b, a = np.polyfit(x, y, 1)
    xs = np.linspace(min(x), max(x), 50)
    return xs, a + b * xs


def pretty(a):
    a = a.replace(" and ", " & ").replace("upon thames", "upon Thames")
    return " ".join(w.capitalize() if w not in ("&", "and", "of", "the", "upon") else w
                    for w in a.split())


# ================================================================ fig 1
fig, ax = plt.subplots(figsize=(9.0, 5.6))
sc = ax.scatter(cs["rate"], cs["price"] / 1000, c=cs["salary"] / 1000,
                cmap="YlOrRd", s=70, edgecolor="#333333", linewidth=0.45, zorder=3)
xs, ys = ols(cs["rate"], cs["price"] / 1000)
ax.plot(xs, ys, color=INK, lw=1.5, zorder=2, alpha=0.85)

for name, dx, dy, ha in [("westminster", -12, 12, "right"),
                         ("kensington and chelsea", 10, 4, "left"),
                         ("bexley", 8, -14, "left"),
                         ("harrow", 0, -17, "center"),
                         ("camden", 10, 2, "left")]:
    r = cs[cs["area"] == name].iloc[0]
    ax.annotate(pretty(name), xy=(r["rate"], r["price"] / 1000),
                xytext=(dx, dy), textcoords="offset points", fontsize=8.5,
                color=INK, ha=ha)

cb = fig.colorbar(sc, ax=ax, pad=0.015)
cb.set_label("Median earnings (£ thousands)", color=MUTED, fontsize=9.5)
cb.outline.set_visible(False)

ax.set_xlabel("Recorded crimes per 1,000 residents, 2016–2018 mean")
ax.set_ylabel("Average house price (£ thousands)")
ax.set_xlim(45, 252)
ax.set_ylim(230, 1440)
ax.set_title("Crime and house prices move together — the opposite of the claim",
             loc="left", pad=12)
ax.text(0.985, 0.05, f"Spearman ρ = {res['crime rate / residents vs price']:.2f}   n = 32",
        transform=ax.transAxes, ha="right", fontsize=10, color=INK)
tidy(ax)
save(fig, "fig1_baseline.png")

# ================================================================ fig 2
labels = ["Crime rate\nvs price", "Median earnings\nvs price",
          "Crime rate\nvs earnings", "Crime count\nvs price"]
keys = ["crime rate / residents vs price", "median earnings vs price",
        "crime rate vs median earnings", "crime count vs price"]
vals = [res[k] for k in keys]
pvals = ["p = 0.008", "p = 0.004", "p = 0.0004", "p = 0.17"]
colors = [TERRA, BLUE, BLUE, MUTED]

fig, ax = plt.subplots(figsize=(8.4, 4.4))
ypos = np.arange(len(labels))[::-1]
ax.barh(ypos, vals, height=0.55, color=colors, edgecolor="none")
ax.axvline(0, color=INK, lw=1.0)
for yy, v, p in zip(ypos, vals, pvals):
    ax.text(v + 0.012, yy, f"{v:.2f}   {p}", va="center", fontsize=9.5, color=INK)
ax.set_yticks(ypos)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlim(0, 0.82)
ax.set_xlabel("Spearman ρ with average house price, 2016–2018 means (n = 32)")
ax.set_title("Earnings sit on both sides of the scatter, so the terracotta bar is tangled",
             loc="left", pad=12)
ax.legend(handles=[Line2D([], [], marker="s", ls="", color=TERRA, label="the claim's own comparison"),
                   Line2D([], [], marker="s", ls="", color=BLUE, label="possible confounders"),
                   Line2D([], [], marker="s", ls="", color=MUTED, label="weak measure")],
          loc="lower right", fontsize=8.8)
tidy(ax, "x")
save(fig, "fig2_bars.png")

# ================================================================ fig 3
cols = ["price", "rate", "salary", "jobs_ratio"]
names = ["Average price", "Crime rate\n/ residents", "Median earnings", "Jobs per\nresident"]
M = pd.DataFrame(index=names, columns=names, dtype=float)
for i, a in enumerate(cols):
    for j, b in enumerate(cols):
        M.iloc[i, j] = cs[a].rank().corr(cs[b].rank())

fig, ax = plt.subplots(figsize=(6.4, 5.2))
im = ax.imshow(M.values.astype(float), cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(names, fontsize=9)
ax.set_yticklabels(names, fontsize=9)
for i in range(4):
    for j in range(4):
        v = M.values[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=11,
                color="white" if abs(v) > 0.55 else INK)
ax.set_title("Everything correlates with everything — that is the problem",
             loc="left", pad=12)
for s in ax.spines.values():
    s.set_visible(False)
fig.colorbar(im, ax=ax, shrink=0.78, pad=0.02).outline.set_visible(False)
save(fig, "fig3_heatmap.png")

# ================================================================ fig 4
curve = res["k_curve"]
ks = np.array([c[0] for c in curve])
rhos = np.array([c[1] for c in curve])

fig, ax = plt.subplots(figsize=(9.0, 5.0))
ax.axhspan(ymin=0, ymax=0.62, color=PALE, zorder=0)
ax.plot(ks, rhos, color=BLUE, lw=2.2, zorder=3)
ax.axhline(0, color=INK, lw=1.0, zorder=2)
ax.axvline(res["zero_crossing"], color=TERRA, ls="--", lw=1.2, zorder=2)
ax.scatter([0, 1.0], [rhos[0], rhos[10]], s=90, color=TERRA, zorder=4,
           edgecolor="white", linewidth=1.2)

ax.annotate("only residents\n(the proposal's rate)", xy=(0, rhos[0]), xytext=(0.22, 0.53),
            fontsize=9.2, color=INK,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.annotate("residents + jobs\n(daytime exposure)", xy=(1.0, rhos[10]), xytext=(1.18, 0.34),
            fontsize=9.2, color=INK,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.text(res["zero_crossing"] + 0.03, -0.24, f"sign flips\nat k ≈ {res['zero_crossing']}",
        fontsize=9, color=TERRA)

ax.set_xlabel("k  —  weight on jobs in the denominator   (denominator = residents + k × jobs)")
ax.set_ylabel("Spearman ρ, crime rate vs average price")
ax.set_title("Change what you divide by, and the answer changes with it", loc="left", pad=12)
ax.set_xlim(-0.05, 2.05)
ax.set_ylim(-0.28, 0.58)
tidy(ax)
save(fig, "fig4_denominator_curve.png")

# ================================================================ fig 5
fig, ax = plt.subplots(figsize=(9.0, 5.4))
for mask, color, marker, lab, key in [
    (cs["inner"], BLUE, "o", "Inner London (11)", "inner"),
    (~cs["inner"], GOLD, "s", "Outer London (21)", "outer"),
]:
    sub = cs[mask]
    ax.scatter(sub["rate"], sub["price"] / 1000, s=68, color=color, marker=marker,
               edgecolor="white", linewidth=0.9, zorder=3,
               label=f"{lab}   ρ = {res[key]:+.2f}")
    xs, ys = ols(sub["rate"], sub["price"] / 1000)
    ax.plot(xs, ys, color=color, lw=1.8, alpha=0.9, zorder=2)

for name, dx, dy in [("westminster", -14, 10), ("kensington and chelsea", 8, 4),
                     ("bexley", 6, -13), ("richmond upon thames", 6, 6)]:
    r = cs[cs["area"] == name].iloc[0]
    ax.annotate(pretty(name), xy=(r["rate"], r["price"] / 1000), xytext=(dx, dy),
                textcoords="offset points", fontsize=8.5, color=INK)

ax.set_xlabel("Recorded crimes per 1,000 residents, 2016–2018 mean")
ax.set_ylabel("Average house price (£ thousands)")
ax.set_title("Split the same 32 boroughs in two and the sign flips", loc="left", pad=12)
ax.text(0.985, 0.93, "pooled ρ = +0.47", transform=ax.transAxes, ha="right",
        fontsize=9.5, color=MUTED, style="italic")
ax.legend(loc="upper left", fontsize=9.5)
tidy(ax)
save(fig, "fig5_inner_outer.png")

# ================================================================ fig 6
fig, ax = plt.subplots(figsize=(8.6, 5.4))
ax.axhline(0, color=INK, lw=0.8, alpha=0.5, zorder=1)
ax.axvline(0, color=INK, lw=0.8, alpha=0.5, zorder=1)
ax.scatter(chg["d_rate"], chg["d_price"] / 1000, s=18, color=BLUE, alpha=0.45,
           edgecolor="none", zorder=3)
xs, ys = ols(chg["d_rate"], chg["d_price"] / 1000)
ax.plot(xs, ys, color=TERRA, lw=2.2, zorder=4)
ax.set_xlim(-90, 120)
ax.set_ylim(-160, 190)
ax.set_xlabel("Change in recorded crimes per 1,000 residents (year on year)")
ax.set_ylabel("Change in average price (£ thousands)")
ax.set_title("Inside a borough, a year of rising crime barely moves the price",
             loc="left", pad=12)
lo, hi = res["within_ci"]
ax.text(0.985, 0.06,
        f"Spearman ρ = {res['within_rho']:.2f}   95% CI [{lo:.2f}, {hi:.2f}]\n"
        f"{res['within_pairs']} year-pairs, 33 boroughs, 2002–2018",
        transform=ax.transAxes, ha="right", fontsize=9.5, color=INK)
tidy(ax)
save(fig, "fig6_within.png")

# ================================================================ fig 7
o = off.copy()
o["label"] = o["offence"].map(lambda s: s.title().replace(" And ", " & "))
o = o.sort_values("rho_price")

fig, ax = plt.subplots(figsize=(9.0, 5.6))
ypos = np.arange(len(o))
ax.hlines(ypos, 0, o["rho_price"], color=GRID, lw=1.2, zorder=1)
ax.scatter(o["rho_price"], ypos, s=78, color=BLUE, zorder=3, edgecolor="white",
           linewidth=0.9, label="per resident")
ax.scatter(o["rho_price_earnings"], ypos, s=62, marker="D", color=TERRA, zorder=3,
           edgecolor="white", linewidth=0.9, label="earnings partialled out")
ax.axvline(0, color=INK, lw=1.0)
ax.set_yticks(ypos)
ax.set_yticklabels(o["label"], fontsize=9.5)
ax.set_xlabel("Spearman ρ with average house price (offence rate per 1,000 residents)")
ax.set_title("Crime is not one thing: burglary tracks price, criminal damage does not",
             loc="left", pad=12)
ax.set_xlim(-0.45, 0.95)
ax.legend(loc="lower right", fontsize=9, bbox_to_anchor=(1.0, 0.06))
for yy, v in zip(ypos, o["rho_price"]):
    ax.text(v + (0.018 if v >= 0 else -0.018), yy, f"{v:.2f}", va="center",
            ha="left" if v >= 0 else "right", fontsize=8.5, color=MUTED)
tidy(ax, "x")
save(fig, "fig7_offence.png")

# ================================================================ fig 8
loo = sorted([(a, cs.loc[cs["area"] != a, "rate"].rank().corr(
    cs.loc[cs["area"] != a, "price"].rank())) for a in cs["area"]],
    key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(9.2, 4.2))
names_ = [pretty(a) for a, _ in loo]
vals_ = [v for _, v in loo]
ax.bar(range(len(vals_)), vals_, color=[TERRA if n in ("Camden", "Westminster") else BLUE
                                        for n, _ in [(pretty(a), v) for a, v in loo]],
       width=0.72)
ax.axhline(res["crime rate / residents vs price"], color=INK, ls="--", lw=1.0)
ax.text(0.4, res["crime rate / residents vs price"] + 0.002,
        "all 32 boroughs: 0.47", ha="left", va="bottom", fontsize=9, color=INK)
ax.set_xticks(range(len(vals_)))
ax.set_xticklabels(names_, rotation=62, ha="right", fontsize=7.6)
ax.set_ylim(0.36, 0.58)
ax.set_ylabel("ρ with that borough removed")
ax.set_title("No single borough carries the result", loc="left", pad=12)
tidy(ax, "y")
save(fig, "fig8_loo.png")

print("\nall figures written to", FIG)
