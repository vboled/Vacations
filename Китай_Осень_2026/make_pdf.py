# -*- coding: utf-8 -*-
import base64, re, mimetypes, pathlib, markdown

BASE = pathlib.Path(__file__).parent
MD = BASE / "Маршрут_Китай_Осень_2026.md"
HTML = BASE / "Маршрут_Китай_Осень_2026.html"

text = MD.read_text(encoding="utf-8")

html_body = markdown.markdown(
    text,
    extensions=["tables", "fenced_code", "sane_lists", "nl2br", "attr_list"],
)

# Inline local images as base64 data URIs so the PDF is self-contained
def inline_img(m):
    src = m.group(1)
    p = (BASE / src).resolve()
    if not p.exists():
        return m.group(0)
    mime = mimetypes.guess_type(str(p))[0] or "image/jpeg"
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f'src="data:{mime};base64,{data}"'

html_body = re.sub(r'src="([^"]+)"', inline_img, html_body)

CSS = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
* { box-sizing: border-box; }
body {
  font-family: "Segoe UI", "Segoe UI Emoji", "Segoe UI Symbol", Arial, sans-serif;
  font-size: 11pt; line-height: 1.55; color: #24292e;
  max-width: 820px; margin: 0 auto; padding: 0 4px;
}
h1 {
  font-size: 26pt; line-height: 1.2; color: #b30000;
  border-bottom: 3px solid #b30000; padding-bottom: .25em;
  margin: .2em 0 .6em;
}
h2 {
  font-size: 17pt; color: #c0392b; margin-top: 1.4em;
  border-bottom: 1px solid #f0c9c0; padding-bottom: .15em;
  page-break-after: avoid;
}
h3 { font-size: 13pt; color: #1b4965; margin-top: 1.1em; page-break-after: avoid; }
p { margin: .5em 0; }
a { color: #c0392b; text-decoration: none; }
strong { color: #1a1a1a; }
ul { margin: .4em 0; padding-left: 1.3em; }
li { margin: .2em 0; }
img {
  max-width: 100%; border-radius: 8px; margin: .6em 0 .2em;
  box-shadow: 0 2px 8px rgba(0,0,0,.18); display: block;
}
em { color: #6a737d; font-size: .92em; }
table {
  border-collapse: collapse; width: 100%; margin: .8em 0;
  font-size: 10pt; page-break-inside: avoid;
}
th, td { border: 1px solid #e1c8c0; padding: 7px 10px; text-align: left; vertical-align: top; }
th { background: #b30000; color: #fff; font-weight: 600; }
tr:nth-child(even) td { background: #fbf3f1; }
blockquote {
  border-left: 4px solid #e0a800; background: #fffbe6;
  margin: .7em 0; padding: .5em .9em; border-radius: 0 6px 6px 0;
  color: #5a4b00; font-size: .96em;
}
pre {
  background: #1b1f23; color: #e6edf3; padding: 14px 16px;
  border-radius: 8px; overflow-x: auto; font-size: 9.5pt; line-height: 1.4;
  page-break-inside: avoid;
}
code { font-family: "Cascadia Code", "Consolas", monospace; }
pre code { color: inherit; }
hr { border: none; border-top: 1px solid #e1e4e8; margin: 1.4em 0; }
h2, h3, img, table, blockquote, pre { page-break-inside: avoid; }
"""

doc = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<title>Китай · Осень 2026 — маршрут</title>
<style>{CSS}</style></head>
<body>{html_body}</body></html>"""

HTML.write_text(doc, encoding="utf-8")
print("HTML written:", HTML)
