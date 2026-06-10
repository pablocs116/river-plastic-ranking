"""
baseline.py
Reimplementation of the Meijer et al. (2021) probabilistic river plastic emission model.

Reference:
    Meijer, L.J.J., et al. (2021). More than 1000 rivers account for 80% of global
    riverine plastic emissions into the ocean. Science Advances, 7(18).
    DOI: 10.1126/sciadv.aaz5803

Model structure:
    E_i = W_i * P(M) * P(R) * P(O)

    W_i   = mismanaged plastic waste in catchment i (kg/year)
    P(M)  = mobilization probability (precipitation + wind)
    P(R)  = probability of reaching a river (overland transport)
    P(O)  = probability of reaching the ocean (in-river transport)
"""

import numpy as np
import pandas as pd

PLASTIC_FRACTION_MSW = 0.12
WIND_MAX_MS = 32.7
RAIN_MAX_MM_YR = 3000.0

PARAMS_S9 = {
    "epsilon": 0.01,
    "tau": 0.005,
    "theta": 0.07,
    "iota": 0.01,
    "kappa": 0.001,
    "mu": 0.95,
}

LAND_USE_ROUGHNESS = {
    0: 0.95,
    1: 0.90,
    2: 0.80,
    3: 0.50,
    4: 0.30,
    5: 0.25,
    6: 0.20,
    7: 0.15,
    8: 0.10,
    9: 0.10,
    10: 0.08,
    11: 0.07,
    12: 0.06,
    13: 0.05,
    14: 0.04,
    15: 0.03,
    16: 0.03,
    17: 0.40,
    18: 0.02,
    19: 0.02,
    20: 0.35,
    21: 0.01,
    22: 0.01,
}


def compute_mismanaged_waste(
    population: pd.Series,
    waste_per_capita: pd.Series,
    mismanagement_rate: pd.Series,
) -> pd.Series:
    return population * waste_per_capita * 365 * PLASTIC_FRACTION_MSW * mismanagement_rate


def mobilization_probability(
    runoff_mm: pd.Series, pop_density: pd.Series, dist_to_waterway_km: pd.Series,
    wind_speed_ms: pd.Series | None = None, precipitation_mm_yr: pd.Series | None = None,
) -> pd.Series:
    """
    P(M) = P(P) + P(W)  (union of precipitation and wind mobilization)

    If precipitation/wind are not provided, falls back to a logistic approximation
    using runoff, population density, and distance to waterway (simplified formulation
    used when only catchment-level aggregates are available).
    """
    if precipitation_mm_yr is not None and wind_speed_ms is not None:
        p_precip = (precipitation_mm_yr / RAIN_MAX_MM_YR).clip(0, 1)
        p_wind = (wind_speed_ms / WIND_MAX_MS).clip(0, 1)
        p_mob = (p_precip + p_wind).clip(0, 1)
        return p_mob

    k = 0.005
    r = 0.01
    x = runoff_mm * k + pop_density * r - dist_to_waterway_km * 0.5
    return 1 / (1 + np.exp(-x + 5))


def transport_to_river(
    land_use_classes: pd.Series,
    slope: pd.Series,
    dist_to_river_km: pd.Series,
    params: dict | None = None,
) -> pd.Series:
    """
    P(R) = (sum_i nu_i * (epsilon * s_i + tau) / n) ^ D_Land

    When only catchment-level aggregates are available, uses mean values.
    """
    p = params or PARAMS_S9
    nu = land_use_classes.map(LAND_USE_ROUGHNESS).fillna(0.01)
    cell_prob = nu * (p["epsilon"] * slope + p["tau"])
    mean_prob = cell_prob.clip(0, 1)
    p_river = mean_prob ** dist_to_river_km.clip(lower=0.1)
    return p_river.clip(0, 1)


def transport_to_ocean(
    strahler_order: pd.Series,
    discharge_m3s: pd.Series,
    river_length_km: pd.Series,
    params: dict | None = None,
) -> pd.Series:
    """
    P(O) = (sum_i (theta * SO_i + iota) * (kappa * Q_i + mu) / n) ^ D_River
    """
    p = params or PARAMS_S9
    so_term = p["theta"] * strahler_order + p["iota"]
    q_term = p["kappa"] * discharge_m3s + p["mu"]
    cell_prob = so_term * q_term
    mean_prob = cell_prob.clip(0, 1)
    p_ocean = mean_prob ** river_length_km.clip(lower=0.1)
    return p_ocean.clip(0, 1)


def compute_emission(
    mismanaged_waste: pd.Series,
    p_mob: pd.Series,
    p_river: pd.Series,
    p_ocean: pd.Series,
) -> pd.Series:
    return mismanaged_waste * p_mob * p_river * p_ocean
