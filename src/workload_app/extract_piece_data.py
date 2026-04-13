"""Extracts data from KUKA .src files."""

import re


def extract_puck_data(file_path):
    """Extracts the EPS height, holeformers, and trajectory from a given plain text file (.src)"""
    with open(file_path, encoding="utf-8") as f:
        eps_height = 0.0
        holeformers = []
        trajectory = 0.0
        found = False
        for line in f:
            if found:
                eps_height = float(line.split("=")[1])
                found = False  # Reset for next search

            if "EPS Height" in line:
                found = True

            matches = re.findall(
                r'(\d+)-\d+"\s*(PVC(?:.*Cut Back)?|Concrete)', line, re.IGNORECASE
            )
            
            if matches:
                holeformers += matches

        return eps_height, holeformers, trajectory
