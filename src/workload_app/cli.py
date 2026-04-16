"""Processes incoming KUKA .src files and calculates workload metrics."""

from pathlib import Path
from math import ceil
from workload_app.extract_piece_data import extract_puck_data
from workload_app.scoring import get_effort
from workload_app.holeformers_chart import HOLEFORMERS_CHART

MILLING_SPEED = 56.45  # mm/s — average deduced from MHDR11 and MHDA02 real measurements

today_dir = Path(r"C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today")


def analyze(src_files, shift=8):
    """Analyzes a list of .src file paths and returns a workload report string."""
    total_eps = 0
    total_pieces = 0
    total_trajectory = 0.0
    holeformer_counts = {}
    errors = []

    for src_file in src_files:
        try:
            eps_height, holeformers, trajectory = extract_puck_data(src_file)
            total_eps += eps_height + 20  # Add 20mm as a cutting allowance for the puck
            total_trajectory += trajectory
            total_pieces += 1
            for holeformer in holeformers:
                holeformer_counts[holeformer] = holeformer_counts.get(holeformer, 0) + 1
        except ValueError as e:
            errors.append(f"Error processing {src_file.name}: {e}")

    for holeformer, count in holeformer_counts.items():
        key = (holeformer[0], "PVC") if "PVC" in holeformer[1] else holeformer
        chart = HOLEFORMERS_CHART.get(key, {})
        if chart:
            per_sheet = chart["per_sheet"]
            sheets = ceil(count / per_sheet)
            total_eps += sheets * chart["length"]

    effort = get_effort(total_eps, shift)
    required_blocks = ceil(total_eps / 2400)  # Each block is 2400mm length
    milling_seconds = total_trajectory / MILLING_SPEED
    milling_hours = int(milling_seconds // 3600)
    milling_minutes = int((milling_seconds % 3600) // 60)

    holeformers_list = ""
    for holeformer, count in holeformer_counts.items():
        holeformers_list += f"  {holeformer[0]} {holeformer[1]} : {count}\n"

    report = (
        "=============================\n"
        "        WORKLOAD REPORT\n"
        "=============================\n"
        f"Orders processed : {total_pieces}\n"
        f"Shift            : {shift}h\n"
        f"Effort           : {effort}\n"
        f"Milling time     : {milling_hours}h {milling_minutes}min\n"
        "-----------------------------\n"
        f"Total EPS        : {total_eps} mm\n"
        f"Blocks needed    : {required_blocks}\n"
        "-----------------------------\n"
        "Holeformers:\n"
        f"{holeformers_list}"
        "=============================\n"
    )

    if errors:
        report += "\nErrors:\n" + "\n".join(errors)

    return report


def main():
    """Processes today's .src files and prints the workload report."""
    src_files = list(today_dir.glob("*.src"))
    print(analyze(src_files))


if __name__ == "__main__":
    main()
