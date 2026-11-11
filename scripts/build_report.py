#!/usr/bin/env python3
"""Build a single-file HTML project report from a JSON spec.

Usage:
    python build_report.py report.json output.html

Mermaid diagrams are rendered to inline SVG when the Mermaid CLI (`mmdc`)
is available; otherwise the page loads Mermaid from a CDN and renders in
the browser.
"""
import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LABELS = {
    "en": {
        "toc": "Contents", "flows": "User flows: walk through one action",
        "flows_intro": "Each flow starts from one action in the app and follows the code until the data is stored. "
                       "Every step lists what happened, the <b>technologies</b> used, and the <b>files</b>: "
                       "path, what the file is for, and the function used in this step "
                       "(a function is a named piece of code that does one job).",
        "main_flows": "Main flows in this project", "steps": "steps", "flow": "Flow", "scene": "Scenario",
        "tech_used": "Technologies used", "files": "Files",
        "tree": "Folder structure and what each file does", "file_col": "File / folder", "role_col": "What it does",
        "tech": "Technologies", "tech_cols": ["Technology", "In plain words", "Layer", "What it does here"],
        "dataflow": "Data flow", "storage": "Where data is stored",
        "storage_cols": ["Location", "What is stored", "Why it is stored here"],
        "checklist": "Pre-launch checklist", "check_cols": ["Check", "Status", "How it is done", "Evidence"],
        "status": {"done": "Done", "partial": "Partial", "missing": "Not done"},
        "quiz": "Interview self-test", "quiz_intro": "Answer first, then open the key points. Ask an AI about anything you still don't get.",
        "findings": "Surprises found in the code", "summary_note": "",
    },
    "zh": {
        "toc": "目录", "flows": "操作流程：跟着操作走一遍",
        "flows_intro": "每条流程从你在网页上的一次操作开始，一步步写到数据存进哪里。每步先写发生了什么，再写<b>用到的技术</b>各自干了什么，"
                       "最后是<b>对应文件</b>：文件路径、这个文件管什么、这一步用到的函数（文件里一段有名字、专门干一件事的代码）。",
        "main_flows": "这个项目的主要流程", "steps": "步", "flow": "流程", "scene": "场景",
        "tech_used": "用到的技术", "files": "对应文件",
        "tree": "文件夹结构与每个文件的作用", "file_col": "文件 / 文件夹", "role_col": "作用",
        "tech": "用了哪些技术", "tech_cols": ["技术", "打个比方", "属于哪层", "在这个项目里干什么"],
        "dataflow": "数据流向", "storage": "数据存在哪里",
        "storage_cols": ["位置", "存了什么", "为什么放这里"],
        "checklist": "上线检查清单", "check_cols": ["检查项", "状态", "怎么做的", "证据"],
        "status": {"done": "已实现", "partial": "部分", "missing": "未实现"},
        "quiz": "面试自测", "quiz_intro": "先自己回答，再点开看要点。答不上来的，可以复制问题去问 AI。",
        "findings": "读代码时的意外发现", "summary_note": "",
    },
}

