# Machining time estimation — KUKA Robot (EPS)

## Goal

Calculate the time the robot takes to machine each piece from KUKA `.src` programs, without access to the controller.

## Method

The `.src` files are plain text with XYZ coordinates for each `LIN` movement.

1. Calculate the **Euclidean distance** between consecutive points → total trajectory length.
2. The speed **is not in the files** (it lives in `QRS_SPEED_INIT()`), so it is deduced using a timed file as reference.

**Timed reference:** MHDR11 → 243.9 m in 67 minutes = **60.7 mm/s**

## Results

| File | Trajectory | Estimated time |
|---|---|---|
| MHDR11 *(timed reference)* | 243.9 m | 67 min (real) |
| SA03 | 169.4 m | ~46 min |
| SA02 | 94.7 m | ~26 min |

## Limitations

- The speed is deduced, not read directly. If `QRS_SPEED_INIT` varies between programs, the estimate loses precision.
- PTP movements (rapid positioning) are not included in the calculation — in these files there are only 2 per program, minimal impact.

## Conclusion

The approximation is valid for production planning.

For greater precision, obtain the `QRS_SPEED_INIT.src` file from the controller.

## Next step (implementation)

When the calculation is programmed in Python:
- Parse the `LIN` points from the `.src` file
- Calculate Euclidean distance between consecutive points
- Use **60.7 mm/s** as base speed (or make it configurable if it varies per program)
