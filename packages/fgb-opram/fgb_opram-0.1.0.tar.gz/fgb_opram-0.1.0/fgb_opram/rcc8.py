from .fuzzy_overlap import fuzzy_intersection_and_union

def compute_fuzzy_rcc8(ballA, ballB, resolution=100, epsilon=1e-6):
    """
    Compute fuzzy RCC-8 memberships between two granular balls.
    Relations: DC, EC, PO, TPP, NTPP, EQ, TPPi, NTPPi.

    Returns:
        A dictionary mapping each RCC-8 relation to its membership in [0,1].
    """
    intersection, union, areaA, areaB = fuzzy_intersection_and_union(ballA, ballB, resolution)

    # Compute fuzzy inclusion A ⊆ B and B ⊆ A
    inclusionAtoB = intersection / areaA if areaA > 0 else 0.0
    inclusionBtoA = intersection / areaB if areaB > 0 else 0.0

    # EQ (Equal): both inclusions close to 1
    eq_membership = min(inclusionAtoB, inclusionBtoA)

    # TPP (Tangential Proper Part): A ⊂ B but not equal
    tpp_membership = max(inclusionAtoB - eq_membership, 0.0)

    # NTPP (Non-Tangential Proper Part): approximate as half of TPP
    ntpp_membership = tpp_membership * 0.5

    # TPPi (Inverse of TPP): B ⊂ A but not equal
    tppi_membership = max(inclusionBtoA - eq_membership, 0.0)

    # NTPPi (Inverse of NTPP)
    ntppi_membership = tppi_membership * 0.5

    # PO (Partial Overlap): intersection but no inclusion
    po_membership = max((intersection / union) - max(inclusionAtoB, inclusionBtoA), 0.0) if union > 0 else 0.0

    # DC (Disconnected): almost no intersection
    dc_membership = 1.0 - (intersection / (union + epsilon))

    # EC (Externally Connected): small intersection near boundaries
    ec_membership = max(min(1.0 - intersection / (union + epsilon), min(inclusionAtoB, inclusionBtoA)), 0.0)

    # Clip all memberships to [0,1]
    rcc8 = {
        'DC': min(max(dc_membership, 0.0), 1.0),
        'EC': min(max(ec_membership, 0.0), 1.0),
        'PO': min(max(po_membership, 0.0), 1.0),
        'TPP': min(max(tpp_membership, 0.0), 1.0),
        'NTPP': min(max(ntpp_membership, 0.0), 1.0),
        'TPPi': min(max(tppi_membership, 0.0), 1.0),
        'NTPPi': min(max(ntppi_membership, 0.0), 1.0),
        'EQ': min(max(eq_membership, 0.0), 1.0)
    }

    return rcc8