CSS = """
:root{--bg:#fafaf9;--card:#fff;--text:#1c1917;--muted:#57534e;--line:#e7e5e4;--accent:#1d4ed8;--ok:#15803d;--okbg:#dcfce7;--part:#a16207;--partbg:#fef9c3;--no:#b91c1c;--nobg:#fee2e2;--code:#f5f5f4}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1c1917;--card:#292524;--text:#f5f5f4;--muted:#a8a29e;--line:#44403c;--accent:#93c5fd;--ok:#86efac;--okbg:#14532d;--part:#fde68a;--partbg:#713f12;--no:#fca5a5;--nobg:#7f1d1d;--code:#1c1917}}
:root[data-theme="dark"]{--bg:#1c1917;--card:#292524;--text:#f5f5f4;--muted:#a8a29e;--line:#44403c;--accent:#93c5fd;--ok:#86efac;--okbg:#14532d;--part:#fde68a;--partbg:#713f12;--no:#fca5a5;--nobg:#7f1d1d;--code:#1c1917}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif}
.layout{max-width:1260px;margin:0 auto;display:grid;grid-template-columns:240px minmax(0,1fr);gap:8px;padding:0 16px}
main{margin:0;width:100%;min-width:0;max-width:960px;padding:32px 0 64px;overflow-wrap:break-word}
main p,.fp,code,.chip{overflow-wrap:anywhere}
.toc{position:sticky;top:0;align-self:start;max-height:100vh;overflow:auto;padding:32px 8px 32px 0;font-size:13.5px}
.toc-h{font-weight:700;margin-bottom:8px}.toc ol{list-style:none;margin:0;padding:0}.toc ol ol{padding-left:12px;margin:2px 0 6px}
.toc li{margin:2px 0}.toc a{color:var(--muted);text-decoration:none;display:block;padding:3px 6px;border-radius:6px}.toc a:hover{color:var(--text);background:var(--card)}
@media (max-width:1000px){.layout{grid-template-columns:minmax(0,1fr)}.toc{position:static;max-height:none;padding:24px 0 0}.toc ol ol{display:none}}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:40px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line);scroll-margin-top:12px}
h3{font-size:16.5px;margin:28px 0 4px;scroll-margin-top:12px}
.sub{color:var(--muted);margin:0 0 16px}.note{font-size:13px;color:var(--muted);margin-top:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600;white-space:nowrap}tr:last-child td{border-bottom:none}
code{background:var(--code);border:1px solid var(--line);border-radius:4px;padding:0 4px;font-size:13px;word-break:break-all}
.b{display:inline-block;font-size:12px;font-weight:600;border-radius:999px;padding:1px 9px;white-space:nowrap}
.done{color:var(--ok);background:var(--okbg)}.partial{color:var(--part);background:var(--partbg)}.missing{color:var(--no);background:var(--nobg)}
.summary{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 0}
.chip{display:inline-block;font-size:12px;border-radius:6px;padding:1px 7px;border:1px solid var(--line);color:var(--accent)}
.steps{display:flex;flex-direction:column;gap:10px}
.step{display:flex;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.step .num{flex:0 0 28px;height:28px;border-radius:50%;background:var(--accent);color:var(--card);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.step .body{min-width:0}.step .st{font-weight:700}.step p{margin:4px 0 8px}
.lbl{font-size:12px;font-weight:700;color:var(--muted);margin:10px 0 4px}
.techs{margin:0;padding-left:18px}.techs li{margin:2px 0;font-size:14px}
.files{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-direction:column;gap:6px}
.files li{border-left:3px solid var(--line);padding-left:10px;display:flex;flex-direction:column}
.fp{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;word-break:break-all}.fr{font-size:13.5px}.fn{font-size:13px;color:var(--muted)}
td.tree{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;white-space:nowrap}td.tree.dir{font-weight:700;color:var(--accent)}
.diagram svg{width:100%;height:auto}.diagram.arch svg{max-width:640px;display:block;margin:0 auto}
.flowlist ol{margin:8px 0 0;padding-left:20px}.flowlist a{color:var(--accent)}
details{border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:8px 0;background:var(--card)}
summary{cursor:pointer;font-weight:600}details .ans{margin:8px 0 0;color:var(--muted)}
.qt{display:inline-block;font-size:12px;font-weight:600;color:var(--accent);border:1px solid var(--line);border-radius:999px;padding:0 8px;margin-right:8px}
.findings li{margin:4px 0}
"""


def esc(value):
    return html.escape(str(value), quote=False)


def render_mermaid(source, svg_id):
    """Return inline SVG via mmdc, or a client-side Mermaid block."""
    mmdc = shutil.which("mmdc")
    if mmdc:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp, "d.mmd")
            out = Path(tmp, "d.svg")
            cfg = Path(tmp, "c.json")
            src.write_text(source, encoding="utf-8")
            cfg.write_text(json.dumps({
                "themeVariables": {"fontFamily": "Noto Sans CJK SC, Segoe UI, sans-serif"},
                "flowchart": {"wrappingWidth": 420, "htmlLabels": True},
            }), encoding="utf-8")
            result = subprocess.run([mmdc, "-i", str(src), "-o", str(out), "-c", str(cfg), "-b", "transparent"],
                                    capture_output=True, text=True)
            if result.returncode == 0 and out.exists():
                svg = out.read_text(encoding="utf-8")
                svg = svg[svg.find("<svg"):]
                return svg.replace("my-svg", svg_id), False
    return f'<pre class="mermaid">{esc(source)}</pre>', True


def table(headers, rows):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="card"><table><tr>{head}</tr>{body}</table></div>'


