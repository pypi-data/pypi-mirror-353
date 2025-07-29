import h5py
import numpy as np
import logging
log = logging.getLogger('h5Writer')
from ntsim.utils.report_timing import report_timing

from ntsim.IO.Base.WriterBase import WriterBase

class H5Writer(WriterBase):
    arg_dict = {
        'h5_output_file': {'type': str, 'default': 'events', 'help': 'output file name'},
        'h5_output_dir': {'type': str, 'default': 'h5_output', 'help': 'output directory name'},
        'h5_save_event': {'type': str, 'nargs': '+', 'choices': ['geometry','tracks','particles','photons','hits','clones'], 'default': ['geometry','tracks','particles','photons','hits','clones'],
                          'help': 'By default, all information about the event and geometry is recorded. When pointing specific values from choices, they and only they will be recorded'},
        'no_h5_save_event': {'type': str, 'nargs': '+', 'choices': ['geometry','tracks','particles','photons','hits','clones'], 'default': [],
                             'help': 'When pointing specific values from choices, they will not be written to the event or geometry'},
        'h5_save_header': {'type': str, 'nargs': '+', 'choices': ['prod_header','primary_header','event_header'], 'default': ['prod_header','primary_header','event_header'],
                           'help': 'By default, all information about the header is recorded. When pointing specific values from choices, they and only they will be recorded'},
        'no_h5_save_header': {'type': str, 'nargs': '+', 'choices': ['prod_header','primary_header','event_header'], 'default': [],
                              'help': 'When pointing specific values from choices, they will not be written to the header'}
    }
    
    '''
    arg_dict = {
        'h5_save_geometry': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save geometry'},
        'h5_save_medium_model': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save water model: absorption & scattering'},
        'h5_save_prod_header': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save production header'},
        'h5_save_event_header': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save event header'},
        'h5_save_primary_header': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save event header'},
        'h5_save_tracks': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save tracks'},
        'h5_save_particles': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save particles'},
        'h5_save_photons': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save photons'},
        'h5_save_hits': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save hits'},
        'h5_save_vertices': {'type': bool, 'default': False, 'action': 'BooleanOptionalAction', 'help': 'Boolean to save vertices'}
    }
    '''
    
    def open_file(self):
        import os
        if not os.path.exists(self.h5_output_dir):
            os.makedirs(self.h5_output_dir)
        log.info(f"open {self.h5_output_dir}/{self.h5_output_file}.h5")
        self.h5_file = h5py.File(f'{self.h5_output_dir}/{self.h5_output_file}.h5', 'w')

    def new_event(self, event_id):
        event_folder = f'event_{event_id}'
        if event_folder not in self.h5_file.keys():
            self.event_folder = self.h5_file.create_group(event_folder)
            if 'particles' in self.h5_save_event:
                self.event_folder.create_group('particles')
            if 'tracks' in self.h5_save_event:
                self.event_folder.create_group('tracks')
            if 'photons' in self.h5_save_event:
                self.event_folder.create_group('photons')
            if 'hits' in self.h5_save_event:
                self.event_folder.create_group('hits')
            if 'clones' in self.h5_save_event:
                self.event_folder.create_group('hits/cloner_hits')
        else:
            self.event_folder = self.h5_file[event_folder]
    
    @report_timing
    def write_data(self, data_list, folder_name):
        if len(data_list) == 0:
            log.info(f"no {folder_name} to write to {folder_name}")
        if folder_name in self.event_folder.keys():
            folder = self.event_folder[folder_name]
            for data in data_list:
                log.info(f"writing {folder_name} ({data.label})")
                folder.create_dataset(data.label, data=data.get_named_data())

    def write_cloner_shifts(self, shifts):
        if len(shifts):
            shifts_folder = f'cloner_shifts'
            log.info(f"writing cloner shifts")
            if 'photons' in self.event_folder.keys():
                photon_folder = self.event_folder['photons']
                if shifts_folder not in photon_folder.keys():
                    cloner_shifts_folder = photon_folder.create_group(shifts_folder)
                    shifts_type  = [('x_m',float),('y_m',float),('z_m',float)]
                    named_shifts = np.array([tuple(_) for _ in shifts], dtype = shifts_type)
                    cloner_shifts_folder.create_dataset(shifts_folder, data=named_shifts)
    
    def write_photons(self, photons, bunch_id):
        if 'photons' in self.h5_save_event:
            log.info(f"writing photon bunch #{bunch_id}")# ({list_of_bunches[0].label})")
            photon_folder = self.event_folder['photons']
            bunch_folder = photon_folder.create_group(f'photons_{bunch_id}')
            bunch_folder.create_dataset("weight",     data=photons.weight)
            bunch_folder.create_dataset("n_photons",  data=photons.n_photons)
            bunch_folder.create_dataset("n_steps",    data=photons.scattering_steps)
            bunch_folder.create_dataset("r",          data=photons.position_m)
            bunch_folder.create_dataset("t",          data=photons.time_ns)
            bunch_folder.create_dataset("dir",        data=photons.direction)
            bunch_folder.create_dataset("wavelength", data=photons.wavelength_nm)
            bunch_folder.create_dataset("progenitor", data=photons.progenitor)
            bunch_folder.create_dataset("ta",         data=photons.absorption_time_ns)
            bunch_folder.create_dataset("ts",         data=photons.scattering_time_ns)
            bunch_folder.attrs["label"] = photons.label
    
    def write_prod_header(self,productionHeader):
        if 'prod_header' in self.h5_save_header:
            g_header = self.h5_file.create_group('ProductionHeader')
            g_header.create_dataset("n_events_original",data=productionHeader.n_events_original)
            g_header.create_dataset("n_events_cloned",data=productionHeader.n_events_cloned)
            g_header.create_dataset("n_events_total",data=productionHeader.n_events_total)
            g_header.create_dataset("primary_generator",data=np.array([str.encode(productionHeader.primary_generator)]))
            g_header.create_dataset("primary_propagators",data=np.array([str.encode(productionHeader.primary_propagators)]))
            g_header.create_dataset("photon_propagator",data=np.array([str.encode(productionHeader.photon_propagator)]))
            g_header.create_dataset("ray_tracer",data=np.array([str.encode(productionHeader.ray_tracer)]))
            g_header.create_dataset("cloner",data=np.array([str.encode(productionHeader.cloner)]))
            g_header.create_dataset("photons_n_scatterings",data=productionHeader.photons_n_scatterings)
            g_header.create_dataset("photons_wave_range",data=productionHeader.photons_wave_range)
            g_header.create_dataset("cloner_accumulate_hits",data=productionHeader.cloner_accumulate_hits)
            g_header.create_dataset("medium_scattering_model",data=np.array([str.encode(productionHeader.medium_scattering_model)]))
            g_header.create_dataset("medium_anisotropy",data=productionHeader.medium_anisotropy)
    
    def write_primary_header(self,primHeader):
        if 'primary_header' in self.h5_save_header:
            g_header = self.h5_file.create_group('PrimaryHeader')
            g_header.create_dataset("name",data=primHeader.name)
            g_header.create_dataset("track",data=primHeader.track)
    
    def write_geometry(self, bounding_surfaces: np.ndarray, sensitive_detectors: np.ndarray):
        if 'geometry' in self.h5_save_event:
            geometry_folder = self.h5_file.create_group('geometry')
            geometry_folder.create_dataset('Geometry', data=sensitive_detectors)
            geometry_folder.create_dataset('Bounding_Surfaces', data=bounding_surfaces)
    
    def write_geometry_old(self,geometry):
        if 'geometry' in self.h5_save_event:
            geometry_folder = self.h5_file.create_group('geometry')
            geometry_folder.create_dataset('Season',data=geometry.season)
            geometry_folder.create_dataset('geom',data=geometry.geom)
            geometry_folder.create_dataset('bounding_box_subcluster',data=geometry.get_bounding_box_subcluster())
            geometry_folder.create_dataset('bounding_box_cluster',data=geometry.get_bounding_box_cluster())
            geometry_folder.create_dataset('det_normals',data=geometry.direction_OM)
    
    def write_event_header(self,evtHeader):
        if 'event_header' in self.h5_save_header:
            g_header = self.event_folder.create_group('event_header')
            g_header.create_dataset("photons_sampling_weight",data=evtHeader.photons_sampling_weight)
#            g_header.create_dataset("om_area_weight",data=evtHeader.om_area_weight)
            g_header.create_dataset("n_bunches",data=evtHeader.n_photon_bunches)
            g_header.create_dataset("n_photons_total",data=evtHeader.n_photons_total)
            g_header.create_dataset("event_weight",data=evtHeader.event_weight)
            return g_header
    
    @report_timing
    def close_file(self):
        try:
            log.info(f"close {self.h5_output_dir}/{self.h5_output_file}.h5")
            self.h5_file.close()
        except:
            log.warning("can not close h5 file properly")