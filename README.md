# RA-PatchTST: IEEE manuscript

IEEE-format research paper for the RA-PatchTST project (24CS52, Ramaiah Institute of Technology):
*RA-PatchTST: A Reliability-Aware Extension of PatchTST for Multivariate Time-Series Forecasting Under Corrupted Inputs.*

## Deliverables (`output/`)

| File | Contents |
|---|---|
| `RA-PatchTST_IEEE_paper.pdf` | Main manuscript, IEEEtran journal class, single column, 12 pt (28 pages) |
| `RA-PatchTST_IEEE_paper_two-column.pdf` | Same source in the two-column IEEE camera-ready layout (19 pages) |
| `RA-PatchTST_IEEE_paper.docx` | Editable Word version; equations are native Word equations, numbering matches the PDF |
| `RA-PatchTST_LaTeX_source.zip` | Complete LaTeX source (main.tex, sections, tables, figures, TikZ sources, refs.bib) |
| `RA-PatchTST_figures.zip` | All figures as vector PDF and 300-dpi PNG |

## Layout

```
paper/main.tex           manuscript root (IEEEtran)
paper/sections/*.tex     one file per section
paper/tables/*.tex       table bodies, generated from the result files
paper/figures/           figures (PDF for LaTeX, PNG for Word)
paper/tikz/              TikZ sources of the diagrams
paper/refs.bib           verified references (see paper/refs_verification.md)
data/results/            per-run JSON results of the project (A0-A4, seeds 2021/2022)
data/ETTh1.csv           dataset used by the project
scripts/make_figures.py  builds every chart from data/results
scripts/make_tables.py   builds every results table from data/results
scripts/make_docx.py     converts the compiled LaTeX into the Word version
```

## Rebuild

Requires TeX Live (IEEEtran, pgf/TikZ, algorithmicx), Python 3 with numpy, pandas,
matplotlib and python-docx, and pandoc.

```bash
python3 scripts/make_figures.py
python3 scripts/make_tables.py
(cd paper/tikz && for f in fig_*.tex; do pdflatex "$f"; done)   # then copy PDFs to paper/figures
paper/build.sh                 # main_review.pdf and main_camera.pdf
python3 scripts/make_docx.py   # output/RA-PatchTST_IEEE_paper.docx
```

Every number in the results section comes from `data/results/raw/*.json`; nothing is typed by hand.
