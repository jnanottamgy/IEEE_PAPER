"""Convert the compiled LaTeX manuscript into an editable Word document.

Run after paper/build.sh (needs paper/main_review.aux and .bbl for numbering).
Steps: flatten sections and tables, resolve \\ref/\\eqref/\\cite from the .aux file so the
numbers match the PDF, convert IEEEtran-specific markup, swap PDF figures for PNGs, then run
pandoc (equations become native Word OMML) and post-format with python-docx.
"""
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "paper"
BUILD = ROOT / "output" / "docx_build"
BUILD.mkdir(parents=True, exist_ok=True)


def balanced(s, i):
    """Return index just past the brace group starting at s[i] == '{'."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    raise ValueError("unbalanced")


aux = (P / "main_review.aux").read_text()
labels = {}
for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{", aux):
    k = m.group(1)
    j = balanced(aux, m.end() - 1)
    v = aux[m.end():j - 1]
    v = v.replace("\\mbox  {", "").replace("\\mbox {", "").replace("}", "").replace("{", "")
    labels[k] = v
cites = dict(re.findall(r"\\bibcite\{([^}]+)\}\{(\d+)\}", aux))

# ------------------------------------------------------------------ flatten
main = (P / "main.tex").read_text()
body = main[main.index("\\begin{document}") + len("\\begin{document}"):main.index("\\end{document}")]


def inline_inputs(t):
    t = re.sub(r"\\input\{(sections/[^}]+)\}", lambda m: (P / (m.group(1) + ".tex")).read_text(), t)
    t = re.sub(r"\\tabin\{([^}]+)\}", lambda m: (P / "tables" / (m.group(1) + ".tex")).read_text(), t)
    return t


body = inline_inputs(inline_inputs(body))
body = re.sub(r"(?<!\\)%.*", "", body)  # comments

# \colfit{% <tabular> } -> <tabular>
body = re.sub(r"\\colfit\{\s*(\\begin\{tabular\}.*?\\end\{tabular\})\}", r"\1", body, flags=re.S)

# references
body = re.sub(r"\\eqref\{([^}]+)\}", lambda m: f"({labels[m.group(1)]})", body)
body = re.sub(r"\\ref\{([^}]+)\}", lambda m: labels[m.group(1)], body)


def cite(m):
    nums = sorted(int(cites[k.strip()]) for k in m.group(1).split(","))
    return ", ".join(f"[{n}]" for n in nums)


body = re.sub(r"\\cite\{([^}]+)\}", cite, body)
body = body.replace("~[", " [")

# title block
title = re.search(r"\\title\{(.*?)\}\n", main, re.S).group(1)
authors = "Jeevika N, Jnanottam G Y, and Mallegowda M"
thanks = re.search(r"\\thanks\{(.*?)\}\}", main, re.S).group(1)
body = body[body.index("\\maketitle") + len("\\maketitle"):]  # drop original title/author block
body = re.sub(r"\\markboth\{.*?\}%\n\{.*?\}\n", "", body, flags=re.S)

body = re.sub(r"\\IEEEPARstart\{(\w)\}\{(\w+)\}", lambda m: m.group(1) + m.group(2).lower(), body)
body = body.replace("\\begin{abstract}", "\\textbf{\\textit{Abstract}}\u2014").replace("\\end{abstract}", "")
body = re.sub(r"\\begin\{IEEEkeywords\}\s*(.*?)\s*\\end\{IEEEkeywords\}",
              lambda m: "\\textbf{\\textit{Index Terms}}\u2014" + m.group(1), body, flags=re.S)

# appendices: letter the sections
app_i = body.index("\\appendices")
pre, post = body[:app_i], body[app_i + len("\\appendices"):]
letters = iter("ABCDEFG")
post = re.sub(r"\\section\{([^}]*)\}", lambda m: f"\\section*{{Appendix {next(letters)}: {m.group(1)}}}", post)
body = pre + post

# numbered headings, IEEE style (I., A., 1))
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
sec = [0, 0, 0]


def heading(m):
    lvl, star, txt = m.group(1), m.group(2), m.group(3)
    if star:
        return m.group(0)
    if lvl == "section":
        sec[0] += 1; sec[1] = 0; sec[2] = 0
        return f"\\section*{{{ROMAN[sec[0]]}. {txt}}}"
    if lvl == "subsection":
        sec[1] += 1; sec[2] = 0
        return f"\\subsection*{{{chr(64 + sec[1])}. {txt}}}"
    sec[2] += 1
    return f"\\subsubsection*{{{sec[2]}) {txt}}}"


body = re.sub(r"\\(section|subsection|subsubsection)(\*?)\{([^}]*)\}", heading, body)

# figures: pdf -> png, explicit widths, caption prefix
def fig_env(m):
    env, inner = m.group(1), m.group(2)
    lab = re.search(r"\\label\{([^}]+)\}", inner).group(1)
    wide = env == "figure*"
    inner = re.sub(r"\\includegraphics\[[^\]]*\]\{([^}]+)\.pdf\}",
                   lambda g: f"\\includegraphics[width={6.4 if wide else 4.6}in]{{{P}/figures/{g.group(1)}.png}}", inner)
    inner = re.sub(r"\\caption\{", lambda _: f"\\caption{{Fig. {labels[lab]}. ", inner, count=1)
    return f"\\begin{{figure}}{inner}\\end{{figure}}"


body = re.sub(r"\\begin\{(figure\*?)\}\[[^\]]*\](.*?)\\end\{figure\*?\}", fig_env, body, flags=re.S)

# tables: caption prefix "TABLE N", drop sizing commands
def tab_env(m):
    inner = m.group(2)
    lab = re.search(r"\\label\{([^}]+)\}", inner).group(1)
    inner = re.sub(r"\\caption\{", lambda _: f"\\caption{{TABLE {labels[lab]}: ", inner, count=1)
    return f"\\begin{{table}}{inner}\\end{{table}}"


body = re.sub(r"\\begin\{(table\*?)\}\[[^\]]*\](.*?)\\end\{table\*?\}", tab_env, body, flags=re.S)
body = re.sub(r"\\renewcommand\{\\arraystretch\}\{[\d.]+\}", "", body)
for cmd in ("\\footnotesize", "\\scriptsize", "\\small", "\\centering"):
    body = body.replace(cmd + "\n", "\n").replace(cmd + " ", " ")
body = body.replace("\\begin{footnotesize}", "").replace("\\end{footnotesize}", "")
body = re.sub(r"\\cmidrule(\([^)]*\))?\{[^}]*\}", "", body)

# algorithm -> rendered image
alg = re.search(r"\\begin\{algorithm\}\[[^\]]*\](.*?)\\end\{algorithm\}", body, re.S)
alg_inner = alg.group(1)
alg_cap = re.search(r"\\caption\{([^}]*)\}", alg_inner).group(1)
alg_code = re.search(r"\\begin\{algorithmic\}.*?\\end\{algorithmic\}", alg_inner, re.S).group(0)
alg_tex = ("\\documentclass[varwidth=15cm,border=6pt]{standalone}\n\\usepackage{amsmath,amssymb,mathptmx}\n"
           "\\usepackage{algpseudocode}\n\\newcommand{\\X}{\\mathbf{X}}\\newcommand{\\Y}{\\mathbf{Y}}\n"
           "\\begin{document}\\small\n" + alg_code + "\n\\end{document}\n")
(BUILD / "alg_train.tex").write_text(alg_tex)
subprocess.run(["pdflatex", "-interaction=nonstopmode", "alg_train.tex"], cwd=BUILD, capture_output=True)
subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile", "alg_train.pdf", "alg_train"], cwd=BUILD)
body = body.replace(alg.group(0),
                    f"\\begin{{figure}}\\includegraphics[width=5.6in]{{{BUILD}/alg_train.png}}"
                    f"\\caption{{Algorithm {labels['alg:train']}. {alg_cap}}}\\end{{figure}}")

# bibliography from the .bbl
bbl = (P / "main_review.bbl").read_text()
items = re.findall(r"\\bibitem\{([^}]+)\}\s*(.*?)(?=\\bibitem\{|\\end\{thebibliography\})", bbl, re.S)
refs = []
for key, txt in items:
    t = re.sub(r"\\BIBentry\w+\s*", "", txt).replace("\\newblock", "").replace("\\allowbreak", "")
    t = re.sub(r"\\url\{([^}]*)\}", r"\\texttt{\1}", t)
    t = re.sub(r"\s+", " ", t).strip()
    refs.append(f"[{cites[key]}] {t}\n")
body = body.replace("\\bibliographystyle{IEEEtran}", "").replace(
    "\\bibliography{refs}", "\\section*{References}\n\n" + "\n".join(refs))
body = body.replace("\\appendices", "")

# equation numbers: \label{eq:..} -> \tag{n} so Word shows the PDF numbering
def tag_eq(m):
    return "\\tag{" + labels[m.group(1)] + "}"
body = re.sub(r"\\label\{(eq:[^}]+)\}", tag_eq, body)
body = body.replace("\\checkmark", "\u2713")


# table footnote rows (\multicolumn after \bottomrule) -> paragraph after the table
def move_footer(t):
    k = t.find("\\bottomrule\n\\multicolumn{")
    if k < 0:
        return t
    i = k + len("\\bottomrule\n\\multicolumn")
    i = balanced(t, i); i = balanced(t, i)
    j = balanced(t, i)
    note = t[i + 1:j - 1]
    t = t[:k] + "\\bottomrule\n" + t[j:]
    return t.replace("\\end{table}", "\\end{table}\n\n\\noindent\\textit{Note:} " + note + "\n", 1)


body = re.sub(r"\\begin\{table\}.*?\\end\{table\}", lambda m: move_footer(m.group(0)), body, flags=re.S)

macros = r"""\newcommand{\X}{\mathbf{X}}
\newcommand{\Y}{\mathbf{Y}}
\newcommand{\R}{\mathbb{R}}
"""
doc = ("\\documentclass{article}\n\\usepackage{amsmath,amssymb,graphicx,booktabs}\n" + macros +
       "\\begin{document}\n" + f"\\title{{{title}}}\n\\author{{{authors}}}\n\\date{{}}\n\\maketitle\n" +
       f"\\noindent\\textit{{{thanks}}}\n\n" + body + "\\end{document}\n")
flat = BUILD / "paper_flat.tex"
flat.write_text(doc)

# ------------------------------------------------------------------ reference doc + pandoc
ref = BUILD / "reference.docx"
subprocess.run(["pandoc", "-o", str(ref), "--print-default-data-file", "reference.docx"], check=True)
rd = Document(ref)
for st in rd.styles:
    try:
        st.font.name = "Times New Roman"
        rpr = st.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts"); rpr.append(rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(a), "Times New Roman")
        st.font.color.rgb = None
    except (AttributeError, ValueError):
        pass
sizes = {"Normal": 10, "Body Text": 10, "First Paragraph": 10, "Compact": 9, "Title": 24, "Author": 11,
         "Heading 1": 10, "Heading 2": 10, "Heading 3": 10, "Caption": 8, "Image Caption": 8, "Table Caption": 8}
STY = {st.name: st for st in rd.styles}
for name, sz in sizes.items():
    if name in STY:
        STY[name].font.size = Pt(sz)
STY["Heading 1"].font.small_caps = True
STY["Heading 1"].font.bold = False
for name in ("Heading 2", "Heading 3"):
    STY[name].font.italic = True
    STY[name].font.bold = False
STY["Title"].font.bold = False
rd.save(ref)

out = ROOT / "output" / "RA-PatchTST_IEEE_paper.docx"
# Pandoc's LaTeX reader can lose text when several tables follow each other, so each table is
# converted on its own and spliced into the Markdown of the prose.
src = flat.read_text()
pre_tex = src[:src.index("\\begin{document}")] + "\\begin{document}\n"
tables = []


def stash(m):
    tables.append(m.group(0))
    return f"\n\nDOCXTABLE{len(tables) - 1}X\n\n"


src = re.sub(r"\\begin\{table\}.*?\\end\{table\}", stash, src, flags=re.S)
md = subprocess.run(["pandoc", "-s", "-f", "latex", "-t", "markdown"], input=src, capture_output=True, text=True,
                    check=True).stdout
for i, t in enumerate(tables):
    tmd = subprocess.run(["pandoc", "-f", "latex", "-t", "markdown"], input=pre_tex + t + "\n\\end{document}",
                         capture_output=True, text=True, check=True).stdout
    assert "---" in tmd, f"table {i} failed to convert"
    md = md.replace(f"DOCXTABLE{i}X", tmd)
assert "DOCXTABLE" not in md
(BUILD / "paper.md").write_text(md)
subprocess.run(["pandoc", str(BUILD / "paper.md"), "-f", "markdown", "-t", "docx", "--reference-doc", str(ref),
                "-o", str(out)], check=True, cwd=BUILD)

# ------------------------------------------------------------------ post-format
d = Document(out)
for sec_ in d.sections:
    sec_.page_width, sec_.page_height = Inches(8.5), Inches(11)
    sec_.left_margin = sec_.right_margin = Inches(0.75)
    sec_.top_margin, sec_.bottom_margin = Inches(0.75), Inches(1.0)
for p in d.paragraphs:
    sn = p.style.name
    if sn in ("Title", "Author", "Image Caption", "Table Caption", "Captioned Figure", "Heading 1"):
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif sn in ("Body Text", "First Paragraph"):
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if p.text.startswith("[") and re.match(r"^\[\d+\] ", p.text):
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        for r in p.runs:
            r.font.size = Pt(8)
    if any(r.element.findall(".//" + qn("w:drawing")) for r in p.runs):
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
for t in d.tables:
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl = t._tbl
    pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "8"); e.set(qn("w:color"), "000000")
        borders.append(e)
    pr.append(borders)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8)
d.save(out)
print("wrote", out)
