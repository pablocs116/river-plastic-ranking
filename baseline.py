"""
baseline.py
Reimplementation of the Meijer et al. (2021) probabilistic river plastic emission model.

Reference:
    Meijer, L.J.J., et al. (2021). More than 1000 rivers account for 80% of global
    riverine plastic emissions into the ocean. Science Advances, 7(18).
    DOI: 10.1126/sciadv.aaz5803
"""

import numpy as np
import pandas as pd


def compute_mismanaged_waste(population: pd.Series, waste_per_capita: pd.Series,
                              mismanagement_rate: pd.Series) -> pd.Series:
    """
    Compute mismanaged plastic waste per catchment (kg/year).

    Args:
        population: catchment population
        waste_per_capita: kg/person/day
        mismanagement_rate: fraction of waste that is mismanaged (0–1)

    Returns:
        mismanaged_plastic_kg_year: Series of mismanaged plastic waste per catchment
    """
    plastic_fraction = 0.12  # global average plastic fraction of MSW (Jambeck 2015)
    return population * waste_per_capita * 365 * plastic_fraction * mismanagement_rate


def mobilization_probability(runoff_mm: pd.Series, pop_density: pd.Series,
                              dist_to_waterway_km: pd.Series) -> pd.Series:
    """
    Estimate probability that mismanaged waste reaches a waterway.
    Follows Meijer 2021 logistic formulation.

    Args:
        runoff_mm: mean annual runoff in mm/year
        pop_density: population density per km²
        dist_to_waterway_km: distance from population centroid to nearest waterway

    Returns:
        p_mob: mobilization probability per catchment (0–1)
    """
    # Placeholder — implement Meijer eq. S1 from supplementary
    raise NotImplementedError("Implement from Meijer 2021 supplementary eq. S1")


def transport_probability(river_length_km: pd.Series, mean_discharge_m3s: pd.Series,
                           slope: pd.Series) -> pd.Series:
    """
    Estimate probability that plastic in waterway reaches ocean outfall.
    Follows Meijer 2021 formulation.

    Args:
        river_length_km: total river length from source to mouth
        mean_discharge_m3s: mean annual discharge
        slope: average river bed slope

    Returns:
        p_trans: transport probability per river (0–1)
    """
    raise NotImplementedError("Implement from Meijer 2021 supplementary eq. S2")


def compute_emission(mismanaged_waste: pd.Series, p_mob: pd.Series,
                     p_trans: pd.Series) -> pd.Series:
    """
    Final emission estimate at river outfall (kg/year).
    """
    return mismanaged_waste * p_mob * p_trans
