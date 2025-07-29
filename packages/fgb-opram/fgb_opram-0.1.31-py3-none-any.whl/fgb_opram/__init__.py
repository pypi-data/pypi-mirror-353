""" 
FGB-OPRAm Package: Fuzzy Granular-Ball and OPRAm Spatial Reasoning Modules
Version: 0.1.31
Author: Bongjae Kwon <bongjae.kwon@snu.ac.kr>
"""

__version__ = "0.1.31"

from .granular_ball import GranularBall
from .fuzzy_overlap import fuzzy_overlap, fuzzy_intersection_and_union
from .rcc8 import compute_fuzzy_rcc8
from .opram import opram_direction, opram_converse, opram_composition
from .spatial_query_engine import SpatialQueryEngine
from .visualize import visualize_fuzzy_balls
from .gui import run_spatial_example, main  # GUI entry points
