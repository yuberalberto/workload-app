# Cut optimization — Research

## Problem

Given a set of pieces with known lengths, determine:
1. The cut order that minimizes material waste
2. How many blocks are needed for the day

## Parameters

- **Block length:** 2400mm
- **Excess per cut:** 20mm (added to each piece)
- **Started block:** there may be a block already in use on the machine, with less than 2400mm of available length

## Recommended algorithm: First Fit Decreasing (FFD)

A classic **bin packing** algorithm — how to fit pieces into containers minimizing wasted space.

### Steps
1. Sort all pieces from largest to smallest
2. For each piece, find the first block where it fits (`piece_length + 20mm`)
3. If it doesn't fit in any existing block, open a new block
4. The started block on the machine is added first with its real available length

### Advantages
- Simple to implement
- Gives results close to optimal in practice
- Handles the started block case well

### Limitations
- Does not guarantee the mathematical optimum (exact algorithms exist for that, but are slower and more complex)
- For the daily work volume of this project, FFD is sufficient

## References
- [Bin packing problem — Wikipedia](https://en.wikipedia.org/wiki/Bin_packing_problem)
- [First Fit Decreasing — explanation](https://en.wikipedia.org/wiki/First-fit-decreasing_bin_packing)
