# -*- coding: utf-8 -*-
import base64, io, re, mimetypes, pathlib, markdown
from PIL import Image

# thumbnails are displayed ~90px tall; 360px source keeps them sharp on retina
THUMB_MAX = (640, 360)
JPEG_QUALITY = 72

BASE = pathlib.Path(__file__).parent
MD = BASE / "Маршрут_Чжанцзяцзе_Яншо_Гуанчжоу.md"
HTML = BASE / "Маршрут_Чжанцзяцзе_Яншо_Гуанчжоу.html"

text = MD.read_text(encoding="utf-8")

html_body = markdown.markdown(
    text,
    extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"],
)

# Inline local images as base64 data URIs; drop <img> whose file is missing.
def inline_img(m):
    src = m.group(1)
    p = (BASE / src).resolve()
    if not p.exists():
        # tolerate .jpg/.png extension mismatch
        alt = p.with_suffix(".png" if p.suffix == ".jpg" else ".jpg")
        if alt.exists():
            p = alt
        else:
            return 'data-missing="1"'
    img = Image.open(p)
    img.thumbnail(THUMB_MAX, Image.LANCZOS)
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return f'src="data:image/jpeg;base64,{data}"'

html_body = re.sub(r'src="([^"]+)"', inline_img, html_body)
# remove img tags whose source was missing
html_body = re.sub(r'<img[^>]*data-missing="1"[^>]*>', "", html_body)

CSS = """
@page { size: A4; margin: 15mm 13mm 16mm 13mm; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Segoe UI", "Segoe UI Emoji", "Segoe UI Symbol",
               "Microsoft YaHei", "Noto Sans CJK SC", "PingFang SC", Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.5; color: #24292e;
  max-width: 840px; margin: 0 auto; padding: 0 4px;
}
h1 { font-size: 24pt; line-height: 1.2; color: #b30000;
  border-bottom: 3px solid #b30000; padding-bottom: .25em; margin: .2em 0 .5em; }
h2 { font-size: 16pt; color: #c0392b; margin-top: 1.3em;
  border-bottom: 1px solid #f0c9c0; padding-bottom: .15em; page-break-after: avoid; }
h3 { font-size: 12.5pt; color: #1b4965; margin-top: 1em; page-break-after: avoid; }
p { margin: .45em 0; }
a { color: #c0392b; text-decoration: none; }
strong { color: #1a1a1a; }
ul { margin: .35em 0; padding-left: 1.25em; }
li { margin: .15em 0; }
em { color: #6a737d; font-size: .92em; }

/* photo gallery: one compact strip of thumbnails per day */
.gallery {
  display: flex; flex-wrap: nowrap; gap: 5px;
  margin: .5em 0 .9em; page-break-inside: avoid;
}
.gallery img {
  flex: 1 1 0; min-width: 0; height: 88px; object-fit: cover;
  border-radius: 5px; box-shadow: 0 1px 4px rgba(0,0,0,.16);
}

table { border-collapse: collapse; width: 100%; margin: .7em 0;
  font-size: 9.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #e1c8c0; padding: 6px 9px; text-align: left; vertical-align: top; }
th { background: #b30000; color: #fff; font-weight: 600; }
tr:nth-child(even) td { background: #fbf3f1; }
blockquote { border-left: 4px solid #e0a800; background: #fffbe6;
  margin: .6em 0; padding: .45em .85em; border-radius: 0 6px 6px 0;
  color: #5a4b00; font-size: .94em; }
pre { background: #1b1f23; color: #e6edf3; padding: 12px 14px;
  border-radius: 8px; overflow-x: auto; font-size: 9pt; line-height: 1.4; page-break-inside: avoid; }
code { font-family: "Cascadia Code", "Consolas", monospace; }
pre code { color: inherit; }
hr { border: none; border-top: 1px solid #e1e4e8; margin: 1.2em 0; }
h2, h3, table, blockquote, pre { page-break-inside: avoid; }
"""

doc = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<title>Чжанцзяцзе · Яншо · Гуанчжоу — маршрут</title>
<style>{CSS}</style></head>
<body>{html_body}</body></html>"""

HTML.write_text(doc, encoding="utf-8")
print("HTML written, images embedded:", html_body.count("data:image"))
