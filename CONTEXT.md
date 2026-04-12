# Contexto de sesión — workload_app

## Qué estamos construyendo
Una CLI en Python que lee PDFs de órdenes de producción, extrae datos de material, y devuelve un score de carga laboral (low/medium/high/critical).

## Contexto del negocio
El usuario produce moldes EPS para casting de concreto de manholes. Cada PDF representa una orden con:
- **Puck** — la pieza principal. Tiene un campo `EPSØxH` con dos valores: diámetro y height. El height es lo que suma al total de material.
- **Holeformers** — piezas pequeñas (inlet/outlet). Aparecen en el campo `Connectionstype` con formato `525-21"Concrete` o `200-8"PVCSDR`. Solo importa el número y el tipo (PVC o Concrete).

**PDFs reales en:** `C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today\`
Los PDFs del día se ponen manualmente en la carpeta `today\` para simular la asignación de trabajo.

## Estructura de archivos
```
src/workload_app/
    __init__.py           — vacío, marca el paquete
    pdf_extract.py        — extrae datos del PDF (eps_height + holeformers)
    scoring.py            — recibe total mm y devuelve nivel de carga
    holeformers_chart.py  — tabla de conversión de holeformers
    cli.py                — coordina todo, muestra resultado
tests/
    explore_pdf.py        — archivo scratch para exploración/testing
```

## Estado actual de cada archivo

### scoring.py — COMPLETO
```python
def get_score(total):
    if total < 5000:        return "low"
    elif total < 8000:      return "medium"
    elif total < 10000:     return "high"
    else:                   return "critical"
```

### pdf_extract.py — COMPLETO
```python
import pdfplumber
import re

def extract_puck_data(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        for line in text.split("\n"):
            if "EPSØxH" in line:
                eps_height = float(line.split()[-1].replace(",", "."))
            if "Connectionstype" in line:
                holeformers = re.findall(r'(\d+)-\d+"\s*(PVC|Concrete)', line, re.IGNORECASE)
        return eps_height, holeformers
```
Devuelve tupla: `(849.5, [('600', 'Concrete'), ('200', 'PVC')])`

### holeformers_chart.py — COMPLETO
Diccionario `HOLEFORMERS_CHART` con clave `("size", "type")` → `{"length": mm, "per_sheet": n}`
- `length`: grosor de lámina EPS en mm
- `per_sheet`: cuántos holeformers salen de una lámina

Lógica de lotes: si necesito 5 holeformers de 300 PVC (per_sheet=4), necesito 2 láminas → 600mm aunque sobren 3.
Fórmula: `sheets = math.ceil(count / per_sheet)`, `material = sheets * length`

### cli.py — COMPLETO
```python
"""Procesa archivos PDF de órdenes entrantes y calcula métricas de EPS y holeformers."""

from pathlib import Path
from math import ceil
from workload_app.pdf_extract import extract_puck_data
from workload_app.scoring import get_score
from workload_app.holeformers_chart import HOLEFORMERS_CHART

today_dir = Path(r"C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today")
pdf_files = today_dir.glob("*.pdf")

def main():
    """Procesa los PDF de today y calcula el total de EPS y el score."""
    total_eps = 0
    total_pieces = 0
    holeformer_counts = {}

    for pdf_file in pdf_files:
        try:
            eps_height, holeformers = extract_puck_data(pdf_file)
            total_eps += eps_height
            total_pieces += 1
            for holeformer in holeformers:
                holeformer_counts[holeformer] = holeformer_counts.get(holeformer, 0) + 1
        except ValueError as e:
            print(f"Error processing {pdf_file}: {e}")

    for holeformer, count in holeformer_counts.items():
        chart = HOLEFORMERS_CHART.get(holeformer, {})
        if chart:
            per_sheet = chart["per_sheet"]
            sheets = ceil(count / per_sheet)
            total_eps += sheets * chart["length"]

    score = get_score(total_eps)
    print(f"Total EPS height: {total_eps}, Total pieces: {total_pieces}, Score: {score}")
    print(holeformer_counts)

if __name__ == "__main__":
    main()
```

Correr con: `cd src && ../.venv/Scripts/python.exe -m workload_app.cli`

## Próximo paso
Mejorar el output para que sea más legible (actualmente imprime raw).

## Pendiente para más adelante
- Cálculo de tiempo de torneado por tipo de puck (segunda dimensión del workload)
- UI con file picker (actualmente se usa carpeta `today\` como simulación)
- `pyproject.toml` y `pip install -e .` para resolver el problema de imports
- Convertir a `.exe` con PyInstaller (incluir GUI con tkinter)
- Compatibilidad con Windows 7: evaluar si usar Python 3.8 para generar el `.exe`
- Optimización de cortes: dado bloques de 2400mm y 20mm de exceso por corte, calcular orden de corte para minimizar desperdicio y número de bloques necesarios por día

## Reglas de colaboración
Ver `CLAUDE.md` para el enfoque de enseñanza completo.
