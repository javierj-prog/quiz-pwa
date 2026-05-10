import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bitacora_sostenible.app import normalize_fact_sheet


env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))

for example in ["bitacora_cetaceos_demo.json", "bitacora_agua_demo.json"]:
    data = normalize_fact_sheet(json.loads((ROOT / "examples" / example).read_text(encoding="utf-8")))
    for template_name in ["base.html", "editorial_visual.html"]:
        css_name = "editorial_visual.css" if template_name == "editorial_visual.html" else "bitacora.css"
        html = env.get_template(template_name).render(data=data, css=(ROOT / "styles" / css_name).read_text(encoding="utf-8"))
        assert "Bitácora" in html

print("OK: examples render in both templates")
