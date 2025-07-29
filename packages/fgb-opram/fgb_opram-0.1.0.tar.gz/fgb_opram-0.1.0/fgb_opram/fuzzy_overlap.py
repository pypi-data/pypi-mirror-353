import math
import numpy as np

from .granular_ball import EARTH_RADIUS_KM

def fuzzy_intersection_and_union(ballA, ballB, resolution=100):
    """
    Compute approximate intersection, union, and self-areas for two fuzzy granular balls
    using a grid-based sampling approach.

    Returns:
        intersection_value: sum of min(μA, μB) * cell_area
        union_value: sum of max(μA, μB) * cell_area
        areaA_value: sum of μA * cell_area
        areaB_value: sum of μB * cell_area
    """
    latA, lonA = ballA.center
    latB, lonB = ballB.center
    max_sigma = max(ballA.sigma, ballB.sigma)

    # Bounding box: ±3σ around both centers (approx)
    lat_offset = (3 * max_sigma) / 111.0
    lon_offset = (3 * max_sigma) / (111.0 * math.cos(math.radians((latA + latB) / 2.0) or 1.0))

    lat_min = min(latA, latB) - lat_offset
    lat_max = max(latA, latB) + lat_offset
    lon_min = min(lonA, lonB) - lon_offset
    lon_max = max(lonA, lonB) + lon_offset

    lat_vals = np.linspace(lat_min, lat_max, resolution)
    lon_vals = np.linspace(lon_min, lon_max, resolution)

    # Approximate cell dimensions in kilometers
    dlat = (lat_max - lat_min) / (resolution - 1)
    dlon = (lon_max - lon_min) / (resolution - 1)

    intersection = 0.0
    union = 0.0
    areaA = 0.0
    areaB = 0.0

    for phi in lat_vals:
        lat_rad = math.radians(phi)
        cell_area = (EARTH_RADIUS_KM * math.radians(dlat)) * (EARTH_RADIUS_KM * math.radians(dlon) * math.cos(lat_rad))
        for lam in lon_vals:
            muA = ballA.membership((phi, lam))
            muB = ballB.membership((phi, lam))
            intersection += min(muA, muB) * cell_area
            union += max(muA, muB) * cell_area
            areaA += muA * cell_area
            areaB += muB * cell_area

    return intersection, union, areaA, areaB

def fuzzy_overlap(ballA, ballB, resolution=100):
    """
    Estimate fuzzy overlap between two granular balls and normalize to [0,1].
    overlap_value = intersection / union (or 0 if union == 0).
    """
    intersection, union, _, _ = fuzzy_intersection_and_union(ballA, ballB, resolution)
    return (intersection / union) if union > 0 else 0.0
