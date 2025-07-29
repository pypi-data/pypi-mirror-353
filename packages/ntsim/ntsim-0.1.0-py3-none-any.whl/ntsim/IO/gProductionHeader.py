from dataclasses import dataclass, field

@dataclass
class gProductionHeader:
    n_events_original : int = 0
    n_events_cloned : int = 0
    n_events_total : int = 0
    primary_generator : str = ''
    primary_propagators : str = ''
    photon_propagator : str = ''
    ray_tracer : str = ''
    cloner : str = ''
    photons_n_scatterings : int = 0
    photons_wave_range : list = field(default_factory=list)
    cloner_accumulate_hits : int = -1
    medium_scattering_model : str = ''
    medium_anisotropy : float = -2
