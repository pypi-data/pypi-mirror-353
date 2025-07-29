import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from .granular_ball import GranularBall
from .fuzzy_overlap import fuzzy_overlap
from .rcc8 import compute_fuzzy_rcc8
from .opram import opram_direction, opram_converse, opram_composition
from .visualize import visualize_fuzzy_balls
from .spatial_query_engine import SpatialQueryEngine

class StdoutRedirector:
    """
    Redirects all stdout text into a Tkinter ScrolledText widget.
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass  # No-op

def run_spatial_example():
    """
    Example routine that creates sample GranularBall instances,
    computes memberships, overlaps, OPRAm directions, RCC-8 relations,
    and prints results into the GUI text area. Also displays a Matplotlib plot.
    """
    # Sample points (latitude, longitude)
    points = [
        (37.5665, 126.9780),  # Seoul City Hall
        (37.5651, 126.9895),  # Gwanghwamun
    ]

    # Generate two GranularBall instances with sigma = 0.5 km
    balls = [GranularBall(center=pt, sigma=0.5) for pt in points]

    # Print ball information
    for i, ball in enumerate(balls):
        print(f"Ball {i}: Center = ({ball.center[0]:.4f}, {ball.center[1]:.4f}), sigma = {ball.sigma:.4f} km")

    # Test membership of a specific point
    test_point = (37.5675, 126.9810)
    for i, ball in enumerate(balls):
        mu = ball.membership(test_point)
        print(f"Ball {i} membership of test point = {mu:.4f}")

    # Compute fuzzy overlap, OPRAm direction, RCC-8 relations
    if len(balls) >= 2:
        overlap_val = fuzzy_overlap(balls[0], balls[1], resolution=200)
        print(f"Fuzzy overlap between Ball 0 and Ball 1 = {overlap_val:.4f}")

        direction_01 = opram_direction(balls[0].center, balls[1].center, m=2)
        print(f"OPRAm-2 direction from Ball 0 to Ball 1: '{direction_01}'")

        rcc8_relations = compute_fuzzy_rcc8(balls[0], balls[1], resolution=200)
        print("Fuzzy RCC-8 relations between Ball 0 and Ball 1:")
        for rel, val in rcc8_relations.items():
            print(f"  {rel}: {val:.4f}")

        converse_10 = opram_converse(direction_01, m=2)
        composed = opram_composition(direction_01, converse_10, m=2)
        print(f"Converse of '{direction_01}' is '{converse_10}', composition gives '{composed}'")

        # Visualize the two balls and their intersection
        visualize_fuzzy_balls(balls[0], balls[1], resolution=200)

    # Use SpatialQueryEngine to print all pairwise relations
    engine = SpatialQueryEngine(balls, m=2, grid_resolution=150)
    all_relations = engine.query_all_pairs()
    print("\nAll pairwise spatial relations:")
    for desc in all_relations:
        print(desc)

def main():
    """
    Create a Tkinter window, redirect stdout and stderr to the text widget,
    then run run_spatial_example() after GUI initialization.
    """
    root = tk.Tk()
    root.title("FGB-OPRAm Spatial Reasoning Output")

    text_area = ScrolledText(root, wrap=tk.WORD, width=100, height=30)
    text_area.pack(fill=tk.BOTH, expand=True)

    sys.stdout = StdoutRedirector(text_area)
    sys.stderr = StdoutRedirector(text_area)

    root.after(100, run_spatial_example)
    root.mainloop()

if __name__ == "__main__":
    main()
