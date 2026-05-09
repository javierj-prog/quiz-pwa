from __future__ import annotations

import base64
import json
from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

APP_DIR = Path(__file__).parent
CONFIG_PATH = APP_DIR / "config" / "config.yaml"
OUTPUT_DIR = APP_DIR / "outputs"
TEMPLATES_DIR = APP_DIR / "templates"
STYLES_PATH = APP_DIR / "styles" / "bitacora.css"


def load_config() -> dict[str, Any]:
    defaults = {
        "publication_name": "Bitácora Sostenible",
        "subtitle": "La sostenibilidad explicada desde el trabajo diario del puerto",
        "department": "División de Transición Ecológica, Sostenibilidad Medioambiental y Sistemas de Gestión",
        "email": "medioambiente@puertoalicante.com",
        "logo_path": "assets/logo_apa.png",
        "default_issue_number": "",
        "default_date": "",
    }
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
            defaults.update(loaded)
    return defaults


def safe_slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "bitacora"


def image_to_data_uri(img_file) -> str:
    if not img_file:
        return ""
    raw = img_file.read()
    encoded = base64.b64encode(raw).decode("utf-8")
    mime = img_file.type if hasattr(img_file, "type") else "image/png"
    return f"data:{mime};base64,{encoded}"


def local_image_to_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    suffix = path.suffix.lower().replace(".", "") or "png"
    return f"data:image/{suffix};base64,{encoded}"




def load_example(name: str) -> dict[str, Any]:
    fp = APP_DIR / "examples" / name
    return json.loads(fp.read_text(encoding="utf-8"))

def compose_data(config: dict[str, Any]) -> dict[str, Any]:
    st.sidebar.header("Datos base del boletín")
    issue_number = st.sidebar.text_input("Número de boletín", value=config.get("default_issue_number", ""))
    default_dt = config.get("default_date") or str(date.today())
    issue_date = st.sidebar.text_input("Fecha", value=default_dt)

    title = st.sidebar.text_input("Titular principal")
    standfirst = st.sidebar.text_area("Entradilla", height=120)

    layout_choice = st.sidebar.selectbox(
        "Tipo de composición sugerida",
        ["Pieza divulgativa", "Pieza visual/fotográfica", "Pieza con datos", "Pieza explicativa técnica"],
    )

    st.sidebar.header("Módulos opcionales")
    module_keys = {
        "editorial": st.sidebar.checkbox("Texto editorial", value=True),
        "hero_photo": st.sidebar.checkbox("Foto protagonista", value=True),
        "gallery": st.sidebar.checkbox("Galería", value=False),
        "quote": st.sidebar.checkbox("Cita destacada", value=False),
        "concept": st.sidebar.checkbox("Concepto explicado", value=True),
        "data_highlight": st.sidebar.checkbox("Dato destacado", value=False),
        "chart": st.sidebar.checkbox("Gráfico simple", value=False),
        "map": st.sidebar.checkbox("Mapa o zona", value=False),
        "timeline": st.sidebar.checkbox("Cronología", value=False),
        "fact_sheet": st.sidebar.checkbox("Ficha visual", value=False),
        "closing": st.sidebar.checkbox("Cierre", value=True),
    }

    modules: dict[str, Any] = {}
    with st.expander("Editor de módulos", expanded=True):
        if module_keys["editorial"]:
            modules["editorial"] = {
                "title": st.text_input("Título del bloque editorial", key="editorial_title"),
                "body": st.text_area("Texto editorial", key="editorial_body", height=180),
            }

        if module_keys["hero_photo"]:
            hero_file = st.file_uploader("Foto protagonista", type=["png", "jpg", "jpeg", "webp"], key="hero")
            modules["hero_photo"] = {
                "image": image_to_data_uri(hero_file),
                "caption": st.text_input("Pie de foto (opcional)", key="hero_caption"),
            }

        if module_keys["gallery"]:
            gallery_files = st.file_uploader(
                "Galería (varias imágenes)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, key="gallery"
            )
            captions = st.text_area("Pies de galería (una línea por imagen)", key="gallery_captions")
            caption_lines = [line.strip() for line in captions.splitlines() if line.strip()]
            gallery_items = []
            for i, gf in enumerate(gallery_files):
                gallery_items.append({"image": image_to_data_uri(gf), "caption": caption_lines[i] if i < len(caption_lines) else ""})
            modules["gallery"] = gallery_items

        if module_keys["quote"]:
            modules["quote"] = {"text": st.text_area("Idea o cita destacada", key="quote_text", height=100)}

        if module_keys["concept"]:
            modules["concept"] = {
                "term": st.text_input("Término", key="concept_term"),
                "explanation": st.text_area("Explicación breve", key="concept_exp", height=120),
            }

        if module_keys["data_highlight"]:
            modules["data_highlight"] = {
                "value": st.text_input("Número", key="data_value"),
                "unit": st.text_input("Unidad", key="data_unit"),
                "description": st.text_input("Explicación breve", key="data_desc"),
            }

        if module_keys["chart"]:
            chart_rows = st.number_input("Nº de filas para gráfico", min_value=2, max_value=12, value=4)
            chart_data = []
            for i in range(chart_rows):
                c1, c2 = st.columns(2)
                label = c1.text_input(f"Etiqueta {i+1}", key=f"chart_label_{i}")
                value = c2.number_input(f"Valor {i+1}", key=f"chart_val_{i}", step=1.0)
                chart_data.append({"label": label, "value": value})
            modules["chart"] = {"series": chart_data, "kind": st.selectbox("Tipo", ["bar", "line"])}

        if module_keys["map"]:
            map_file = st.file_uploader("Mapa o esquema", type=["png", "jpg", "jpeg", "webp"], key="map")
            modules["map"] = {"image": image_to_data_uri(map_file), "caption": st.text_input("Pie del mapa", key="map_cap")}

        if module_keys["timeline"]:
            n_events = st.number_input("Número de hitos", min_value=1, max_value=10, value=3)
            events = []
            for i in range(n_events):
                st.markdown(f"**Hito {i+1}**")
                events.append(
                    {
                        "date": st.text_input("Fecha", key=f"tl_date_{i}"),
                        "title": st.text_input("Título", key=f"tl_title_{i}"),
                        "description": st.text_input("Descripción breve", key=f"tl_desc_{i}"),
                    }
                )
            modules["timeline"] = events

        if module_keys["fact_sheet"]:
            modules["fact_sheet"] = {
                "title": st.text_input("Título ficha", key="fact_title"),
                "summary": st.text_area("Resumen", key="fact_summary", height=120),
                "items": st.text_area("Elementos clave (una línea por punto)", key="fact_items", height=100),
            }

        if module_keys["closing"]:
            modules["closing"] = {"text": st.text_area("Cierre breve", key="closing_text", height=100)}

    logo_uri = local_image_to_data_uri(APP_DIR / config["logo_path"])

    return {
        "meta": {
            "publication_name": config["publication_name"],
            "subtitle": config["subtitle"],
            "department": config["department"],
            "email": config["email"],
            "issue_number": issue_number,
            "issue_date": issue_date,
            "layout_choice": layout_choice,
            "logo_uri": logo_uri,
            "logo_missing": not bool(logo_uri),
        },
        "headline": title,
        "standfirst": standfirst,
        "modules": modules,
    }


