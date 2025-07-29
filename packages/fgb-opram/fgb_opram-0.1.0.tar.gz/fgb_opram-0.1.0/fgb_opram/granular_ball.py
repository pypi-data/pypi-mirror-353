import math

EARTH_RADIUS_KM = 6371.0

class GranularBall:

    def __init__(self, center, sigma):

        if not (isinstance(center, (tuple, list)) and len(center) == 2):
            raise ValueError("Center must be a tuple or list of (latitude, longitude).")
        if sigma < 0:
            raise ValueError("Sigma must be non-negative.")

        self.center = (float(center[0]), float(center[1]))
        self.sigma = float(sigma)

    def membership(self, coord):

        if not (isinstance(coord, (tuple, list)) and len(coord) == 2):
            raise ValueError("Input coordinate must be a tuple or list of (latitude, longitude).")

        lat1, lon1 = self.center
        lat2, lon2 = float(coord[0]), float(coord[1])

        # Convert degrees to radians for Haversine formula
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = phi2 - phi1
        delta_lambda = math.radians(lon2 - lon1)

        # Haversine formula to compute great-circle distance
        a = (math.sin(delta_phi / 2) ** 2 +
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        distance_km = EARTH_RADIUS_KM * c

        if self.sigma == 0:
            # Degenerate case: uniform membership
            return 1.0

        membership_value = math.exp(- (distance_km ** 2) / (2 * self.sigma ** 2))
        return max(0.0, min(1.0, membership_value))  # Ensure output is within [0, 1]
