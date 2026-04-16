# Session context — workload_app

## What we are building
A Python CLI/GUI that reads KUKA robot `.src` files from production orders, extracts material data and milling trajectory, and returns a workload effort level (low/medium/high/critical) plus estimated milling time.

## Business context
The user produces EPS molds for concrete manhole casting. Each `.src` file represents an order with:
- **Puck** — the main piece. Has an `EPSØxH` field with two values: diameter and height. The height is what adds to the total material.
- **Holeformers** — small pieces (inlet/outlet). They appear in the `Connectionstype` field with format `525-21"Concrete` or `200-8"PVCSDR`. Only the number and type (PVC or Concrete) matter.

**Real files at:** `C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today\`
Each order produces one `.src` file and one PDF — they always come together. The `.src` is the primary source since it contains all needed data (EPS height, holeformers, milling trajectory) and is required for production.

## File structure
```
src/workload_app/
    __init__.py           — empty, marks the package
    extract_piece_data.py — extracts data from the .src file (eps_height, holeformers, trajectory)
    scoring.py            — receives total mm and shift hours, returns effort level
    holeformers_chart.py  — holeformer conversion table
    cli.py                — analyze() function + main() CLI entry point
    gui.py                — tkinter GUI (MVP complete)
tests/
    explore_pdf.py        — scratch file for exploration/testing
docs/
    investigacion_kuka_tiempo.md  — research doc: milling time estimation method
    optimizacion_cortes.md        — research doc: FFD algorithm for cut optimization
```

## Current state of each file

### extract_piece_data.py — COMPLETE
Function `extract_puck_data(file_path)` reads `.src` files and returns `(eps_height, holeformers, trajectory)`.
- `eps_height` ✓ — extracted using flag pattern on `;QRS#17=EPS Height` / `;QRS#18=value`
- `holeformers` ✓ — normalized to `("size", "PVC")`, `("size", "PVC Cut Back")`, or `("size", "Concrete")`
- `trajectory` ✓ — sum of Euclidean distances between consecutive LIN points (X, Y, Z)

Milling time formula: `time = trajectory / 56.45` (mm/s — averaged from MHDR11 and MHDA02 real measurements)

### scoring.py — COMPLETE
```python
THRESHOLDS = {
    8: (5000, 8000, 10000),
    9: (6000, 9000, 11000),
}

def get_effort(total, shift=8):
    low, medium, high = THRESHOLDS.get(shift, THRESHOLDS[8])
    ...
```
Returns: `"low"`, `"medium"`, `"high"`, or `"critical"`.

### holeformers_chart.py — COMPLETE
Dictionary `HOLEFORMERS_CHART` with key `("size", "type")` → `{"length": mm, "per_sheet": n}`
- Keys use `"PVC"` and `"Concrete"` only (no Cut Back variant)
- In cli.py, Cut Back holeformers are looked up using `"PVC"` key

### cli.py — COMPLETE
- `analyze(src_files, shift=8)` — processes list of Path objects, returns report string
- `main()` — CLI entry point using `today\` folder

### gui.py — MVP COMPLETE
Tkinter GUI with:
- Folder selector
- Job # and Structure filters (dynamic, normalized matching)
- Checkbox list of available .src files with Select all / Deselect all
- Selected files panel with live count
- Shift selector (8h / 9h radio buttons)
- Run analysis button
- Report display area

Run GUI with: `cd src && ../.venv/Scripts/python.exe -m workload_app.gui`
Run CLI with: `cd src && ../.venv/Scripts/python.exe -m workload_app.cli`

## Next step
Package as `.exe` for Windows 7 deployment:
1. Install Python 3.8 on dev machine
2. Create new virtualenv with Python 3.8
3. Install dependencies
4. Generate `.exe` with PyInstaller

## Backlog
- Cut optimization: FFD algorithm — given 2400mm blocks and 20mm excess per cut, calculate cut order to minimize waste (research done in docs/optimizacion_cortes.md)
- Calibrate milling speed constant (56.45 mm/s) with more real measurements
- Remember last used folder — save folder path to a config file (.json) next to the .exe so it loads automatically on next launch
- UI improvements as needed
