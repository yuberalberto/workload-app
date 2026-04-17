"""Holeformer lookup table by diameter and material."""

HOLEFORMERS_CHART = {
    ("100", "PVC"): {"length": 250, "per_sheet": 9},
    ("135", "PVC"): {"length": 250, "per_sheet": 9},
    ("150", "PVC"): {"length": 250, "per_sheet": 9},
    ("200", "PVC"): {"length": 300, "per_sheet": 9},
    ("250", "PVC"): {"length": 300, "per_sheet": 9},
    ("300", "PVC"): {"length": 300, "per_sheet": 4},
    ("375", "PVC"): {"length": 325, "per_sheet": 4},
    ("450", "PVC"): {"length": 325, "per_sheet": 4},
    ("525", "PVC"): {"length": 325, "per_sheet": 1},
    ("600", "PVC"): {"length": 340, "per_sheet": 1},
    ("675", "PVC"): {"length": 400, "per_sheet": 1},
    ("750", "PVC"): {"length": 425, "per_sheet": 1},
    ("300", "Concrete"): {"length": 300, "per_sheet": 4},
    ("375", "Concrete"): {"length": 300, "per_sheet": 4},
    ("450", "Concrete"): {"length": 325, "per_sheet": 1},
    ("525", "Concrete"): {"length": 430, "per_sheet": 1},
    ("600", "Concrete"): {"length": 430, "per_sheet": 1},
    ("675", "Concrete"): {"length": 430, "per_sheet": 1},
    ("750", "Concrete"): {"length": 450, "per_sheet": 1},
    ("825", "Concrete"): {"length": 525, "per_sheet": 1},
}
