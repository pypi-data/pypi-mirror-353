from particle import Particle
import numpy as np

from ntsim.utils.report_timing import report_timing
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase

from ntsim.IO.gTracks import gTracks
from ntsim.IO.gParticles import gParticles
import ntsim.utils.systemofunits as units

from g4camp.g4camp import g4camp

from dataclasses import dataclass

class ParticlePropagator(PropagatorBase):
    arg_dict = {
        'skip_mode':               {'type': str, 'choices': ('cut','fraction'), 'default': 'cut', 'help': ''},
        'g4_casc_bounds_e':        {'type': float, 'nargs': 2, 'default': [10.,10_000.], 'help': 'set minimal/maximal energy to store cascade starters'},
        'g4_mode_custom_physlist': {'type': str, 'choices': ('all_phys','fast','em_cascade'), 'default': 'fast', 'help': ''},
        'g4_photon_suppression':   {'type': int, 'default': 1000, 'help': ''},
        'g4_random_seed':          {'type': int, 'default': 42, 'help': 'set random seed for Geant4'},
        'g4_detector_height':      {'type': float, 'default': 1360., 'help': 'set height (in meters) of cylindrical detector volume'},
        'g4_detector_radius':      {'type': float, 'default': 1000., 'help': 'set radius (in meters) of cylindrical detector volume'},
        'g4_rock_depth':           {'type': float, 'default': 200., 'help': 'set height (in meters) of cylindrical detector volume'},
        'g4_enable_cherenkov':     {'dest': 'g4_cherenkov', 'action': 'store_true', 'help': 'enable production of photons in Geant4'},
        'g4_save_process_name':    {'action': 'store_true', 'help': ''}
    }
    
    def configure(self, opts):
        
        super().configure(opts)
        
        self._g4prop = g4camp(mode_physlist=self.g4_mode_custom_physlist,optics=self.g4_enable_cherenkov,primary_generator='gun')
        self._g4prop.setPhotonSuppressionFactor(self.g4_photon_suppression)
        self._g4prop.setSkipMinMax(self.skip_mode,*self.g4_casc_bounds_e)
        self._g4prop.setRandomSeed(self.g4_random_seed)
        self._g4prop.setDetectorHeight(self.g4_detector_height)
        self._g4prop.setDetectorRadius(self.g4_detector_radius)
        self._g4prop.setRockDepth(self.g4_rock_depth)
        self._g4prop.SaveProcessName(self.g4_save_process_name)
        self._g4prop.configure()
        
        self.world_height_m    = self.g4_rock_depth+self.g4_detector_height
        self.position_shifts_m = 0.5*self.world_height_m-self.g4_rock_depth
    
    @report_timing
    def propagate(self,event):
        
        dataset_index = 0
        for gun_particles in event.particles:
            for n in range(gun_particles.get_n_gun_particles()):
                
                status = gun_particles.status[n]
                if status != 0:
                    continue
                
                pdgid     = gun_particles.pdgid[n]
                pos_m     = gun_particles.position_m[n]
                t_ns      = gun_particles.time_ns[n]
                direction = gun_particles.direction[n]
                Etot_GeV  = gun_particles.total_energy_GeV[n]
                if abs(pdgid) in (12,14,16):
                    mass_GeV = 0.
                else:
                    mass_GeV = Particle.from_pdgid(pdgid).mass*units.MeV/units.GeV # in GeV
                Ekin_GeV = Etot_GeV - mass_GeV
                
                self._g4prop.setGunParticle(pdgid)
                self._g4prop.setGunPosition(*pos_m, 'm')
                self._g4prop.setGunTime(t_ns, 'ns')
                self._g4prop.setGunDirection(*direction)
                self._g4prop.setGunEnergy(Ekin_GeV, 'GeV')
                
                run = next(self._g4prop.run(1))
                
                g4_cascade_starters = run.particles
                g4_tracks           = run.tracks
                
                if g4_cascade_starters.unique_data:
                
                    particles = gParticles(f'g4_cascade_starters_{dataset_index}')
                    
                    g4_cascade_starters_data = g4_cascade_starters.get_named_data()
                    
                    particle_uid             = g4_cascade_starters_data['uid']
                    particle_parent_uid      = g4_cascade_starters_data['parent_uid']
                    particle_pdgid           = g4_cascade_starters_data['pdgid']
                    particle_position_m      = np.column_stack([g4_cascade_starters_data['x_m'],
                                                                g4_cascade_starters_data['y_m'],
                                                                g4_cascade_starters_data['z_m']]
                                                               )
                    particle_time_ns         = g4_cascade_starters_data['t_ns']
                    particle_direction       = np.column_stack([g4_cascade_starters_data['dir_x'],
                                                                g4_cascade_starters_data['dir_y'],
                                                                g4_cascade_starters_data['dir_z']]
                                                               )
                    particle_tot_energy_GeV  = g4_cascade_starters_data['Etot_GeV']
                    status                   = np.zeros(g4_cascade_starters.unique_data)
                    
                    if self.g4_save_process_name:
                        particle_process_name = g4_cascade_starters_data['process_name']
                        particles.add_particles(particle_uid, particle_parent_uid, particle_pdgid, particle_position_m,
                                                particle_time_ns, particle_direction, particle_tot_energy_GeV,
                                                status,particle_process_name)
                    else:
                        particles.add_particles(particle_uid, particle_parent_uid, particle_pdgid, particle_position_m,
                                                particle_time_ns, particle_direction, particle_tot_energy_GeV,
                                                status)
                    
                    event.particles = particles
                
                if g4_tracks.unique_data:
                
                    tracks = gTracks(f'g4_tracks_{dataset_index}')
                    
                    g4_tracks_data = g4_tracks.get_named_data()
                    
                    track_uid             = g4_tracks_data['uid']
                    track_parent_uid      = g4_tracks_data['parent_uid']
                    track_pdgid           = g4_tracks_data['pdgid']
                    track_position_m      = np.column_stack([g4_tracks_data['x_m'],
                                                             g4_tracks_data['y_m'],
                                                             g4_tracks_data['z_m']]
                                                            )
                    track_time_ns         = g4_tracks_data['t_ns']
                    track_tot_energy_GeV  = g4_tracks_data['Etot_GeV']
                    track_step_length     = g4_tracks_data['step_length_m']
                    
                    if self.g4_save_process_name:
                        track_process_name = g4_tracks_data['process_name']
                        tracks.add_tracks(track_uid, track_parent_uid, track_pdgid,
                                      track_position_m, track_time_ns, track_tot_energy_GeV,
                                      track_step_length,track_process_name)
                    else:
                        tracks.add_tracks(track_uid, track_parent_uid, track_pdgid,
                                          track_position_m, track_time_ns, track_tot_energy_GeV,
                                          track_step_length)
                    
                    event.tracks = tracks
                
                if self._g4prop.optics:
                    self.logger_propagator.info('Genat4 Photon Generation (...)')
                    
                    from ntsim.IO.gPhotons import gPhotons
                    
                    photons = gPhotons(f'g4_photons')
                    
                    g4_photons      = run.photons
                    g4_photons_data = g4_photons.get_named_data()
                    
                    n_photons         = g4_photons.unique_data
                    photon_pos_m      = np.column_stack([g4_photons_data['x_m'],
                                                         g4_photons_data['y_m'],
                                                         g4_photons_data['z_m']])
                    photon_t_ns       = g4_photons_data['t_ns']
                    photon_direction  = np.column_stack([g4_photons_data['dir_x'],
                                                         g4_photons_data['dir_y'],
                                                         g4_photons_data['dir_z']])
                    photon_wl_nm      = g4_photons_data['wl_nm']
                    photon_parent_uid = g4_photons_data['parent_uid']
                    n_steps           = 1
                    
                    photons.add_photons(n_photons, n_steps, photon_pos_m, photon_t_ns,
                                        photon_direction, photon_wl_nm, photon_parent_uid,
                                        new_weight=self.g4_photon_suppression)
                    
                    event.photons = np.atleast_1d(photons)
                    
                dataset_index += 1