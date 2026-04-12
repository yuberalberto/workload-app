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

            total_eps += eps_height + 20  # Add 20mm as a cutting allowance for the puck
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
    required_blocks = ceil(total_eps / 2400)  # Where each block is 2400mm length

    holeformers_list = ""
    for holeformer, count in holeformer_counts.items():
        holeformers_list += (
            f"{holeformer[0]} {holeformer[1]} : {count}\n               "
        )

    # print(
    #     f"Total EPS height: {total_eps}, Total pieces: {total_pieces}, Score: {score}, Required blocks: {required_blocks}"
    # )
    # print(holeformer_counts)

    print(
        f"""
            =============================
                WORKLOAD REPORT
            =============================
            Orders processed : {total_pieces}
            Effort           : {score}
            -----------------------------
            Total EPS processed: {total_eps} mm
            Blocks needed    : {required_blocks}
            -----------------------------
            Holeformers counted:
               {holeformers_list}
            =============================
        """
    )


if __name__ == "__main__":
    main()
