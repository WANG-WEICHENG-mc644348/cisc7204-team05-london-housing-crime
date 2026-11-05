"""
CISC7204 Team Project - London crime and house prices
Rebuild the borough-year panel, run every comparison, write results.

    python build_analysis.py

Inputs (read-only):
    <Proposal03>\\data\\housing_in_london_monthly.csv
    <Proposal03>\\data\\housing_in_london_yearly.csv
    _external\\MPS Borough Level Crime (Historical).csv

Outputs:
    out/results.md         every number, grouped by comparison
    out/results.json       the same numbers, machine readable
    out/panel.csv          borough-year panel
    out/cross_section.csv  the 32-borough cross-section
    out/changes.csv        year-pair changes
    out/offence_types.csv  per-offence correlations
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "data"
MPS = SRC / "MPS_Borough_Level_Crime_Historical.csv"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

INNER = {
    "camden", "islington", "hammersmith and fulham", "hackney", "haringey",
    "southwark", "lambeth", "tower hamlets", "wandsworth", "westminster",
    "kensington and chelsea",
}

L, R = [], {}


def say(s=""):
    L.append(s)


def h(level, text):
    say()
    say("#" * level + " " + text)
    say()


def spearman(x, y):
    x = pd.Series(np.asarray(x, dtype=float))
    y = pd.Series(np.asarray(y, dtype=float))
    return float(x.rank(method="average").corr(y.rank(method="average")))


def perm_p(x, y, n=20000, seed=0):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    obs = abs(spearman(x, y))
    rng = np.random.default_rng(seed)
    hits = sum(abs(spearman(x, rng.permutation(y))) >= obs - 1e-12 for _ in range(n))
    return (hits + 1) / (n + 1)


def partial_spearman(x, y, z):
    rx = pd.Series(x).rank(method="average").to_numpy()
    ry = pd.Series(y).rank(method="average").to_numpy()
    rz = pd.Series(z).rank(method="average").to_numpy()

    def resid(v):
        A = np.column_stack([np.ones_like(rz), rz])
        beta, *_ = np.linalg.lstsq(A, v, rcond=None)
        return v - A @ beta

    return float(np.corrcoef(resid(rx), resid(ry))[0, 1])


def boot_ci(x, y, groups=None, n=4000, seed=1):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    vals = []
    if groups is None:
        idx = np.arange(len(x))
        for _ in range(n):
            s = rng.choice(idx, size=len(idx), replace=True)
            if len(np.unique(x[s])) > 5:
                vals.append(spearman(x[s], y[s]))
    else:
        g = np.asarray(groups)
        uniq = np.unique(g)
        pos = {k: np.where(g == k)[0] for k in uniq}
        for _ in range(n):
            pick = rng.choice(uniq, size=len(uniq), replace=True)
            sel = np.concatenate([pos[k] for k in pick])
            vals.append(spearman(x[sel], y[sel]))
    v = np.array(vals)
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


# ---------------------------------------------------------------- 1. panel
h(2, "1. Borough-year panel")

monthly = pd.read_csv(SRC / "housing_in_london_monthly.csv")
yearly = pd.read_csv(SRC / "housing_in_london_yearly.csv")
monthly["date"] = pd.to_datetime(monthly["date"])
yearly["date"] = pd.to_datetime(yearly["date"])
monthly["year"] = monthly["date"].dt.year
yearly["year"] = yearly["date"].dt.year

m = monthly[monthly["borough_flag"] == 1].copy()
agg = m.groupby(["area", "year"], as_index=False).agg(
    avg_price=("average_price", "mean"),
    crimes=("no_of_crimes", "sum"),
    crime_months=("no_of_crimes", "count"),
    price_months=("average_price", "count"),
    sold=("houses_sold", "mean"),
)

y = yearly[yearly["borough_flag"] == 1][
    ["area", "year", "population_size", "median_salary", "number_of_jobs", "no_of_houses"]
].copy()
for c in ["population_size", "median_salary", "number_of_jobs", "no_of_houses"]:
    y[c] = pd.to_numeric(y[c], errors="coerce")

panel = agg.merge(y, on=["area", "year"], how="left")
panel["crime_per_1000"] = panel["crimes"] / panel["population_size"] * 1000

raw = panel.copy()
panel = panel[
    (panel["crime_months"] >= 10)
    & panel["avg_price"].notna()
    & panel["population_size"].notna()
].copy()
panel = panel.sort_values(["area", "year"]).reset_index(drop=True)

say(f"- borough-years kept: **{len(panel)}**")
say(f"- years: **{int(panel['year'].min())}–{int(panel['year'].max())}**")
cov = panel.groupby("year")["area"].nunique()
say("- boroughs per year: " + ", ".join(f"{int(k)}:{v}" for k, v in cov.items()))
say()
say("Why the panel stops at 2018 — crime is populated through 2019, "
    "but `population_size` and `number_of_jobs` are blank for 2019:")
say()
say("| year | crime months | population present | jobs present |")
say("|---|---|---|---|")
chk = raw[raw["crimes"].notna()].groupby("year").agg(
    months=("crime_months", "max"),
    pop=("population_size", "count"),
    jobs=("number_of_jobs", "count"),
)
for yy in [2016, 2017, 2018, 2019]:
    r = chk.loc[yy]
    say(f"| {yy} | {int(r['months'])} | {int(r['pop'])} of 33 | {int(r['jobs'])} of 33 |")

panel.to_csv(OUT / "panel.csv", index=False, encoding="utf-8-sig")
R["panel_rows"] = int(len(panel))
R["panel_years"] = [int(panel["year"].min()), int(panel["year"].max())]

# ------------------------------------------------------- 2. cross-section
h(2, "2. Cross-section: 2016-2018 borough means")

win = panel[panel["year"].between(2016, 2018)]
cs = win.groupby("area", as_index=False).agg(
    price=("avg_price", "mean"),
    rate=("crime_per_1000", "mean"),
    counts=("crimes", "mean"),
    pop=("population_size", "mean"),
    jobs=("number_of_jobs", "mean"),
    salary=("median_salary", "mean"),
    sold=("sold", "mean"),
    n_years=("year", "nunique"),
)
cs = cs[cs["n_years"] == 3].dropna(subset=["price", "rate", "salary", "jobs"]).reset_index(drop=True)
cs["rate_day"] = cs["counts"] / (cs["pop"] + cs["jobs"]) * 1000
cs["jobs_ratio"] = cs["jobs"] / cs["pop"]
cs["inner"] = cs["area"].isin(INNER)
cs.to_csv(OUT / "cross_section.csv", index=False, encoding="utf-8-sig")

say(f"n = **{len(cs)}** boroughs")
say()
say("| pair | Spearman rho | permutation p |")
say("|---|---|---|")
pairs = [
    ("crime rate / residents vs price", "rate", "price"),
    ("crime count vs price", "counts", "price"),
    ("median earnings vs price", "salary", "price"),
    ("crime rate vs median earnings", "rate", "salary"),
    ("jobs per resident vs price", "jobs_ratio", "price"),
    ("jobs per resident vs crime rate", "jobs_ratio", "rate"),
]
for label, a, b in pairs:
    rho = spearman(cs[a], cs[b])
    say(f"| {label} | **{rho:.3f}** | {perm_p(cs[a], cs[b], n=5000, seed=7):.4f} |")
    R[label] = round(rho, 4)
say()
say(f"Baseline check: rho = **{spearman(cs['rate'], cs['price']):.3f}** "
    "(the proposal reports 0.47, so the panel reproduces).")

# ------------------------------------------------------ 3. earnings control
h(2, "3. Partialling out earnings")

lo, hi = boot_ci(cs["rate"], cs["price"])
lo2, hi2 = boot_ci(cs["rate_day"], cs["price"])
say("| comparison | rho | 95% bootstrap CI |")
say("|---|---|---|")
say(f"| crime rate vs price (raw) | **{spearman(cs['rate'], cs['price']):.3f}** | [{lo:.3f}, {hi:.3f}] |")
say(f"| crime rate vs price, earnings partialled out | **{partial_spearman(cs['rate'], cs['price'], cs['salary']):.3f}** | — |")
say(f"| crime rate / (residents + jobs) vs price | **{spearman(cs['rate_day'], cs['price']):.3f}** | [{lo2:.3f}, {hi2:.3f}] |")
say(f"| same, earnings partialled out | **{partial_spearman(cs['rate_day'], cs['price'], cs['salary']):.3f}** | — |")
R["partial_earnings"] = round(partial_spearman(cs["rate"], cs["price"], cs["salary"]), 4)
R["rate_day_vs_price"] = round(spearman(cs["rate_day"], cs["price"]), 4)
R["rate_day_partial"] = round(partial_spearman(cs["rate_day"], cs["price"], cs["salary"]), 4)
R["ci_raw"] = [round(lo, 4), round(hi, 4)]

# --------------------------------------------------------- 4. denominator
h(2, "4. Denominator sensitivity: residents + k x jobs")

ks = [round(0.1 * i, 1) for i in range(0, 21)]
curve = []
say("| k | rho |")
say("|---|---|")
for k in ks:
    rho = spearman(cs["counts"] / (cs["pop"] + k * cs["jobs"]) * 1000, cs["price"])
    curve.append((k, round(rho, 4)))
    say(f"| {k:.1f} | {rho:.3f} |")
zero = None
for i in range(len(curve) - 1):
    (k0, r0), (k1, r1) = curve[i], curve[i + 1]
    if r0 * r1 < 0:
        zero = round(k0 + (0 - r0) * (k1 - k0) / (r1 - r0), 2)
        break
say()
say(f"- zero crossing at **k ≈ {zero}**" if zero else "- no zero crossing on this grid")
say(f"- rho at k = 0: {curve[0][1]:.3f}; at k = 1: "
    f"{[r for k, r in curve if k == 1.0][0]:.3f}; at k = 2: {curve[-1][1]:.3f}")
R["k_curve"] = curve
R["zero_crossing"] = zero

# ------------------------------------------------------------ 5. inner/out
h(2, "5. Inner and outer London")

for name, sub in (("inner", cs[cs["inner"]]), ("outer", cs[~cs["inner"]])):
    rho = spearman(sub["rate"], sub["price"])
    say(f"- {name} London, n = {len(sub)}: rho = **{rho:.3f}** "
        f"(permutation p = {perm_p(sub['rate'], sub['price'], n=5000, seed=11):.4f})")
    R[name] = round(rho, 4)
    R[name + "_n"] = int(len(sub))
say(f"- pooled, n = 32: rho = **{spearman(cs['rate'], cs['price']):.3f}**")

# ----------------------------------------------------- 6. within-borough
h(2, "6. Within-borough year-to-year changes")

pp = panel.sort_values(["area", "year"]).copy()
grp = pp.groupby("area")
pp["prev_year"] = grp["year"].shift(1)
pp["d_rate"] = pp["crime_per_1000"] - grp["crime_per_1000"].shift(1)
pp["d_price"] = pp["avg_price"] - grp["avg_price"].shift(1)
pos_rate = pp["crime_per_1000"].where(pp["crime_per_1000"] > 0)
pp["d_rate_ln"] = np.log(pos_rate) - np.log(pos_rate.groupby(pp["area"]).shift(1))
pos_pr = pp["avg_price"].where(pp["avg_price"] > 0)
pp["d_price_ln"] = np.log(pos_pr) - np.log(pos_pr.groupby(pp["area"]).shift(1))
chg = pp[(pp["year"] - pp["prev_year"]) == 1].dropna(subset=["d_rate", "d_price"]).copy()
chg.to_csv(OUT / "changes.csv", index=False, encoding="utf-8-sig")

rho = spearman(chg["d_rate"], chg["d_price"])
lo, hi = boot_ci(chg["d_rate"], chg["d_price"], groups=chg["area"])
say(f"- year-pairs: **{len(chg)}** across **{chg['area'].nunique()}** boroughs")
say(f"- change in crime rate vs change in price: rho = **{rho:.3f}**, "
    f"cluster-bootstrap 95% CI [{lo:.3f}, {hi:.3f}]")
nc = chg[chg["area"] != "city of london"]
say(f"- excluding City of London: rho = **{spearman(nc['d_rate'], nc['d_price']):.3f}** "
    f"(n = {len(nc)} pairs, {nc['area'].nunique()} boroughs)")
say(f"- log-change version: rho = {spearman(chg['d_rate_ln'], chg['d_price_ln']):.3f}")
R["within_rho"] = round(rho, 4)
R["within_pairs"] = int(len(chg))
R["within_ci"] = [round(lo, 4), round(hi, 4)]

say()
say("Lead and lag:")
lag = pp.sort_values(["area", "year"]).copy()
lag["d_price_next"] = lag.groupby("area")["d_price"].shift(-1)
lag["d_rate_next"] = lag.groupby("area")["d_rate"].shift(-1)
a1 = lag.dropna(subset=["d_rate", "d_price_next"])
a2 = lag.dropna(subset=["d_price", "d_rate_next"])
say(f"- d crime(t) vs d price(t+1): rho = **{spearman(a1['d_rate'], a1['d_price_next']):.3f}** (n = {len(a1)})")
say(f"- d price(t) vs d crime(t+1): rho = **{spearman(a2['d_price'], a2['d_rate_next']):.3f}** (n = {len(a2)})")
R["lag_crime_to_price"] = round(spearman(a1["d_rate"], a1["d_price_next"]), 4)
R["lag_price_to_crime"] = round(spearman(a2["d_price"], a2["d_rate_next"]), 4)

# ---------------------------------------------------------------- 7. LOO
h(2, "7. Leave-one-out")

loo = sorted(
    [(a, spearman(cs.loc[cs["area"] != a, "rate"], cs.loc[cs["area"] != a, "price"]))
     for a in cs["area"]],
    key=lambda t: t[1],
)
say(f"- range: **{loo[0][1]:.3f} – {loo[-1][1]:.3f}**")
say(f"- lowest when dropping `{loo[0][0]}` ({loo[0][1]:.3f}); "
    f"highest when dropping `{loo[-1][0]}` ({loo[-1][1]:.3f})")
say(f"- dropping Westminster: {dict(loo)['westminster']:.3f}")
R["loo_range"] = [round(loo[0][1], 4), round(loo[-1][1], 4)]

# ------------------------------------------------------- 8. offence types
h(2, "8. Offence types (MPS borough file, 2016-2018)")

if MPS.exists():
    mps = pd.read_csv(MPS, encoding="utf-8-sig")
    mps.columns = [str(c).strip() for c in mps.columns]
    month_cols = [c for c in mps.columns if c.isdigit() and len(c) == 6]
    want = [c for c in month_cols if c[:4] in ("2016", "2017", "2018")]
    say(f"- file rows = {len(mps)}; months used = {len(want)} ({want[0]} to {want[-1]})")

    tot = mps[want].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    mps = mps.assign(_total=tot, area=mps["BoroughName"].str.strip().str.lower())

    types = (mps.groupby(["MajorText", "area"], as_index=False)["_total"].sum()
             .rename(columns={"MajorText": "offence"}))

    pop3 = panel[panel["year"].between(2016, 2018)].groupby("area")["population_size"].sum()
    job3 = panel[panel["year"].between(2016, 2018)].groupby("area")["number_of_jobs"].sum()
    pri = dict(zip(cs["area"], cs["price"]))
    sal = dict(zip(cs["area"], cs["salary"]))

    say()
    say("| offence | n | rho vs price | earnings-partialled | rho vs earnings | "
        "rho vs price, jobs-adjusted rate |")
    say("|---|---|---|---|---|---|")
    rows_out = []
    for off, g in types.groupby("offence"):
        s = g.set_index("area")["_total"]
        areas = [a for a in s.index if a in pri and a in pop3.index and pop3[a] > 0]
        if len(areas) < 20 or s.loc[areas].sum() == 0:
            say(f"| {off.title()} | {len(areas)} | (skipped) | | | |")
            continue
        cnt = s.loc[areas].to_numpy(dtype=float)
        pv = np.array([pri[a] for a in areas])
        sv = np.array([sal[a] for a in areas])
        den = np.array([pop3[a] for a in areas])
        den2 = den + np.array([job3[a] for a in areas])
        r1 = spearman(cnt / den, pv)
        r2 = partial_spearman(cnt / den, pv, sv)
        r3 = spearman(cnt / den, sv)
        r4 = spearman(cnt / den2, pv)
        say(f"| {off.title()} | {len(areas)} | **{r1:.3f}** | {r2:.3f} | {r3:.3f} | {r4:.3f} |")
        rows_out.append({"offence": off, "n": len(areas), "rho_price": round(r1, 4),
                         "rho_price_earnings": round(r2, 4), "rho_earnings": round(r3, 4),
                         "rho_price_jobsadj": round(r4, 4)})
    pd.DataFrame(rows_out).to_csv(OUT / "offence_types.csv", index=False, encoding="utf-8-sig")
    R["offence_types"] = rows_out

    unmatched = sorted(set(types["area"]) - set(cs["area"]))
    if unmatched:
        say()
        say(f"- MPS areas with no match in the panel: {', '.join(unmatched)}")
else:
    say("MPS file not found, section skipped.")

# ---------------------------------------------------------- 9. data notes
h(2, "9. Notes for the write-up")

say("- Crime is populated 2001–2019, but `population_size` and `number_of_jobs` "
    "stop at 2018 in the annual file, so the crime **rate** panel is 2001–2018.")
say(f"- {int(panel[panel['year'] <= 2009]['area'].nunique())} areas carry crime data "
    f"before 2010 (City of London included); "
    f"{int(panel[panel['year'] >= 2010]['area'].nunique())} from 2010 on.")
say(f"- `number_of_jobs` complete for {panel['number_of_jobs'].notna().mean() * 100:.0f}% "
    "of panel borough-years.")
w = cs.loc[cs["area"] == "westminster", "jobs_ratio"].iloc[0]
say(f"- Westminster has {w:.2f} jobs per resident; the median borough has "
    f"{cs['jobs_ratio'].median():.2f}.")
say(f"- Median earnings missing in a few borough-years "
    f"({int(cs['salary'].isna().sum())} of 32 in the cross-section after dropna).")

(OUT / "results.md").write_text("\n".join(L), encoding="utf-8")
(OUT / "results.json").write_text(json.dumps(R, indent=1, default=float), encoding="utf-8")
print("done ->", OUT)
