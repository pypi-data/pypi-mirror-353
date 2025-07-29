from .opram import opram_direction, opram_converse, opram_composition
from .rcc8 import compute_fuzzy_rcc8

class SpatialQueryEngine:
    """
    Provides spatial query answering for multiple fuzzy granular-ball regions,
    integrating OPRAm directional reasoning and fuzzy RCC-8 topology.
    """

    def __init__(self, balls, m=2, grid_resolution=100):
        """
        Args:
            balls: list of GranularBall instances
            m: granularity parameter for OPRAm (default 2 → 8 directions)
            grid_resolution: resolution for fuzzy RCC-8 and overlap computations
        """
        self.balls = balls
        self.m = m
        self.grid_resolution = grid_resolution

    def get_opram_relation(self, idxA, idxB):
        """
        Compute the OPRAm direction relation label between ball at index idxA and ball at index idxB.
        Returns a string like "r{i}" or None if indices are invalid.
        """
        if (idxA < 0 or idxA >= len(self.balls) or
            idxB < 0 or idxB >= len(self.balls)):
            return None
        A = self.balls[idxA]
        B = self.balls[idxB]
        return opram_direction(A.center, B.center, self.m)

    def get_rcc8_fuzzy(self, idxA, idxB):
        """
        Compute fuzzy RCC-8 membership dictionary between ball idxA and ball idxB.
        Returns a dict or None if indices are invalid.
        """
        if (idxA < 0 or idxA >= len(self.balls) or
            idxB < 0 or idxB >= len(self.balls)):
            return None
        A = self.balls[idxA]
        B = self.balls[idxB]
        return compute_fuzzy_rcc8(A, B, resolution=self.grid_resolution)

    def describe_pair(self, idxA, idxB):
        """
        Generate a combined description string of the OPRAm direction and fuzzy RCC-8 topology
        for ball idxA relative to ball idxB.
        """
        if (idxA < 0 or idxA >= len(self.balls) or
            idxB < 0 or idxB >= len(self.balls)):
            return "Index out of range."

        A = self.balls[idxA]
        B = self.balls[idxB]

        # Compute OPRAm direction
        dir_label = opram_direction(A.center, B.center, self.m)
        if dir_label is None:
            dir_desc = "Points coincide."
        else:
            dir_desc = f"OPRAm-{self.m} direction label: '{dir_label}'."

        # Compute fuzzy RCC-8
        rcc8 = compute_fuzzy_rcc8(A, B, resolution=self.grid_resolution)
        # Find the relation with highest membership
        max_rel, max_val = max(rcc8.items(), key=lambda x: x[1])
        topo_desc = f"Fuzzy RCC-8 top relation: '{max_rel}' with membership = {max_val:.4f}."

        return f"Ball {idxB} relative to Ball {idxA}: {dir_desc} {topo_desc}"

    def query_all_pairs(self):
        """
        Compute and return a list of description strings for all ordered pairs (i→j, i ≠ j).
        """
        descriptions = []
        n = len(self.balls)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                desc = self.describe_pair(i, j)
                descriptions.append(f"[{i}→{j}] {desc}")
        return descriptions
