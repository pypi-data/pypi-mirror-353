# -*- coding: utf-8 -*-
# function: lazy import for scholar researches.


from scipy.spatial import ConvexHull

from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


from pybw.core import *

from bond_valence import (
    BVAnalyzer, 
    ClusterAnalyzer, 
    MobileCoulomb, 
    ElongatedSiteAnalyzer
)

from bond_valence.cluster import (
    init_3d_ax, 
    clean_ax, 
    rejust_ax_axis_length, 
    plot_hull, 
    plot_point_cloud, 
    plot_point_cloud_and_hull, 
    plot_ellipsoid, 
)


def get_site_symbols(site):
    """
    Parameters
    ----------
        site : 
            pymatgen Site.
    
    Returns
    -------
    List of site symbols.
    """
    elements = site.species.elements
    symbols = [i.element.symbol for i in elements]
    return symbols


def get_symmetrized_structure(stru, symprec=1e-3, return_analyzer=False):
    spg_analyzer = SpacegroupAnalyzer(stru, symprec=1e-3)
    sym_stru = spg_analyzer.get_symmetrized_structure()
    if return_analyzer:
        return sym_stru, analyzer
    else:
        return sym_stru


