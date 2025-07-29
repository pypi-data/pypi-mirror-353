# FGB-OPRAm (Fuzzy Granular-Ball and OPRAm Spatial Query Answering)

**Package Name:** `fgb-opram`  
**Version:** 0.1.31  
**Author:** Bongjae Kwon <bongjae.kwon@snu.ac.kr>  
**GitHub:** https://github.com/bongjaekwon/FGB-OPRAm-SQAUE  

## Overview
The `fgb-opram` package integrates the Fuzzy Granular-Ball model with OPRAm (Oriented Point Relation Algebra modulo m) directional calculus 
and fuzzy RCC-8 (Region Connection Calculus) topology. It enables robust spatial query answering under uncertainty.

### Key Features
- **GranularBall**: A class representing a fuzzy spatial region using a Gaussian membership function.
- **fuzzy_overlap** and **compute_fuzzy_rcc8**: Functions to compute fuzzy intersection, union, and RCC-8 topological relations between two regions.
- **opram_direction**, **opram_converse**, **opram_composition**: OPRAm-based directional reasoning utilities.
- **SpatialQueryEngine**: Engine that produces pairwise spatial relations (direction + topology) among multiple fuzzy regions.
- **visualize_fuzzy_balls**: A Matplotlib-based function to visualize two fuzzy regions and their overlap.
- **GUI Example**: A Tkinter-based window that redirects stdout to a scrolling text widget, demonstrating the entire pipeline.

## Installation

### From PyPI
```bash
pip install fgb-opram
```

### From Source (Development Mode)
```bash
git clone https://github.com/bongjaekwon/FGB-OPRAm-SQAUE.git
cd FGB-OPRAm-SQAUE
pip install .
```

## Usage Example

```python
from fgb_opram import GranularBall, opram_direction, compute_fuzzy_rcc8

# Create two fuzzy regions
ballA = GranularBall(center=(37.5651, 126.9895), radius=1, sigma=0.5)
ballB = GranularBall(center=(37.5670, 126.9800), radius=1, sigma=0.5)

# Compute membership of a point
muA = ballA.membership((37.5675, 126.9810))
muB = ballB.membership((37.5675, 126.9810))
print(f"Ball A Membership: {muA:.4f}, Ball B Membership: {muB:.4f}")

# Compute fuzzy RCC-8 topological relations
rcc8_relations = compute_fuzzy_rcc8(ballA, ballB)
print("Fuzzy RCC-8 memberships:", rcc8_relations)

# Compute OPRAm direction (m=2 → 8 directions)
direction_label = opram_direction(ballA.center, ballB.center, m=2)
print("OPRAm-2 direction from A to B:", direction_label)
```

## GUI Example

After installation, run the following command in your terminal to launch the GUI example:

```bash
fgb_opram_gui
```

This will open a Tkinter window that prints spatial reasoning results (memberships, overlap, RCC-8, OPRAm, etc.) 
into a scrolling text widget and displays a Matplotlib plot of two fuzzy regions.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
