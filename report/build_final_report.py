"""Build the final report .docx from AIN_Final_Report_Template.docx and report_content.py.

The cover, styles, headers, footers and the table of contents of the template are kept.
The instruction page and every guidance paragraph are removed, and the body is rebuilt
with the template's own styles (Heading 1/2, Normal, Caption, Table Text, Code,
Reference, List Paragraph), SEQ caption fields and native Word equations.

Usage (system Python with python-docx, from the repository root):
    python report/build_final_report.py --class-code 61FIT3AIN-TUT01 --group 03
Then run report/finalize_report.ps1 to let Word update the TOC and caption fields.
"""
from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt
from lxml import etree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import report_content as C  # noqa: E402

TEMPLATE = HERE / "AIN_Final_Report_Template.docx"
MML2OMML = Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL")
TEXT_WIDTH = 9070  # dxa, A4 with 2.5 cm margins
BULLET_NUM_ID = "2"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# ----------------------------------------------------------------------------- labels and citations
LABELS: dict[str, int] = {}
CITE_ORDER: list[str] = []


def collect_labels_and_citations() -> None:
    counters = {"tab": 0, "fig": 0, "eq": 0}
    texts: list[str] = []
    for block in C.BLOCKS:
        kind = block[0]
        if kind == "table":
            counters["tab"] += 1
            LABELS[f"tab:{block[1]}"] = counters["tab"]
        elif kind in ("fig", "fig2"):
            counters["fig"] += 1
            LABELS[f"fig:{block[1]}"] = counters["fig"]
        elif kind == "eq":
            counters["eq"] += 1
            LABELS[f"eq:{block[1]}"] = counters["eq"]
        texts.append(repr(block))
    groups = re.findall(r"\[(@[^\]]+)\]", "\n".join(texts))
    for key in [k.strip().lstrip("@") for group in groups for k in group.split(";")]:
        if key not in CITE_ORDER:
            if key not in C.REFERENCES:
                raise KeyError(f"Unknown citation key {key}")
            CITE_ORDER.append(key)
    unused = set(C.REFERENCES) - set(CITE_ORDER)
    if unused:
        raise ValueError(f"References never cited: {sorted(unused)}")


def resolve(text: str) -> str:
    def cite(match: re.Match) -> str:
        keys = [k.strip().lstrip("@") for k in match.group(1).split(";")]
        return ", ".join(f"[{CITE_ORDER.index(k) + 1}]" for k in keys)

    text = re.sub(r"\[(@[^\]]+)\]", cite, text)
    return re.sub(r"\{((?:tab|fig|eq):[a-z0-9_]+)\}", lambda m: str(LABELS[m.group(1)]), text)


# ----------------------------------------------------------------------------- runs from markup
TOKEN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|_\{.+?\}|\^\{.+?\})")


def add_runs(paragraph, markup: str, size: int | None = None, bold: bool = False) -> None:
    for part in TOKEN.split(resolve(markup)):
        if not part:
            continue
        kwargs = {}
        if part.startswith("**"):
            text, kwargs["bold"] = part[2:-2], True
        elif part.startswith("*"):
            text, kwargs["italic"] = part[1:-1], True
        elif part.startswith("_{"):
            text, kwargs["sub"] = part[2:-1], True
        elif part.startswith("^{"):
            text, kwargs["sup"] = part[2:-1], True
        else:
            text = part
        # Nested italics inside bold, e.g. **F1 — *x***, are not needed in this report.
        run = paragraph.add_run(text)
        if kwargs.get("bold") or bold:
            run.bold = True
        if kwargs.get("italic"):
            run.italic = True
        if kwargs.get("sub"):
            run.font.subscript = True
        if kwargs.get("sup"):
            run.font.superscript = True
        if size:
            run.font.size = Pt(size / 2)


def set_text_keep_format(paragraph, text: str) -> None:
    runs = paragraph.runs
    runs[0].text = text
    for run in runs[1:]:
        run._r.getparent().remove(run._r)


