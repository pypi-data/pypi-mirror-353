import math

def qualitative_bearing(pointA, pointB):
    """
    Compute the bearing (in degrees) from pointA to pointB.
    0° corresponds to North, increasing clockwise.
    Returns None if the two points coincide.
    """
    lat1, lon1 = pointA
    lat2, lon2 = pointB

    if (lat1 == lat2) and (lon1 == lon2):
        return None  # Same point

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360) % 360

    return bearing

def opram_direction(pointA, pointB, m):
    """
    Compute the OPRAm direction relation between two points with granularity m.
    360° is divided into 4*m equally sized sectors. Returns label "r{i}" where i in [0, 4m-1].
    Returns None if points coincide.
    """
    bearing = qualitative_bearing(pointA, pointB)
    if bearing is None:
        return None

    num_sectors = 4 * m
    interval = 360.0 / num_sectors
    index = int(((bearing + (interval / 2.0)) % 360) // interval)
    return f"r{index}"

def opram_converse(relation_label, m):
    """
    Compute the converse (inverse) of an OPRAm relation:
    converse(r_i) = r_{(i + 2m) mod (4m)}.
    Returns None if input is None or invalid.
    """
    if relation_label is None:
        return None
    try:
        idx = int(relation_label[1:])
    except (ValueError, IndexError):
        return None

    num_sectors = 4 * m
    j = (idx + 2 * m) % num_sectors
    return f"r{j}"

def opram_composition(rel1, rel2, m):
    """
    Compute a simplified composition of two OPRAm relations:
    (i + j) mod (4m). Returns None if either relation is None or invalid.
    """
    if (rel1 is None) or (rel2 is None):
        return None
    try:
        i = int(rel1[1:])
        j = int(rel2[1:])
    except (ValueError, IndexError):
        return None

    num_sectors = 4 * m
    k = (i + j) % num_sectors
    return f"r{k}"
