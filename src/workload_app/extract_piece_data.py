"""Extracts data from KUKA .src files."""

import re
import math


def extract_puck_data(file_path):
    """Extracts the EPS height, holeformers, and trajectory from a given plain text file (.src)"""
    with open(file_path, encoding="utf-8") as f:
        eps_height = 0.0
        holeformers = []
        trajectory = 0.0
        found = False
        prev_point = None
        for line in f:
            if found:
                eps_height = float(line.split("=")[1].replace(",", "."))
                found = False  # Reset for next search

            if "EPS Height" in line:
                found = True

            matches = re.findall(
                r'(\d+)-\d+"\s*(PVC(?:.*Cut Back)?|Concrete)', line, re.IGNORECASE
            )

            for size, raw_type in matches:
                if "Cut Back" in raw_type:
                    tipo = "PVC Cut Back"
                elif "PVC" in raw_type.upper():
                    tipo = "PVC"
                else:
                    tipo = "Concrete"
                holeformers.append((size, tipo))

            if line.startswith("LIN"):
                coords = re.findall(r'[XYZ]\s*([\d.\-]+)', line)
                if len(coords) >= 3:
                    x = float(coords[0].replace(",", "."))
                    y = float(coords[1].replace(",", "."))
                    z = float(coords[2].replace(",", "."))
                    if prev_point is not None:
                        dx = x - prev_point[0]
                        dy = y - prev_point[1]
                        dz = z - prev_point[2]
                        trajectory += math.sqrt(dx**2 + dy**2 + dz**2)
                    prev_point = (x, y, z)

        return eps_height, holeformers, trajectory
