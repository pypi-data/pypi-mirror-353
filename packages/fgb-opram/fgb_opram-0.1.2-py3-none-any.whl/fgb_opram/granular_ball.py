import numpy as np

# Earth's radius in kilometers
EARTH_RADIUS_KM = 6371.0
# fgb_opram/granular_ball.py

class GranularBall:
    """
    Represents a fuzzy granular ball defined by a center, radius, and fuzziness parameter sigma.
    Supports computation of fuzzy membership degrees and spatial inclusion queries.
    """

    def __init__(self, center, radius, sigma=0.1):
        """
        Initialize a fuzzy granular ball.

        Args:
            center (tuple): Coordinates (x, y) of the ball center.
            radius (float): Radius of the ball.
            sigma (float, optional): Fuzziness parameter controlling membership decay. Default is 0.1.
        """
        self.center = tuple(center)
        self.radius = float(radius)
        self.sigma = float(sigma)

    def membership(self, point):
        """
        Compute fuzzy membership degree of a point relative to the ball.

        Membership is 1 at the center and decreases smoothly towards zero near the boundary,
        controlled by the fuzziness parameter sigma.

        Args:
            point (tuple): 2D point (x, y)

        Returns:
            float: Membership degree in [0, 1]
        """
        distance = np.linalg.norm(np.array(point) - np.array(self.center))
        if distance > self.radius + 3 * self.sigma:
            return 0.0
        else:
            # Using a smooth Gaussian-like decay outside radius
            if distance <= self.radius:
                return 1.0
            else:
                diff = distance - self.radius
                return np.exp(- (diff ** 2) / (2 * self.sigma ** 2))

    def contains(self, point, threshold=0.5):
        """
        Determine if a point is contained in the ball given a membership threshold.

        Args:
            point (tuple): 2D point (x, y)
            threshold (float): Membership cutoff for inclusion (default 0.5)

        Returns:
            bool: True if membership ≥ threshold, False otherwise
        """
        return self.membership(point) >= threshold
