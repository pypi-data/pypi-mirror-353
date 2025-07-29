from dataclasses import dataclass

@dataclass
class gEventHeader:
    n_photons_total : int = 0
    n_photon_bunches : int = 0
    photons_sampling_weight : int = 1
    event_weight : float = 1.