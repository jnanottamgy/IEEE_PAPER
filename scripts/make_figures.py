"""Build every data figure in the paper from the project's own result files.

Inputs : data/results/raw/*.json  (written by train.py of the RA-PatchTST project)
         data/ETTh1.csv           (public ETTh1 file used by the project)
Outputs: paper/figures/*.pdf (for LaTeX) and *.png (for the DOCX), plus
         paper/figures/stats.txt with every derived number quoted in the text.

Nothing here is typed in by hand: all values come from the JSON results.
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "results" / "raw"
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Categorical palette (validated: lightness band, chroma, CVD and normal-vision separation pass).
COL = {"A0": "#2a78d6", "A1": "#eb6834", "A2": "#1baf7a", "A3": "#eda100", "A4": "#e87ba4"}
MARK = {"A0": "o", "A1": "s", "A2": "^", "A3": "D", "A4": "v"}
HATCH = {"A0": "", "A1": "////", "A2": "....", "A3": "\\\\\\\\", "A4": "xx"}
NAME = {"A0": "A0 PatchTST", "A1": "A1 +CAT", "A2": "A2 +CAT+shift head",
        "A3": "A3 +CAT+gate", "A4": "A4 RA-PatchTST"}
INK, MUTED, GRID = "#1f1f1e", "#5f5e58", "#d9d8d3"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "pdf.fonttype": 42,
    "mathtext.fontset": "stix", "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.5, "axes.axisbelow": True, "legend.frameon": False, "lines.linewidth": 1.4,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})

GROUPS = {
    "clean": ["clean"],
    "missing\n(point)": [f"missing_{p}" for p in (1, 5, 10, 15)],
    "missing\n(16-stretch)": [f"missingpatch_{p}" for p in (1, 5, 10, 15)],
    "noise": [f"noise_{p}" for p in (1, 5, 10, 15)],
    "anomaly": [f"anomaly_{p}" for p in (1, 5, 10, 15)],
    "shift": [f"shift_{k}" for k in (1, 3, 5, 10)],
    "mixed": ["mixed"],
}
CORR = [s for g, v in GROUPS.items() if g != "clean" for s in v]
VARS = ["A0", "A1", "A2", "A3", "A4"]


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


def load():
    runs = defaultdict(dict)
    for f in sorted(RAW.glob("*_H96_s*.json")):
        r = json.loads(f.read_text())
        runs[r["variant"]][r["seed"]] = r
    return runs


runs = load()
SEEDS = sorted(runs["A0"])


def per_seed(v, names, k=0):
    return np.array([np.mean([runs[v][s]["test"][n][k] for n in names]) for s in SEEDS])


stats = []
P = stats.append

# ----------------------------------------------------------------- derived numbers
for v in VARS:
    r0 = runs[v][SEEDS[0]]
    P(f"{v}: params={r0['params']} gate={r0['gate_params']} epochs={[runs[v][s]['epochs_run'] for s in SEEDS]} "
      f"best_sel={[runs[v][s]['best_epoch_sel'] for s in SEEDS]} best_clean={[runs[v][s]['best_epoch_clean'] for s in SEEDS]} "
      f"sec/ep={np.mean([runs[v][s]['sec_per_epoch'] for s in SEEDS]):.1f} infer={np.mean([runs[v][s]['infer_sec_test'] for s in SEEDS]):.2f}")
    cv = np.array([runs[v][s]["test_cleanval_ckpt_clean"] for s in SEEDS])
    P(f"   clean-val ckpt clean MSE/MAE mean {cv[:,0].mean():.4f}/{cv[:,1].mean():.4f} per-seed {cv[:,0].round(4)}")
    for g, names in GROUPS.items():
        m, a = per_seed(v, names, 0), per_seed(v, names, 1)
        P(f"   {g.replace(chr(10),' '):22s} MSE {m.mean():.4f}±{m.std(ddof=1):.4f} MAE {a.mean():.4f}  seeds {m.round(4)}")
    m, a = per_seed(v, CORR, 0), per_seed(v, CORR, 1)
    P(f"   avg21                  MSE {m.mean():.4f}±{m.std(ddof=1):.4f} MAE {a.mean():.4f}  seeds {m.round(4)}")
for v in VARS:
    clean = per_seed(v, ["clean"]).mean()
    worst = max(CORR, key=lambda n: per_seed(v, [n]).mean())
    P(f"{v} relative degradation: worst {worst} {per_seed(v,[worst]).mean():.4f} (+{100*(per_seed(v,[worst]).mean()/clean-1):.1f}% over own clean); "
      f"shift group +{100*(per_seed(v,GROUPS['shift']).mean()/clean-1):.1f}%; anomaly group +{100*(per_seed(v,GROUPS['anomaly']).mean()/clean-1):.1f}%; avg21 +{100*(per_seed(v,CORR).mean()/clean-1):.1f}%")
# per-setting A4 vs A0 wins
wins = sum(per_seed("A4", [n]).mean() < per_seed("A0", [n]).mean() for n in CORR)
wins1 = sum(per_seed("A4", [n]).mean() < per_seed("A1", [n]).mean() for n in CORR)
P(f"A4 better than A0 on {wins}/21 corrupted settings; better than A1 on {wins1}/21")
for n in ["shift_10", "anomaly_15", "mixed", "missing_15", "missingpatch_15"]:
    a0, a1, a4 = (per_seed(v, [n]).mean() for v in ("A0", "A1", "A4"))
    P(f"{n}: A0 {a0:.4f} A1 {a1:.4f} A4 {a4:.4f}  A4 vs A0 {100*(a4/a0-1):+.1f}%  A4 vs A1 {100*(a4/a1-1):+.1f}%")
# gate
for v in ("A3", "A4"):
    for st in runs[v][SEEDS[0]]["gate"]:
        wc = [runs[v][s]["gate"][st]["w_corrupted"] for s in SEEDS]
        wk = [runs[v][s]["gate"][st]["w_clean"] for s in SEEDS]
        fr = [runs[v][s]["gate"][st]["frac_patches_corrupted"] for s in SEEDS]
        wcm = None if wc[0] is None else np.mean(wc)
        P(f"gate {v} {st:15s} frac {np.mean(fr):.3f} w_corr {wcm if wcm is None else round(wcm,4)} w_clean {np.mean(wk):.4f}")
(OUT / "stats.txt").write_text("\n".join(stats) + "\n")

# ----------------------------------------------------------------- Fig: dataset overview
df = pd.read_csv(ROOT / "data" / "ETTh1.csv", parse_dates=["date"])
TR, VA, TE = 8640, 11520, 14400
fig, axes = plt.subplots(2, 1, figsize=(7.0, 2.6), sharex=True)
for ax, col, lab in zip(axes, ["OT", "HUFL"], ["Oil temperature OT", "High useful load HUFL"]):
    ax.plot(df["date"], df[col], color=COL["A0"], lw=0.35)
    for a, b, c, t in [(0, TR, "#ffffff", "train (12 mo)"), (TR, VA, "#eeeeea", "validation (4 mo)"),
                       (VA, TE, "#dcdbd5", "test (4 mo)"), (TE, len(df) - 1, "#ffffff", "unused")]:
        ax.axvspan(df["date"].iloc[a], df["date"].iloc[b], color=c, zorder=0, lw=0)
        if ax is axes[0]:
            ax.text(df["date"].iloc[(a + b) // 2], 1.02, t, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=7, color=MUTED)
    for x in (TR, VA, TE):
        ax.axvline(df["date"].iloc[x], color=MUTED, lw=0.6, ls="--")
    ax.set_ylabel(lab, fontsize=7)
    ax.grid(axis="x", visible=False)
save(fig, "fig_dataset")


# ----------------------------------------------------------------- Fig: corruption examples
# NumPy port of corrupt.py (same distributions and parameters), used only for illustration.
def np_missing_point(x, p, rng):
    m = rng.random(x.shape) < p
    return np.where(m, 0.0, x), m


def np_missing_patch(x, p, rng, stretch=16):
    L = len(x)
    start = (rng.random(L) < p / stretch).astype(int)
    c = np.cumsum(start)
    c_prev = np.concatenate([np.zeros(stretch, int), c[:-stretch]])
    m = (c - c_prev) > 0
    return np.where(m, 0.0, x), m


def np_noise(x, p, rng):
    m = rng.random(x.shape) < p
    return x + m * rng.standard_normal(x.shape), m


def np_anomaly(x, p, rng):
    m = rng.random(x.shape) < p
    mag = 3.0 + 2.0 * rng.random(x.shape)
    sign = np.where(rng.random(x.shape) < 0.5, -1.0, 1.0)
    return x + m * mag * sign, m


def np_shift(x, k, rng):
    L = len(x)
    seg = L // 10
    m = np.zeros(L, bool)
    x = x.copy()
    for _ in range(k):
        s = rng.integers(0, L - seg + 1)
        off, scl = -2 + 4 * rng.random(), 0.5 + 1.5 * rng.random()
        x[s:s + seg] = x[s:s + seg] * scl + off
        m[s:s + seg] = True
    return x, m


def np_mixed(x, rng):
    x, m1 = np_shift(x, 1, rng)
    x, m2 = np_noise(x, 0.05, rng)
    x, m3 = np_anomaly(x, 0.05, rng)
    x, m4 = np_missing_point(x, 0.05, rng)
    return x, m1 | m2 | m3 | m4


data = df.iloc[:, 1:].to_numpy(np.float64)
mu, sd = data[:TR].mean(0), data[:TR].std(0)
sc = (data - mu) / sd
x0 = sc[VA + 400: VA + 400 + 336, 6]  # one test-period input window, OT channel, scaled units
cases = [("missing (point), 10%", lambda x, r: np_missing_point(x, 0.10, r)),
         ("missing (16-stretch), 10%", lambda x, r: np_missing_patch(x, 0.10, r)),
         ("noise, 10%", lambda x, r: np_noise(x, 0.10, r)),
         ("anomaly, 5%", lambda x, r: np_anomaly(x, 0.05, r)),
         ("shift, $k=3$ segments", lambda x, r: np_shift(x, 3, r)),
         ("mixed", lambda x, r: np_mixed(x, r))]
fig, axes = plt.subplots(2, 3, figsize=(7.0, 3.0), sharex=True, sharey=True)
for i, (ax, (t, fn)) in enumerate(zip(axes.ravel(), cases)):
    xc, m = fn(x0, np.random.default_rng(11 + i))
    ax.plot(x0, color="#a8a79f", lw=0.9, label="clean input")
    ax.plot(xc, color=COL["A0"], lw=0.8, label="corrupted input")
    idx = np.where(m)[0]
    ax.scatter(idx, xc[idx], s=4, color=COL["A1"], zorder=3, lw=0, label="altered values")
    ax.set_title(t, color=INK)
    if i == 0:
        ax.legend(loc="lower left", fontsize=6, handlelength=1.2)
fig.subplots_adjust(hspace=0.42)
for ax in axes[1]:
    ax.set_xlabel("input step (hours)")
for ax in axes[:, 0]:
    ax.set_ylabel("OT (scaled)")
save(fig, "fig_corruptions")

# ----------------------------------------------------------------- Fig: MSE by group
glabels = list(GROUPS) + ["avg of 21\ncorruptions"]
fig, ax = plt.subplots(figsize=(7.0, 2.5))
w = 0.16
xs = np.arange(len(glabels))
for j, v in enumerate(VARS):
    vals = [per_seed(v, n) for n in GROUPS.values()] + [per_seed(v, CORR)]
    mean = [a.mean() for a in vals]
    err = [a.std(ddof=1) for a in vals]
    ax.bar(xs + (j - 2) * w, mean, w * 0.88, color=COL[v], hatch=HATCH[v], edgecolor="white", lw=0.3,
           yerr=err, error_kw=dict(lw=0.6, capsize=1.2, ecolor=INK), label=NAME[v])
ax.set_xticks(xs)
ax.set_xticklabels(glabels)
ax.set_ylim(0.36, 0.53)
ax.set_ylabel("test MSE (lower is better)")
ax.grid(axis="x", visible=False)
ax.legend(ncol=5, loc="upper left", bbox_to_anchor=(0, 1.13), columnspacing=1.0, handlelength=1.6)
save(fig, "fig_mse_groups")

# ----------------------------------------------------------------- Fig: severity curves
fam = [("missing (point)", "missing", (1, 5, 10, 15), "% of points"),
       ("missing (16-stretch)", "missingpatch", (1, 5, 10, 15), "% of points"),
       ("noise", "noise", (1, 5, 10, 15), "% of points"),
       ("anomaly", "anomaly", (1, 5, 10, 15), "% of points"),
       ("shift", "shift", (1, 3, 5, 10), "segments $k$")]
fig, axes = plt.subplots(1, 5, figsize=(7.0, 1.9))
for ax, (t, key, lv, xl) in zip(axes, fam):
    for v in ("A0", "A1", "A4"):
        arr = np.array([per_seed(v, [f"{key}_{l}"]) for l in lv])
        ax.plot(lv, arr.mean(1), color=COL[v], marker=MARK[v], ms=3.2, lw=1.2, label=NAME[v])
        ax.fill_between(lv, arr.min(1), arr.max(1), color=COL[v], alpha=0.18, lw=0)
    ax.set_title(t, color=INK)
    ax.set_xlabel(xl)
    ax.set_xticks(lv)
axes[0].set_ylabel("test MSE")
axes[0].legend(loc="upper left", fontsize=6, handlelength=1.4)
fig.tight_layout(w_pad=0.6)
save(fig, "fig_severity")

# ----------------------------------------------------------------- Fig: ablation (% vs A0)
cats = [("avg of 21", CORR), ("shift", GROUPS["shift"]), ("anomaly", GROUPS["anomaly"]),
        ("mixed", GROUPS["mixed"]), ("clean", GROUPS["clean"]), ("missing (pt)", GROUPS["missing\n(point)"])]
fig, ax = plt.subplots(figsize=(3.45, 2.3))
h = 0.19
ys = np.arange(len(cats))[::-1]
for j, v in enumerate(["A1", "A2", "A3", "A4"]):
    d = [100 * (per_seed(v, n).mean() / per_seed("A0", n).mean() - 1) for _, n in cats]
    ax.barh(ys + (1.5 - j) * h, d, h * 0.88, color=COL[v], hatch=HATCH[v], edgecolor="white", lw=0.3, label=NAME[v])
ax.axvline(0, color=INK, lw=0.7)
ax.set_yticks(ys)
ax.set_yticklabels([c for c, _ in cats])
ax.set_xlabel(r"change in test MSE vs. A0 (%)  $\leftarrow$ better")
ax.grid(axis="y", visible=False)
ax.legend(loc="lower left", fontsize=6, handlelength=1.4)
save(fig, "fig_ablation")

# ----------------------------------------------------------------- Fig: learning curves
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.0), sharex=True)
for ax, key, t in zip(axes, ["val_clean", "val_mixed"], ["clean validation", "mixed-corruption validation"]):
    for v in ("A0", "A1", "A4"):
        for k, s in enumerate(SEEDS):
            hst = runs[v][s]["history"]
            ax.plot([e["epoch"] for e in hst], [e[key] for e in hst], color=COL[v], ls="-" if k == 0 else "--",
                    lw=1.0, marker=MARK[v], ms=2.2, markevery=4, label=f"{NAME[v]}, seed {s}")
    ax.set_title(t, color=INK)
    ax.set_xlabel("epoch")
    ax.set_xticks([1, 5, 10, 15, 20])
axes[0].set_ylabel("validation MSE")
axes[0].set_ylim(0.66, 0.80)
axes[1].set_ylim(0.71, 0.86)
axes[1].legend(ncol=1, fontsize=5.6, loc="upper right", handlelength=2.2)
save(fig, "fig_learning")

# ----------------------------------------------------------------- Fig: gate weights
sets = ["clean", "missing_5", "missingpatch_5", "noise_5", "anomaly_5", "shift_3", "mixed"]
lab = ["clean", "miss.\n5%", "stretch\n5%", "noise\n5%", "anom.\n5%", "shift\nk=3", "mixed"]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.0), sharey=True)
for ax, v in zip(axes, ("A3", "A4")):
    xs = np.arange(len(sets))
    wc = [np.nan if runs[v][SEEDS[0]]["gate"][st]["w_corrupted"] is None else
          np.mean([runs[v][s]["gate"][st]["w_corrupted"] for s in SEEDS]) for st in sets]
    wk = [np.mean([runs[v][s]["gate"][st]["w_clean"] for s in SEEDS]) for st in sets]
    ax.bar(xs - 0.19, wk, 0.36, color="#9ec5f4", edgecolor="white", lw=0.3, label="clean patches")
    ax.bar(xs + 0.19, wc, 0.36, color=COL["A1"], hatch="////", edgecolor="white", lw=0.3, label="corrupted patches")
    ax.set_xticks(xs)
    ax.set_xticklabels(lab, fontsize=6)
    ax.set_ylim(0.90, 0.97)
    ax.set_title(NAME[v], color=INK)
    ax.grid(axis="x", visible=False)
axes[0].set_ylabel("mean gate weight $w$")
axes[0].legend(loc="upper left", fontsize=6, ncol=2)
save(fig, "fig_gate_weights")

# ----------------------------------------------------------------- Fig: relative degradation heatmap
fig, ax = plt.subplots(figsize=(7.0, 1.75))
M = np.array([[100 * (per_seed(v, [n]).mean() / per_seed(v, ["clean"]).mean() - 1) for n in CORR] for v in VARS])
im = ax.imshow(M, aspect="auto", cmap="Blues", vmin=0, vmax=90)
ax.set_yticks(range(len(VARS)))
ax.set_yticklabels([NAME[v] for v in VARS])
short = [n.replace("missingpatch_", "mp").replace("missing_", "m").replace("noise_", "n").replace("anomaly_", "a")
         .replace("shift_", "s").replace("mixed", "mix") for n in CORR]
ax.set_xticks(range(len(CORR)))
ax.set_xticklabels(short, fontsize=6)
ax.grid(False)
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        if M[i, j] >= 10:
            ax.text(j, i, f"{M[i,j]:.0f}", ha="center", va="center", fontsize=5.2,
                    color="white" if M[i, j] > 45 else INK)
cb = fig.colorbar(im, ax=ax, pad=0.01, fraction=0.03)
cb.set_label("% MSE above own clean", fontsize=6)
cb.ax.tick_params(labelsize=6)
save(fig, "fig_heatmap")

print("\n".join(stats))
