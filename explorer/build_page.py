"""Inject data.json into template.html and write the explorer page served by GitHub Pages."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = (HERE / "data.json").read_text().replace("</", "<\\/")
script = (HERE / "page.js").read_text()
page = (HERE / "template.html").read_text().replace("__DATA__", data, 1).replace("__SCRIPT__", script, 1)
out = HERE.parent / "docs" / "index.html"
out.write_text(page)
print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
