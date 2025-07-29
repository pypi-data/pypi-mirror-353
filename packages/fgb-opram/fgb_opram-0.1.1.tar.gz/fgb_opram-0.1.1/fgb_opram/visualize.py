import math
import numpy as np
import matplotlib.pyplot as plt

from .granular_ball import EARTH_RADIUS_KM

def visualize_fuzzy_balls(ballA, ballB, resolution=200):
    """
    Visualize two fuzzy granular-ball regions (ballA, ballB) and their intersection in 2D.
    Uses contour plots for membership values of each ball and their overlap.
    """
    latA, lonA = ballA.center
    latB, lonB = ballB.center
    max_sigma = max(ballA.sigma, ballB.sigma)

    # Define bounding box ±3σ in degrees (approx)
    lat_offset = (3 * max_sigma) / 111.0
    lon_offset = (3 * max_sigma) / (111.0 * math.cos(math.radians((latA + latB) / 2.0) or 1.0))

    lat_min = min(latA, latB) - lat_offset
    lat_max = max(latA, latB) + lat_offset
    lon_min = min(lonA, lonB) - lon_offset
    lon_max = max(lonA, lonB) + lon_offset

    lat_vals = np.linspace(lat_min, lat_max, resolution)
    lon_vals = np.linspace(lon_min, lon_max, resolution)
    lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)

    membershipA = np.zeros_like(lat_grid)
    membershipB = np.zeros_like(lat_grid)
    intersection = np.zeros_like(lat_grid)

    for i in range(resolution):
        for j in range(resolution):
            coord = (lat_grid[i, j], lon_grid[i, j])
            muA = ballA.membership(coord)
            muB = ballB.membership(coord)
            membershipA[i, j] = muA
            membershipB[i, j] = muB
            intersection[i, j] = min(muA, muB)

    plt.figure(figsize=(10, 8))
    plt.contourf(lon_grid, lat_grid, membershipA, levels=50, cmap='Blues', alpha=0.4)
    plt.contourf(lon_grid, lat_grid, membershipB, levels=50, cmap='Reds', alpha=0.4)
    plt.contourf(lon_grid, lat_grid, intersection, levels=50, cmap='Greens', alpha=0.6)

    plt.scatter([lonA], [latA], c='blue', label='Ball A Center')
    plt.scatter([lonB], [latB], c='red', label='Ball B Center')

    plt.title("Fuzzy Granular-Ball Membership and Intersection")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True)
    plt.show()
