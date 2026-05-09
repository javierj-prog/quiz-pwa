# Bitácora Sostenible (MVP · Iteración 2)

Aplicación Streamlit para generar boletines ambientales internos con enfoque editorial modular, sin IA generativa.

## 1) Ejecutar en local (paso a paso)

1. Crear entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r bitacora_sostenible/requirements.txt
   ```
3. Iniciar la app:
   ```bash
   streamlit run bitacora_sostenible/app.py
   ```
4. Abrir la URL que muestra Streamlit (normalmente `http://localhost:8501`).

## 2) Logo institucional

- Ruta esperada del logo real: `bitacora_sostenible/assets/logo_apa.png`.
- La app lo carga automáticamente en cabecera.
- Si el archivo no existe, se mantiene la maqueta con placeholder discreto.

## 3) Cargar ejemplos de uso

En la barra lateral hay dos botones:
- **Cargar ejemplo: Cetáceos**
- **Cargar ejemplo: Calidad del agua**

También puedes cargar manualmente:
- `bitacora_sostenible/examples/bitacora_cetaceos_demo.json`
- `bitacora_sostenible/examples/bitacora_agua_demo.json`

## 4) Exportación

- Exportación principal: **HTML** (siempre disponible).
- Exportación **PDF**: best effort con WeasyPrint. Puede requerir dependencias nativas del sistema.
- Todos los resultados se guardan en `bitacora_sostenible/outputs/`.

## 5) Estructura

```
bitacora_sostenible/
├─ app.py
├─ config/config.yaml
├─ assets/logo_apa.png
├─ examples/
│  ├─ bitacora_cetaceos_demo.json
│  └─ bitacora_agua_demo.json
├─ templates/base.html
├─ templates/modules.html
├─ styles/bitacora.css
├─ outputs/
├─ requirements.txt
└─ README.md
```