def render_html(data: dict[str, Any]) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html"]))
    template = env.get_template("base.html")
    css = STYLES_PATH.read_text(encoding="utf-8")
    return template.render(data=data, css=css)


def export_outputs(html: str, issue_number: str):
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    slug = safe_slug(issue_number or "boletin")
    html_path = OUTPUT_DIR / f"bitacora-{slug}.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path


def try_export_pdf(html: str, html_path: Path):
    try:
        from weasyprint import HTML

        pdf_path = html_path.with_suffix(".pdf")
        HTML(string=html, base_url=str(APP_DIR)).write_pdf(str(pdf_path))
        return pdf_path, "ok"
    except Exception as exc:
        return None, str(exc)


def main():
    st.set_page_config(page_title="Bitácora Sostenible", layout="wide")
    config = load_config()

    if "example_data" not in st.session_state:
        st.session_state.example_data = None

    st.sidebar.subheader("Carga rápida")
    if st.sidebar.button("Cargar ejemplo: Cetáceos"):
        st.session_state.example_data = load_example("bitacora_cetaceos_demo.json")
    if st.sidebar.button("Cargar ejemplo: Calidad del agua"):
        st.session_state.example_data = load_example("bitacora_agua_demo.json")
    st.title("Bitácora Sostenible · Constructor editorial")
    st.caption("MVP modular para crear boletines ambientales internos claros, visuales y exportables.")

    data = st.session_state.example_data or compose_data(config)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Guardar / Cargar")
    json_name = st.sidebar.text_input("Nombre de archivo JSON", value="bitacora_borrador.json")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        html = render_html(data)
        st.components.v1.html(html, height=1000, scrolling=True)

    with c2:
        if st.button("Exportar HTML"):
            html_path = export_outputs(html, data["meta"].get("issue_number", ""))
            st.success(f"HTML exportado en: {html_path}")

        if st.button("Exportar PDF"):
            html_path = export_outputs(html, data["meta"].get("issue_number", ""))
            pdf_path, status = try_export_pdf(html, html_path)
            if pdf_path:
                st.success(f"PDF exportado en: {pdf_path}")
            else:
                st.warning(f"No se pudo exportar PDF con WeasyPrint: {status}")

    with c3:
        json_blob = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button("Guardar JSON", data=json_blob.encode("utf-8"), file_name=json_name, mime="application/json")
        uploaded = st.file_uploader("Cargar JSON previo", type=["json"])
        if uploaded:
            loaded = json.loads(uploaded.read().decode("utf-8"))
            st.info("JSON cargado. Copia/pega campos clave o úsalo como referencia en esta versión MVP.")
            st.json(loaded)

    if data["meta"]["logo_missing"]:
        st.info("Logo institucional no encontrado en assets/logo_apa.png. Se usa placeholder discreto.")


if __name__ == "__main__":
    main()
