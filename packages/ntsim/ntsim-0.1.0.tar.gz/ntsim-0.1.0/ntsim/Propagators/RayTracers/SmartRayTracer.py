from ntsim.Propagators.RayTracers.rt_utils                   import ray_tracer
from ntsim.utils.report_timing                               import report_timing
from ntsim.Propagators.Base.PropagatorBase                   import PropagatorBase
from ntsim.IO.gHits                                          import gHits
import numpy as np

class SmartRayTracer(PropagatorBase):

    def configure(self, bboxes_depth, detectors_depth, effects, effects_options, effects_names):
        self.bboxes_depth = bboxes_depth
        self.detectors_depth = detectors_depth
        self.effects = effects
        self.effects_options = effects_options
        self.effects_names = effects_names
    
    @report_timing
    def propagate(self, event, photons) -> None:
        hits_list = ray_tracer(photons.position_m,photons.time_ns,photons.wavelength_nm,photons.weight,photons.absorption_time_ns,
                               self.bboxes_depth,self.detectors_depth,self.effects,self.effects_options)
        
        if len(event.hits) == 0:
            hits = gHits(f'Hits')
            if len(hits_list):
                hits.add_hits(*list(map(list, zip(*hits_list))),new_effects_names=self.effects_names)
            event.hits = hits
        else:
            if len(hits_list):
                event.hits[0].add_hits(*list(map(list, zip(*hits_list))),new_effects_names=self.effects_names)
        
        # Cloner
        if len(event.cloner_shifts) != 0:
            n_clones = len(event.cloner_shifts)
            accumulation_label = event.ProductionHeader.cloner_hits_accumulation
            for clone_id in range(n_clones):
                cloner_hits_list = ray_tracer(photons.position_m + event.cloner_shifts[clone_id], photons.time_ns,photons.wavelength_nm,photons.weight,photons.absorption_time_ns,
                                            self.bboxes_depth,self.detectors_depth,self.effects,self.effects_options)
                # accumulation on
                if accumulation_label == True:
                    if len(event.cloner_hits) == 0:
                        cloner_hits = gHits(f'ClonerHits_all')
                        if len(cloner_hits_list):
                            cloner_hits.add_hits(*list(map(list, zip(*cloner_hits_list))),new_effects_names=self.effects_names)
                        event.cloner_hits = cloner_hits
                    else:
                        if len(cloner_hits_list):
                            event.cloner_hits[0].add_hits(*list(map(list, zip(*cloner_hits_list))),new_effects_names=self.effects_names)
                # accumulation off
                else: 
                    if len(event.cloner_hits) < n_clones:
                        cloner_hits = gHits(f'ClonerHits_{clone_id}')
                        if len(cloner_hits_list):
                            cloner_hits.add_hits(*list(map(list, zip(*cloner_hits_list))),new_effects_names=self.effects_names)
                        event.cloner_hits = cloner_hits
                    else:
                        if len(cloner_hits_list):
                            event.cloner_hits[clone_id].add_hits(*list(map(list, zip(*cloner_hits_list))),new_effects_names=self.effects_names)
