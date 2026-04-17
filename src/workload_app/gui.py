"""Tkinter GUI for the workload analysis tool."""

import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from workload_app.cli import analyze
from workload_app.version import __version__

def _config_path():
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    return base / "config.json"

def _load_config():
    try:
        return json.loads(_config_path().read_text())
    except Exception:
        return {}

def _save_config(data):
    try:
        _config_path().write_text(json.dumps(data))
    except Exception:
        pass


class WorkloadApp(tk.Tk):
    """Main application window for the workload analyzer."""

    def __init__(self):
        super().__init__()
        self.title(f"OMNI - Milling Workload Analyzer v{__version__}  |  by Yuber Mina")
        self.resizable(True, True)
        self.state("zoomed")

        self.folder_path = None
        self.all_files = []          # All .src files in the selected folder
        self.checkbox_vars = {}      # filename -> BooleanVar (checked state)
        self.selected_files = []     # Files confirmed to the selection panel

        self._build_menu()
        self._build_ui()

        last_folder = _load_config().get("last_folder")
        if last_folder and Path(last_folder).is_dir():
            self._load_folder(Path(last_folder))

    def _build_menu(self):
        menubar = tk.Menu(self)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title("About OMNI")
        win.resizable(False, False)
        text = (
            f"OMNI - Milling Workload Analyzer v{__version__}\n"
            "\n"
            "About this tool:\n"
            "Reads KUKA robot .src files, extracts EPS height,\n"
            "holeformer data, and milling trajectory to calculate\n"
            "workload effort level and estimated milling time per shift.\n"
            "\n"
            "Future ideas:\n"
            "  - Cut optimization: minimize EPS block waste (FFD algorithm)\n"
            "  - Calibrate milling speed with more real measurements\n"
            "  - UI improvements\n"
            "\n"
            "Developed by Yuber Mina"
        )
        tk.Label(win, text=text, justify="left", padx=20, pady=20).pack()
        tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 15))

    def _build_ui(self):
        # --- Top bar: folder button + filter fields ---
        top_frame = tk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        tk.Button(top_frame, text="Select folder", command=self._select_folder).pack(side="left")
        tk.Button(top_frame, text="↺ Refresh", command=self._refresh_folder).pack(side="left", padx=(4, 0))
        self.folder_label = tk.Label(top_frame, text="No folder selected", anchor="w")
        self.folder_label.pack(side="left", padx=10)
        self.count_label = tk.Label(top_frame, text="", anchor="w", fg="gray")
        self.count_label.pack(side="left")

        tk.Label(top_frame, text="Job #:").pack(side="left", padx=(10, 2))
        self.job_var = tk.StringVar()
        self.job_var.trace_add("write", lambda *_: self._apply_filter())
        tk.Entry(top_frame, textvariable=self.job_var, width=10).pack(side="left", padx=(0, 8))

        tk.Label(top_frame, text="Structure:").pack(side="left", padx=(0, 2))
        self.structure_var = tk.StringVar()
        self.structure_var.trace_add("write", lambda *_: self._apply_filter())
        tk.Entry(top_frame, textvariable=self.structure_var, width=14).pack(side="left")

        # --- Middle: checkbox list + selected list side by side ---
        middle_frame = tk.Frame(self)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: available files with checkboxes
        left_outer = tk.LabelFrame(middle_frame, text="Available files")
        left_outer.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Select all / Deselect all buttons inside left panel
        left_btns = tk.Frame(left_outer)
        left_btns.pack(fill="x")
        tk.Button(left_btns, text="Select all", command=self._select_all).pack(side="left", padx=2, pady=2)
        tk.Button(left_btns, text="Deselect all", command=self._deselect_all).pack(side="left", padx=2, pady=2)

        # Scrollable canvas for checkboxes
        canvas = tk.Canvas(left_outer, borderwidth=0)
        scrollbar = tk.Scrollbar(left_outer, orient="vertical", command=canvas.yview)
        self.checkbox_frame = tk.Frame(canvas)
        self.checkbox_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.checkbox_frame.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self._canvas = canvas  # Keep reference to bind checkbuttons on rebuild

        # Buttons in between
        btn_frame = tk.Frame(middle_frame)
        btn_frame.pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add →", command=self._add_checked).pack(pady=5)
        tk.Button(btn_frame, text="← Remove", command=self._remove_selected).pack(pady=5)
        tk.Button(btn_frame, text="Clear", command=self._clear_selected).pack(pady=5)

        # Right: confirmed selection
        self.right_frame = tk.LabelFrame(middle_frame, text="Selected files (0)")
        self.right_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.selected_listbox = tk.Listbox(self.right_frame, height=12)
        self.selected_listbox.pack(fill="both", expand=True, side="left")
        scrollbar_right = tk.Scrollbar(self.right_frame, command=self.selected_listbox.yview)
        scrollbar_right.pack(side="right", fill="y")
        self.selected_listbox.config(yscrollcommand=scrollbar_right.set)
        self.selected_listbox.bind("<MouseWheel>", lambda e: self.selected_listbox.yview_scroll(-1 * (e.delta // 120), "units"))

        # --- Shift selector + Run button ---
        run_frame = tk.Frame(self)
        run_frame.pack(pady=5)

        tk.Label(run_frame, text="Shift:").pack(side="left", padx=(0, 4))
        self.shift_var = tk.IntVar(value=8)
        tk.Radiobutton(run_frame, text="8h", variable=self.shift_var, value=8).pack(side="left")
        tk.Radiobutton(run_frame, text="9h", variable=self.shift_var, value=9).pack(side="left", padx=(0, 10))
        tk.Button(
            run_frame, text="Run analysis", command=self._run_analysis, bg="#4CAF50", fg="white"
        ).pack(side="left")

        # --- Report area ---
        report_frame = tk.LabelFrame(self, text="Report")
        report_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.report_text = tk.Text(
            report_frame, height=14, state="disabled", font=("Courier", 10)
        )
        self.report_text.pack(fill="both", expand=True, side="left")
        scrollbar_report = tk.Scrollbar(report_frame, command=self.report_text.yview)
        scrollbar_report.pack(side="right", fill="y")
        self.report_text.config(yscrollcommand=scrollbar_report.set)

        # --- Footer ---
        tk.Label(
            self, text="Developed by Yuber Mina",
            fg="gray", font=("TkDefaultFont", 8)
        ).pack(side="bottom", pady=(0, 4))

    def _normalize(self, text):
        """Removes dots, dashes and spaces for loose structure matching."""
        return text.replace(".", "").replace("-", "").replace(" ", "").lower()

    def _refresh_folder(self):
        if self.folder_path:
            self._load_folder(self.folder_path)

    def _select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self._load_folder(Path(folder))
        _save_config({"last_folder": str(self.folder_path)})

    def _load_folder(self, path):
        self.folder_path = path
        self.folder_label.config(text=str(self.folder_path))
        self.all_files = sorted(self.folder_path.glob("*.src"), key=lambda f: f.name)
        self.count_label.config(text=f"({len(self.all_files)} .src files found)")
        self.checkbox_vars = {}
        self.selected_files = []
        self.selected_listbox.delete(0, "end")
        self._apply_filter()

    def _apply_filter(self):
        job_query = self.job_var.get().strip().lower()
        structure_query = self._normalize(self.structure_var.get())

        # Rebuild checkbox list for matching files
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()

        for f in self.all_files:
            parts = f.stem.split("_")  # EPS_2_{job}_{structure}_{letter}_{date}
            job = parts[2].lower() if len(parts) > 2 else ""
            structure = self._normalize(parts[3]) if len(parts) > 3 else ""

            if job_query in job and structure_query in structure:
                if f.name not in self.checkbox_vars:
                    self.checkbox_vars[f.name] = tk.BooleanVar()
                cb = tk.Checkbutton(
                    self.checkbox_frame,
                    text=f.name,
                    variable=self.checkbox_vars[f.name],
                    anchor="w"
                )
                cb.pack(fill="x")
                cb.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    def _select_all(self):
        for name, var in self.checkbox_vars.items():
            # Only select visible (filtered) checkboxes
            if any(w.cget("text") == name for w in self.checkbox_frame.winfo_children()):
                var.set(True)

    def _deselect_all(self):
        for var in self.checkbox_vars.values():
            var.set(False)

    def _update_selected_count(self):
        count = len(self.selected_files)
        self.right_frame.config(text=f"Selected files ({count})")

    def _add_checked(self):
        already_added = []
        for name, var in self.checkbox_vars.items():
            if var.get():
                path = self.folder_path / name
                if path in self.selected_files:
                    already_added.append(name)
                else:
                    self.selected_files.append(path)
                    self.selected_listbox.insert("end", name)
                var.set(False)

        self._update_selected_count()

        if already_added:
            messagebox.showwarning(
                "Already in selection",
                "These files were already selected:\n\n" + "\n".join(already_added)
            )

    def _remove_selected(self):
        for i in reversed(self.selected_listbox.curselection()):
            self.selected_files.pop(i)
            self.selected_listbox.delete(i)
        self._update_selected_count()

    def _clear_selected(self):
        self.selected_files = []
        self.selected_listbox.delete(0, "end")
        self._update_selected_count()

    def _run_analysis(self):
        if not self.selected_files:
            messagebox.showwarning(
                "No files selected", "Add at least one .src file to the selection."
            )
            return
        report = analyze(self.selected_files, shift=self.shift_var.get())
        self.report_text.config(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("end", report)
        self.report_text.config(state="disabled")


def main():
    app = WorkloadApp()
    app.mainloop()


if __name__ == "__main__":
    main()
