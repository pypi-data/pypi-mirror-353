import logging
log = logging.getLogger('NuPropagator')
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase
from ntsim.IO.gTracks import gTracks
import nupropagator.flux.Flux as flux
import numpy as np

class nuPropagator(PropagatorBase):
    def __init__(self):
        self.module_type = "propagator"
        self.propagator = None
        self.name = 'nuPropagator'

    def configure(self,opts):
        from nupropagator import NuPropagator 
        self.propagator = NuPropagator.NuPropagator(opts)
        self.propagator.prepare_propagation()

    def propagate(self,event):
        tracks = gTracks("nu_tracks")
        ev = event.particles[0].data[0]
        self.info = self.propagator.get_dragging()
        info = np.array([[-1,ev['gen'],ev['pdgid'],ev['x_m'],ev['y_m'],ev['z_m'],ev['t_ns'],ev['Etot_GeV']]])
        tracks.add_tracks(info)
        self.info = self.propagator.get_dragging()
        ev = event.particles[0].data[1]
        info = np.array([[-1,ev['gen'],ev['pdgid'],ev['x_m'],ev['y_m'],ev['z_m'],ev['t_ns'],ev['Etot_GeV']]])
        tracks.add_tracks(info)
        print(info)
        event.tracks = tracks