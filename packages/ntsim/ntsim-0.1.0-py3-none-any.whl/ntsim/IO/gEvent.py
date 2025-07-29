import itertools
import numpy as np
from ntsim.IO.gEventHeader import gEventHeader
from ntsim.IO.gProductionHeader import gProductionHeader
from ntsim.IO.gPrimaryHeader import gPrimaryHeader

class gEvent():
    def __init__(self):
        self._prodHeader    = gProductionHeader()
        self._primaryHeader = gPrimaryHeader()
        self._evtHeader     = gEventHeader()
        
        self._particles     = np.empty(shape=(0),dtype=int)
        self._tracks        = np.empty(shape=(0),dtype=int)
        self._hits          = np.empty(shape=(0),dtype=int)
        
        self._cloner_hits   = np.empty(shape=(0), dtype=int)
        self._cloner_shifts = np.empty(shape=(0,3), dtype=float)
        
        self._photons   = ()
    
    @property
    def ProductionHeader(self):
        return self._prodHeader
    
    @ProductionHeader.setter
    def ProductionHeader(self, opts):
        self._prodHeader.n_events_original = opts.n_events
#        self._prodHeader.n_events_cloned   = getattr(opts,opts.clone_generator_name+'.n_clones')
#        self._prodHeader.n_events_total    = self._prodHeader.n_events_original + self._prodHeader.n_events_cloned
#        if self.cloner.n_events:
#            self._prodHeader.n_events_total *= self.cloner.n_events
        
        self._prodHeader.primary_generator   = opts.primary_generator_name
        self._prodHeader.primary_propagators = opts.particle_propagator_name
        self._prodHeader.photon_propagator   = opts.photon_propagator_name
        self._prodHeader.ray_tracer          = opts.ray_tracer_name
#        self._prodHeader.cloner              = opts.clone_generator_name
        self._prodHeader.photons_n_scatterings = getattr(opts,self._prodHeader.photon_propagator+'.n_scatterings')
        self._prodHeader.photons_wave_range = getattr(opts,opts.medium_properties_name+'.waves_range')
#        self._prodHeader.cloner_accumulate_hits = getattr(opts,opts.clone_generator_name+'.accumulate_hits')
        self._prodHeader.medium_scattering_model = opts.medium_scattering_model_name
        self._prodHeader.medium_anisotropy = getattr(opts,opts.medium_properties_name+'.anisotropy')
      
    @property
    def EventHeader(self):
        return self._evtHeader
    
    @EventHeader.setter
    def EventHeader(self, opts):
        self._evtHeader.photons_sampling_weight = getattr(opts,opts.photon_suppression)
#        self._evtHeader.set_om_area_weight(self.get_om_area_weight())
    
    @property
    def particles(self):
        return self._particles
    
    @particles.setter
    def particles(self, new_particles):
        self._particles = np.append(self._particles, new_particles)
    
    def has_particles(self):
        return len(self._particles) > 0
    
    @property
    def tracks(self):
        return self._tracks
    
    @tracks.setter
    def tracks(self, new_tracks):
        self._tracks = np.append(self._tracks,new_tracks)
    
    def has_tracks(self):
        return len(self._tracks) > 0

    @property
    def photons(self):
        return self._photons
    
    @photons.setter
    def photons(self, new_photons):
        self._photons = itertools.chain(self._photons,new_photons)
    
    def has_photons(self):
        return len(self._photons) > 0
    
    @property
    def hits(self):
        return self._hits
    
    @hits.setter
    def hits(self, new_hits):
        self._hits = np.append(self._hits,new_hits)

    @property
    def cloner_hits(self):
        return self._cloner_hits
    
    @cloner_hits.setter
    def cloner_hits(self, new_hits):
        self._cloner_hits = np.append(self._cloner_hits,new_hits)

    @property
    def cloner_shifts(self):
        return self._cloner_shifts
    
    @cloner_shifts.setter
    def cloner_shifts(self, new_shifts):
        self._cloner_shifts = new_shifts   
    
    def has_hits(self):
        return len(self._hits) > 0
    
    def reset(self):
        self.__init__()