def build(spec):
    L = LABELS[spec.get("lang", "en")]
    p = spec["project"]
    sections = []  # (id, title, html)
    needs_cdn = False

    # 1. Flows
    flows = spec["flows"]
    parts = [f'<p class="sub">{L["flows_intro"]}</p>',
             f'<div class="card flowlist"><b>{L["main_flows"]}</b><ol>' +
             "".join(f'<li><a href="#{f["id"]}">{esc(f["name"])}</a> ({len(f["steps"])} {L["steps"]})</li>' for f in flows) +
             "</ol>" + (f'<p class="note">{esc(spec["other_flows_note"])}</p>' if spec.get("other_flows_note") else "") + "</div>"]
    for k, f in enumerate(flows):
        parts.append(f'<h3 id="{f["id"]}">{L["flow"]} {chr(65 + k)}: {esc(f["name"])}</h3>'
                     f'<p class="sub">{L["scene"]}: {esc(f["scene"])}</p><div class="steps">')
        for i, s in enumerate(f["steps"], 1):
            techs = "".join(f"<li><b>{esc(n)}</b>: {esc(w)}</li>" for n, w in s["tech"])
            files = "".join(
                f'<li><span class="fp">{esc(fp)}</span><span class="fr">{esc(role)}</span>' +
                (f'<span class="fn">{esc(fn)}</span>' if fn else "") + "</li>" for fp, role, fn in s["files"])
            parts.append(f'<div class="step"><div class="num">{i}</div><div class="body">'
                         f'<div class="st">{esc(s["title"])} <span class="chip">{esc(s["layer"])}</span></div>'
                         f'<p>{esc(s["what"])}</p><div class="lbl">{L["tech_used"]}</div><ul class="techs">{techs}</ul>'
                         f'<div class="lbl">{L["files"]}</div><ul class="files">{files}</ul></div></div>')
        parts.append("</div>")
        if f.get("note"):
            parts.append(f'<p class="note">{esc(f["note"])}</p>')
    sections.append(("flows", L["flows"], "".join(parts)))

    # 2. Tree
    rows = []
    for depth, name, desc, is_dir, layer in spec["tree"]:
        chip = f'<span class="chip">{esc(layer)}</span> ' if layer else ""
        cls = "tree dir" if is_dir else "tree"
        rows.append(f'<tr><td class="{cls}" style="padding-left:{10 + depth * 18}px">{esc(name)}</td><td>{chip}{esc(desc)}</td></tr>')
    sections.append(("tree", L["tree"],
                     f'<div class="card"><table><tr><th>{L["file_col"]}</th><th>{L["role_col"]}</th></tr>{"".join(rows)}</table></div>'))

    # 3. Tech
    arch, cdn = render_mermaid(spec["arch_mermaid"], "arch-svg")
    needs_cdn |= cdn
    tech_rows = [[f"<b>{esc(a)}</b>", esc(b), f'<span class="chip">{esc(c)}</span>', esc(d)] for a, b, c, d in spec["tech"]]
    sections.append(("tech", L["tech"], f'<div class="card diagram arch">{arch}</div><div style="height:12px"></div>' +
                     table(L["tech_cols"], tech_rows)))

    # 4. Data flow
    flow_svg, cdn = render_mermaid(spec["dataflow_mermaid"], "flow-svg")
    needs_cdn |= cdn
    sections.append(("dataflow", L["dataflow"], f'<div class="card diagram">{flow_svg}</div>'))

    # 5. Storage
    sections.append(("storage", L["storage"], table(L["storage_cols"], [[esc(c) for c in r] for r in spec["storage"]])))

    # 6. Checklist
    counts = {"done": 0, "partial": 0, "missing": 0}
    rows = []
    for item, status, how, evidence in spec["checklist"]:
        counts[status] += 1
        rows.append([esc(item), f'<span class="b {status}">{L["status"][status]}</span>', esc(how), f"<code>{esc(evidence)}</code>" if evidence else "—"])
    summary = '<div class="summary">' + "".join(f'<span class="b {k}">{L["status"][k]} {v}</span>' for k, v in counts.items()) + "</div>"
    sections.append(("checklist", L["checklist"], table(L["check_cols"], rows) + summary))

    # 7. Quiz
    qs = [f'<p class="sub">{L["quiz_intro"]}</p>']
    for q in spec["quiz"]:
        answer = f'<p class="ans">{esc(q["answer"])}</p>' if q.get("answer") else ""
        if q.get("table"):
            answer += '<div style="overflow-x:auto;margin-top:8px">' + table(q["table"]["headers"], [[esc(c) for c in r] for r in q["table"]["rows"]]) + "</div>"
        qs.append(f'<details><summary><span class="qt">{esc(q["type"])}</span>{esc(q["question"])}</summary>{answer}</details>')
    sections.append(("quiz", L["quiz"], "".join(qs)))

    # Optional findings
    if spec.get("findings"):
        sections.append(("findings", L["findings"],
                         '<div class="card"><ul class="findings">' + "".join(f"<li>{esc(x)}</li>" for x in spec["findings"]) + "</ul></div>"))

    toc = f'<nav class="toc" aria-label="{L["toc"]}"><div class="toc-h">{L["toc"]}</div><ol>'
    for n, (sid, title, _) in enumerate(sections, 1):
        toc += f'<li><a href="#{sid}">{n}. {esc(title)}</a>'
        if sid == "flows":
            toc += "<ol>" + "".join(f'<li><a href="#{f["id"]}">{L["flow"]} {chr(65 + k)} {esc(f["name"])}</a></li>' for k, f in enumerate(flows)) + "</ol>"
        toc += "</li>"
    toc += "</ol></nav>"

    body = "".join(f'<h2 id="{sid}">{n}. {esc(title)}</h2>{content}' for n, (sid, title, content) in enumerate(sections, 1))
    cdn_script = ('<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs";'
                  'mermaid.initialize({startOnLoad:true});</script>') if needs_cdn else ""
    lang_attr = "zh-CN" if spec.get("lang") == "zh" else "en"
    return (f'<!doctype html><html lang="{lang_attr}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(p["name"])} — Project Report</title>'
            f"<style>{CSS}</style></head><body><div class=\"layout\">{toc}<main><h1>{esc(p['name'])}</h1>"
            f'<p class="sub">{esc(p["summary"])}</p>{body}</main></div>{cdn_script}</body></html>')


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: build_report.py report.json output.html")
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    Path(sys.argv[2]).write_text(build(spec), encoding="utf-8")
    print(f"wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
