import math

EARTH_RADIUS_KM = 6371.0

class GranularBall:

    def __init__(self, center, radius, sigma=0.1):

        if not (isinstance(center, (tuple, list)) and len(center) == 2):
            raise ValueError("Center must be a tuple or list of (latitude, longitude).")
        if radius < 0:
            raise ValueError("Radius must be non-negative.")
        if sigma < 0:
            raise ValueError("Sigma must be non-negative.")

        self.center = (float(center[0]), float(center[1]))
        self.radius = float(radius)
        self.sigma = float(sigma)

    def _haversine_distance_km(self, coord):

        lat1, lon1 = self.center
        lat2, lon2 = float(coord[0]), float(coord[1])

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = phi2 - phi1
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2) ** 2 +
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        return EARTH_RADIUS_KM * c

    def membership(self, coord):

        if not (isinstance(coord, (tuple, list)) and len(coord) == 2):
            raise ValueError("Input coordinate must be a tuple or list of (latitude, longitude).")

        distance_km = self._haversine_distance_km(coord)

        if distance_km <= self.radius:
            return 1.0
        elif self.sigma == 0:
            return 0.0
        else:
            decay = (distance_km - self.radius)
            membership_value = math.exp(- (decay ** 2) / (2 * self.sigma ** 2))
            return max(0.0, min(1.0, membership_value))
