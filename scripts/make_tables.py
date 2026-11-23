"""Emit the LaTeX results tables of the paper from data/results/raw/*.json.

Output: paper/tables/*.tex (each a bare tabular body, wrapped by table floats in main.tex).
Conventions follow make_report.py of the project: mean over seeds, sample std (ddof=1),
percentage change computed from the seed-mean values.
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "results" / "raw"
OUT = ROOT / "paper" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

runs = defaultdict(dict)
for f in sorted(RAW.glob("*_H96_s*.json")):
    r = json.loads(f.read_text())
    runs[r["variant"]][r["seed"]] = r
SEEDS = sorted(runs["A0"])
VARS = ["A0", "A1", "A2", "A3", "A4"]
GROUPS = [
    ("Clean", ["clean"]),
    ("Missing (point)", [f"missing_{p}" for p in (1, 5, 10, 15)]),
    ("Missing (16-stretch)", [f"missingpatch_{p}" for p in (1, 5, 10, 15)]),
    ("Noise", [f"noise_{p}" for p in (1, 5, 10, 15)]),
    ("Anomaly", [f"anomaly_{p}" for p in (1, 5, 10, 15)]),
    ("Shift", [f"shift_{k}" for k in (1, 3, 5, 10)]),
    ("Mixed", ["mixed"]),
]
CORR = [s for g, v in GROUPS if g != "Clean" for s in v]
GROUPS_AVG = GROUPS + [("Avg.\\ of 21 corruptions", CORR)]
MINUS = "$-$"


def ps(v, names, k=0):
    return np.array([np.mean([runs[v][s]["test"][n][k] for n in names]) for s in SEEDS])


def pct(x):
    s = f"{x:+.1f}\\%"
    return s.replace("-", MINUS)


def w(name, rows):
    (OUT / f"{name}.tex").write_text("\n".join(rows) + "\n")


# 1. MSE and MAE by group, mean +- std, best per row in bold (among A0..A4)
for k, metric in ((0, "mse"), (1, "mae")):
    rows = []
    for g, names in GROUPS_AVG:
        vals = {v: ps(v, names, k) for v in VARS}
        best = min(VARS, key=lambda v: round(vals[v].mean(), 3))
        cells = []
        for v in VARS:
            c = f"{vals[v].mean():.3f}\\,$\\pm$\\,{vals[v].std(ddof=1):.3f}"
            cells.append(f"\\textbf{{{c}}}" if round(vals[v].mean(), 3) == round(vals[best].mean(), 3) else c)
        if g.startswith("Avg"):
            rows.append("\\midrule")
        rows.append(f"{g} & " + " & ".join(cells) + " \\\\")
    w(f"tab_groups_{metric}", rows)

# 2. percentage change vs A0 and vs A1
for ref, others, name in (("A0", ["A1", "A2", "A3", "A4"], "tab_delta_a0"), ("A1", ["A2", "A3", "A4"], "tab_delta_a1")):
    rows = []
    for g, names in GROUPS_AVG:
        base = ps(ref, names).mean()
        cells = [pct(100 * (ps(v, names).mean() / base - 1)) for v in others]
        if g.startswith("Avg"):
            rows.append("\\midrule")
        rows.append(f"{g} & " + " & ".join(cells) + " \\\\")
    w(name, rows)

# 3. paired per-seed comparison against A1 (avg of 21 corruptions)
rows = []
for v in ["A2", "A3", "A4"]:
    d = ps(v, CORR) - ps("A1", CORR)
    better = int((d < 0).sum())
    per = ", ".join(f"{x:+.4f}".replace("-", MINUS) for x in d)
    rows.append(f"{v} & {len(d)} & {d.mean():+.4f} & {better}/{len(d)} & {per} \\\\".replace("+-", "-").replace(" -0", f" {MINUS}0"))
w("tab_paired", rows)

# 4. cost
rows = []
base_p = runs["A0"][SEEDS[0]]["params"]
for v in VARS:
    r = runs[v][SEEDS[0]]
    sec = np.mean([runs[v][s]["sec_per_epoch"] for s in SEEDS])
    inf = np.mean([runs[v][s]["infer_sec_test"] for s in SEEDS])
    rows.append(f"{v} & {r['params']:,} & {r['params']-base_p:+,} & {r['gate_params']} & {sec:.1f} & {inf:.2f} & "
                f"{'/'.join(str(runs[v][s]['best_epoch_sel']) for s in SEEDS)} \\\\".replace("+0", "0"))
w("tab_cost", rows)

# 5. gate behaviour (A3 and A4, mean over seeds)
labels = {"clean": "Clean", "missing_5": "Missing (point) 5\\%", "missingpatch_5": "Missing (16-stretch) 5\\%",
          "noise_5": "Noise 5\\%", "anomaly_5": "Anomaly 5\\%", "shift_3": "Shift $k{=}3$", "mixed": "Mixed"}
rows = []
for st, lab in labels.items():
    cells = []
    for v in ("A3", "A4"):
        g = [runs[v][s]["gate"][st] for s in SEEDS]
        wc = None if g[0]["w_corrupted"] is None else np.mean([x["w_corrupted"] for x in g])
        wk = np.mean([x["w_clean"] for x in g])
        cells += ["--" if wc is None else f"{wc:.3f}", f"{wk:.3f}", "--" if wc is None else f"{(wc-wk):+.3f}".replace("-", MINUS)]
    fr = np.mean([runs["A4"][s]["gate"][st]["frac_patches_corrupted"] for s in SEEDS])
    rows.append(f"{lab} & {fr:.2f} & " + " & ".join(cells) + " \\\\")
w("tab_gate", rows)

# 6. full per-setting table (MSE, all variants; MAE for A0 and A4)
names_disp = {"clean": "Clean"}
for p in (1, 5, 10, 15):
    names_disp[f"missing_{p}"] = f"Missing (point) {p}\\%"
for p in (1, 5, 10, 15):
    names_disp[f"missingpatch_{p}"] = f"Missing (16-str.) {p}\\%"
for p in (1, 5, 10, 15):
    names_disp[f"noise_{p}"] = f"Noise {p}\\%"
for p in (1, 5, 10, 15):
    names_disp[f"anomaly_{p}"] = f"Anomaly {p}\\%"
for k in (1, 3, 5, 10):
    names_disp[f"shift_{k}"] = f"Shift $k{{=}}{k}$"
names_disp["mixed"] = "Mixed"
rows = []
for n, lab in names_disp.items():
    m = {v: ps(v, [n]).mean() for v in VARS}
    best = min(m.values())
    cells = [f"\\textbf{{{m[v]:.4f}}}" if m[v] == best else f"{m[v]:.4f}" for v in VARS]
    cells += [f"{ps('A0', [n], 1).mean():.4f}", f"{ps('A4', [n], 1).mean():.4f}",
              pct(100 * (m['A4'] / m['A0'] - 1))]
    rows.append(f"{lab} & " + " & ".join(cells) + " \\\\")
w("tab_full", rows)

# 7. headline A0 vs A4 with per-seed values
rows = []
for v, lab in (("A0", "PatchTST (A0)"), ("A4", "RA-PatchTST (A4)")):
    for g, names in (("Clean", ["clean"]), ("Avg.\\ of 21 corruptions", CORR), ("Shift (4 levels)", GROUPS[5][1]),
                     ("Anomaly (4 levels)", GROUPS[4][1]), ("Mixed", ["mixed"])):
        m, a = ps(v, names), ps(v, names, 1)
        rows.append(f"{lab} & {g} & {m.mean():.3f} & {a.mean():.3f} & {', '.join(f'{x:.4f}' for x in m)} \\\\")
    if v == "A0":
        rows.append("\\midrule")
w("tab_headline", rows)

# 8. clean reproduction (clean-val checkpoint)
rows = []
for v in VARS:
    cv = np.array([runs[v][s]["test_cleanval_ckpt_clean"] for s in SEEDS])
    rows.append(f"{v} & {cv[:,0].mean():.4f} & {cv[:,1].mean():.4f} & {pct(100*(cv[:,0].mean()/0.375-1))} & {pct(100*(cv[:,1].mean()/0.399-1))} \\\\")
w("tab_repro", rows)
print("tables written:", sorted(p.name for p in OUT.glob("*.tex")))