# ----------------------------------------------------------------------------- builders
class Builder:
    def __init__(self, doc: docx.Document):
        self.doc = doc
        self.body = doc.element.body
        self.sect = self.body.find(qn("w:sectPr"))
        self.xslt = etree.XSLT(etree.parse(str(MML2OMML)))

    def _append(self, element) -> None:
        self.sect.addprevious(element)

    def par(self, markup: str = "", style: str = "Normal", align=None, keep_next=False, page_break=False,
            space_after=None, size=None):
        p = self.doc.add_paragraph(style=style)
        if markup:
            add_runs(p, markup, size=size)
        if align is not None:
            p.alignment = align
        if keep_next:
            p.paragraph_format.keep_with_next = True
        if page_break:
            p.paragraph_format.page_break_before = True
        if space_after is not None:
            p.paragraph_format.space_after = Pt(space_after)
        return p

    def heading(self, text: str, level: int):
        p = self.par(text, style=f"Heading {level}")
        if text.startswith("References") or text.startswith("Appendix A"):
            p.paragraph_format.page_break_before = True
        return p

    def bullets(self, items: list[str]) -> None:
        for item in items:
            p = self.par(item, style="List Paragraph", align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            p_pr = p._p.get_or_add_pPr()
            p_pr.insert(1, parse_xml(f'<w:numPr {nsdecls("w")}><w:ilvl w:val="0"/>'
                                     f'<w:numId w:val="{BULLET_NUM_ID}"/></w:numPr>'))

    def caption(self, kind: str, label: str, text: str, keep_next: bool) -> None:
        number = LABELS[f"{'tab' if kind == 'Table' else 'fig'}:{label}"]
        p = self.doc.add_paragraph(style="Caption")
        if keep_next:
            p.paragraph_format.keep_with_next = True
        r = p.add_run(f"{kind} ")
        r.bold = True
        p._p.append(parse_xml(
            f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="begin"/></w:r>'))
        p._p.append(parse_xml(f'<w:r {nsdecls("w")}><w:instrText xml:space="preserve">SEQ {kind} \\* ARABIC'
                              f'</w:instrText></w:r>'))
        p._p.append(parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="separate"/></w:r>'))
        p._p.append(parse_xml(f'<w:r {nsdecls("w")}><w:rPr><w:noProof/></w:rPr><w:t>{number}</w:t></w:r>'))
        p._p.append(parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="end"/></w:r>'))
        r = p.add_run(": ")
        r.bold = True
        add_runs(p, text)

    def equation(self, label: str, mathml: str) -> None:
        omml = self.xslt(etree.fromstring(mathml.encode("utf-8")))
        o_math = omml.getroot()
        if o_math.tag.endswith("oMathPara"):
            o_math = o_math[0] if o_math[0].tag.endswith("oMath") else o_math.find(".//{*}oMath")
        # Display-style equation in a borderless two-column table, number on the right.
        m_ns = "http://schemas.openxmlformats.org/officeDocument/2006/math"
        tbl = parse_xml(
            f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblW w:w="{TEXT_WIDTH}" w:type="dxa"/>'
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="0" w:type="dxa"/>'
            '<w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="8270"/><w:gridCol w:w="800"/></w:tblGrid>'
            '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
            '<w:tc><w:tcPr><w:tcW w:w="8270" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
            '<w:p><w:pPr><w:spacing w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'
            '<w:jc w:val="center"/></w:pPr></w:p></w:tc>'
            '<w:tc><w:tcPr><w:tcW w:w="800" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
            '<w:p><w:pPr><w:spacing w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'
            f'<w:jc w:val="right"/></w:pPr><w:r><w:t>({LABELS["eq:" + label]})</w:t></w:r></w:p></w:tc>'
            '</w:tr></w:tbl>')
        math_par = etree.SubElement(tbl.find(".//" + qn("w:p")), f"{{{m_ns}}}oMathPara")
        math_par.append(copy.deepcopy(o_math))
        self._append(tbl)

    def table(self, label: str, caption: str, header_rows, rows, widths, opts) -> None:
        assert sum(widths) == TEXT_WIDTH, (label, sum(widths))
        size = opts.get("size")
        center_from = opts.get("center_from")
        self.caption("Table", label, caption, keep_next=True)
        border = ('<w:tcBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                  '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                  '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                  '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>')
        grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
        tbl = parse_xml(
            f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblW w:w="{TEXT_WIDTH}" w:type="dxa"/>'
            '<w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
            '<w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
            '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
            '<w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
            '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
            '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tblBorders>'
            '<w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
            '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar>'
            '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" '
            f'w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid></w:tbl>')
        # Header rows may contain (text, colspan, rowspan) tuples and None for a vertically merged cell.
        all_rows = [(r, True) for r in header_rows] + [(r, False) for r in rows]
        vmerge_open: dict[int, bool] = {}
        for row_cells, is_header in all_rows:
            tr = parse_xml(f'<w:tr {nsdecls("w")}><w:trPr>{"<w:tblHeader/>" if is_header else ""}'
                           f'<w:cantSplit/></w:trPr></w:tr>')
            col = 0
            for cell in row_cells:
                span, rowspan, text = 1, 1, ""
                vmerge = ""
                if cell is None:
                    vmerge = '<w:vMerge/>'
                elif isinstance(cell, tuple):
                    text, span, rowspan = cell
                    if rowspan > 1:
                        vmerge = '<w:vMerge w:val="restart"/>'
                else:
                    text = cell
                width = sum(widths[col:col + span])
                grid_span = f'<w:gridSpan w:val="{span}"/>' if span > 1 else ""
                tc = parse_xml(
                    f'<w:tc {nsdecls("w")}><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
                    f'{grid_span}{vmerge}{border}<w:vAlign w:val="center"/></w:tcPr></w:tc>')
                p = parse_xml(f'<w:p {nsdecls("w")}><w:pPr><w:pStyle w:val="TableText"/></w:pPr></w:p>')
                tc.append(p)
                tr.append(tc)
                para = docx.text.paragraph.Paragraph(p, self.doc._body)
                if text:
                    add_runs(para, text, size=size, bold=is_header)
                if (is_header and span > 1) or (center_from is not None and col >= center_from):
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if row_cells is not all_rows[-1][0] and not opts.get("split"):
                    para.paragraph_format.keep_with_next = True  # keep short tables on one page
                col += span
            tbl.append(tr)
        self._append(tbl)
        self.par("", style="Normal", space_after=0).paragraph_format.line_spacing = 1.0

    def figure(self, label: str, caption: str, path: str, width_cm: float) -> None:
        p = self.par("", align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=True, space_after=0)
        p.paragraph_format.line_spacing = 1.0
        p.add_run().add_picture(str((HERE / path).resolve()), width=Cm(width_cm))
        self.caption("Figure", label, caption, keep_next=False)

    def figure_pair(self, label: str, caption: str, items) -> None:
        table = self.doc.add_table(rows=2, cols=2)
        table.autofit = False
        tbl_pr = table._tbl.tblPr
        tbl_pr.append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="fixed"/>'))
        for col, (path, sub_caption) in enumerate(items):
            for row in range(2):
                table.cell(row, col).width = Cm(8.0)
            pic = table.cell(0, col).paragraphs[0]
            pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pic.paragraph_format.keep_with_next = True
            pic.paragraph_format.space_after = Pt(2)
            pic.paragraph_format.line_spacing = 1.0
            pic.add_run().add_picture(str((HERE / path).resolve()), width=Cm(7.75))
            cap = table.cell(1, col).paragraphs[0]
            cap.style = self.doc.styles["Table Text"]
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.keep_with_next = True
            add_runs(cap, sub_caption, size=20)
        for row in table.rows:
            row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        self._append(table._tbl)  # move it before the final sectPr (add_table already did; harmless)
        self.caption("Figure", label, caption, keep_next=False)

    def code(self, lines: list[str]) -> None:
        for i, line in enumerate(lines):
            p = self.par("", style="Code", keep_next=i < len(lines) - 1)
            if line.startswith("**"):
                r = p.add_run(line.strip("*"))
                r.bold = True
            else:
                p.add_run(line)
            if i == len(lines) - 1:
                p.paragraph_format.space_after = Pt(8)


# ----------------------------------------------------------------------------- template surgery
def text_of(el) -> str:
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def style_of(el) -> str:
    p_style = el.find(qn("w:pPr") + "/" + qn("w:pStyle"))
    return p_style.get(qn("w:val")) if p_style is not None else ""


def prepare_front_matter(doc, class_code: str, group: str, month: str) -> None:
    body = doc.element.body
    prefix = f"{class_code}_G{group}_P12"
    # Cover page.
    for p in doc.paragraphs:
        t = p.text
        if t == "[PROJECT TITLE]":
            set_text_keep_format(p, C.TITLE)
        elif t.startswith("Project [P00]"):
            set_text_keep_format(p, f"Project P12  ·  Group G{group}  ·  Class {class_code}")
        elif t.startswith("Hanoi, [Month"):
            set_text_keep_format(p, f"Hanoi, {month}")
    members = doc.tables[0]
    for row, (name, sid, rep) in zip(members.rows[1:], C.MEMBERS):
        set_text_keep_format(row.cells[1].paragraphs[0], name + ("*" if rep else ""))
        set_text_keep_format(row.cells[2].paragraphs[0], sid)
    # Running header of the body section.
    for section in doc.sections:
        for p in section.header.paragraphs:
            for run in p.runs:
                if "[PREFIX]" in run.text:
                    run.text = run.text.replace("[PREFIX]", prefix)
    # Remove the instruction page: from "Template Instructions" up to the "Abstract" heading.
    children = list(body.iterchildren())
    start = next(i for i, el in enumerate(children) if text_of(el) == "Template Instructions")
    end = next(i for i, el in enumerate(children) if text_of(el) == "Abstract")
    for el in children[start:end]:
        body.remove(el)
    # Abstract, keywords and the TOC note.
    for el in list(body.iterchildren()):
        if el.tag != qn("w:p"):
            continue
        t = text_of(el)
        if style_of(el) == "Guidance":
            body.remove(el)
        elif t == "[Write the abstract here.]":
            p = docx.text.paragraph.Paragraph(el, doc._body)
            set_text_keep_format(p, C.ABSTRACT)
        elif t.startswith("Keywords:"):
            p = docx.text.paragraph.Paragraph(el, doc._body)
            p.runs[-1].text = C.KEYWORDS
            for run in p.runs[2:]:
                run._r.getparent().remove(run._r)


def clear_body(doc) -> None:
    """Remove every element after the front-matter section break, keeping the final sectPr."""
    body = doc.element.body
    children = list(body.iterchildren())
    breaks = [i for i, el in enumerate(children)
              if el.tag == qn("w:p") and el.find(qn("w:pPr") + "/" + qn("w:sectPr")) is not None]
    front_end = breaks[1]
    for el in children[front_end + 1:]:
        if el.tag != qn("w:sectPr"):
            body.remove(el)


def build(class_code: str, group: str, month: str, output: Path) -> Path:
    collect_labels_and_citations()
    n_tables = sum(1 for k in LABELS if k.startswith("tab:"))
    LABELS["tab:contrib"], LABELS["tab:aitools"] = n_tables + 1, n_tables + 2
    doc = docx.Document(str(TEMPLATE))
    prepare_front_matter(doc, class_code, group, month)
    clear_body(doc)
    b = Builder(doc)
    for block in C.BLOCKS:
        kind = block[0]
        if kind == "h1":
            b.heading(block[1], 1)
        elif kind == "h2":
            b.heading(block[1], 2)
        elif kind == "p":
            opts = block[2] if len(block) > 2 else {}
            if opts.get("style") == "Caption":
                b.par(block[1], style="Caption", size=20)
            else:
                b.par(block[1])
        elif kind == "bullets":
            b.bullets(block[1])
        elif kind == "eq":
            b.equation(block[1], block[2])
        elif kind == "table":
            b.table(*block[1:])
        elif kind == "fig":
            b.figure(*block[1:])
        elif kind == "fig2":
            b.figure_pair(*block[1:])
        elif kind == "code":
            b.code(block[1])
        else:
            raise ValueError(kind)
    # References.
    b.heading("References", 1)
    for n, key in enumerate(CITE_ORDER, 1):
        p = b.par("", style="Reference")
        p.add_run(f"[{n}]")
        r = p.add_run()
        r.add_tab()
        add_runs(p, C.REFERENCES[key])
    # Appendix A.
    b.heading("Appendix A  Reproducibility", 1)
    b.par("The commands below install the environment and reproduce every table and figure of the report; they "
          "match code/README.md. Each script writes its results under experiments/results/.")
    for i, line in enumerate(C.REPRO_LINES):
        p = b.par("", style="Code", keep_next=i < len(C.REPRO_LINES) - 1)
        p.add_run(line)
    # Appendix B.
    b.heading("Appendix B  Member Contributions", 1)
    b.table("contrib", "Contribution of each member. * marks the group representative who submits.",
            [["Student ID", "Full name", "Main tasks", "%"]],
            [list(row) for row in C.CONTRIBUTIONS], [1500, 2100, 4870, 600], {"size": 21})
    # Appendix C.
    b.heading("Appendix C  Use of Generative AI Tools", 1)
    b.par("The team remains responsible for every claim, number and citation in this report. All results were "
          "regenerated from the committed scripts, and every reference was checked against its source.")
    widths = [2600, 4100, 2370]
    tbl_rows = [list(row) for row in C.AI_TOOLS]
    b.table("aitools", "Generative AI tools used in the project.", [["Tool", "Purpose", "Sections or files "
                                                                                       "affected"]],
            tbl_rows, widths, {"size": 21})
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output))
    return output


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--class-code", default="[CLASS CODE]")
    parser.add_argument("--group", default="[00]", help="two digits, e.g. 03")
    parser.add_argument("--month", default="November 2026")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    prefix = f"{args.class_code}_G{args.group}_P12"
    output = args.output or (HERE / ("P12_report_DRAFT.docx" if "[" in prefix else f"{prefix}_report.docx"))
    print(build(args.class_code, args.group, args.month, output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
