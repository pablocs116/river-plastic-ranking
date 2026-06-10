"""Legacy import — use src.models.baseline instead."""
from src.models.baseline import (
    compute_emission,
    compute_mismanaged_waste,
    mobilization_probability,
    transport_to_ocean,
    transport_to_river,
)

__all__ = [
    "compute_mismanaged_waste",
    "mobilization_probability",
    "transport_to_river",
    "transport_to_ocean",
    "compute_emission",
]
