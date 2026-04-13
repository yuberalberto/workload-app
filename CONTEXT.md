# Session context — workload_app

## What we are building
A Python CLI that reads KUKA robot `.src` files from production orders, extracts material data and milling trajectory, and returns a workload score (low/medium/high/critical) plus estimated milling time.

## Business context
The user produces EPS molds for concrete manhole casting. Each PDF represents an order with:
- **Puck** — the main piece. Has an `EPSØxH` field with two values: diameter and height. The height is what adds to the total material.
- **Holeformers** — small pieces (inlet/outlet). They appear in the `Connectionstype` field with format `525-21"Concrete` or `200-8"PVCSDR`. Only the number and type (PVC or Concrete) matter.

**Real files at:** `C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today\`
Each order produces one `.src` file and one PDF — they always come together. The `.src` is the primary source since it contains all needed data (EPS height, holeformers, milling trajectory) and is required for production.
The day's files are placed manually in the `today\` folder to simulate work assignment.

## File structure
```
src/workload_app/
    __init__.py           — empty, marks the package
    src_extract.py        — extracts data from the .src file (eps_height, holeformers, milling trajectory)
    scoring.py            — receives total mm and returns workload level
    holeformers_chart.py  — holeformer conversion table
    cli.py                — coordinates everything, displays result
tests/
    explore_pdf.py        — scratch file for exploration/testing
docs/
    investigacion_kuka_tiempo.md  — research doc: milling time estimation method
    EPS_2_25252_PD2_A_20250910061714.src  — sample .src file for reference
```

## Current state of each file

### pdf_extract.py — DEPRECATED
Replaced by `src_extract.py`. Do not use.

### extract_piece_data.py — IN PROGRESS
Replaces `pdf_extract.py`. Function `extract_puck_data(file_path)` reads `.src` files and returns `(eps_height, holeformers, trajectory)`.

Current state:
- `eps_height` ✓ — extracted using flag pattern on `;QRS#17=EPS Height` / `;QRS#18=value`
- `holeformers` — partially done. Regex captures matches but normalization of type is pending:
  - Raw capture: `('200', 'PVC SDR 35 Cut Back')` 
  - Should normalize to: `('200', 'PVC Cut Back')`, `('200', 'PVC')`, or `('525', 'Concrete')`
  - Next step: loop through matches with `for`, normalize tipo, append to list
  - In `cli.py`: when looking up chart, strip Cut Back → use `"PVC"` as key
- `trajectory` — not started yet (0.0 placeholder)

Milling time formula: `time = trajectory / 60.7` (mm/s, deduced from timed reference MHDR11)

### scoring.py — COMPLETE
```python
def get_score(total):
    if total < 5000:        return "low"
    elif total < 8000:      return "medium"
    elif total < 10000:     return "high"
    else:                   return "critical"
```

### pdf_extract.py — COMPLETE
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
Returns tuple: `(849.5, [('600', 'Concrete'), ('200', 'PVC')])`

### holeformers_chart.py — COMPLETE
Dictionary `HOLEFORMERS_CHART` with key `("size", "type")` → `{"length": mm, "per_sheet": n}`
- `length`: EPS sheet thickness in mm
- `per_sheet`: how many holeformers come from one sheet

Batch logic: if I need 5 holeformers of 300 PVC (per_sheet=4), I need 2 sheets → 600mm even if 3 are left over.
Formula: `sheets = math.ceil(count / per_sheet)`, `material = sheets * length`

### cli.py — COMPLETE
```python
"""Processes incoming order PDF files and calculates EPS and holeformer metrics."""

from pathlib import Path
from math import ceil
from workload_app.pdf_extract import extract_puck_data
from workload_app.scoring import get_score
from workload_app.holeformers_chart import HOLEFORMERS_CHART

today_dir = Path(r"C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today")
pdf_files = today_dir.glob("*.pdf")

def main():
    """Processes today's PDFs and calculates total EPS and score."""
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

Run with: `cd src && ../.venv/Scripts/python.exe -m workload_app.cli`

## Next step
Complete `extract_piece_data.py`:
1. Normalize holeformer types — loop through `matches`, normalize tipo to `"PVC"`, `"PVC Cut Back"`, or `"Concrete"`, append `(size, tipo)` to list
2. Extract trajectory — sum Euclidean distances between consecutive `LIN` points (X, Y, Z)
3. Update `cli.py` to import from `extract_piece_data` instead of `pdf_extract`, handle Cut Back in chart lookup, and display milling time

## Backlog
- Milling time display in workload report (trajectory / 60.7 mm/s, already researched in docs/)
- UI with file picker (currently using `today\` folder as simulation)
- `pyproject.toml` and `pip install -e .` to solve the imports issue
- Convert to `.exe` with PyInstaller (include GUI with tkinter)
- Windows 7 compatibility: evaluate using Python 3.8 to generate the `.exe`
- Cut optimization: given 2400mm blocks and 20mm excess per cut, calculate cut order to minimize waste and number of blocks needed per day

## Collaboration rules
See `CLAUDE.md` for the complete teaching approach.
