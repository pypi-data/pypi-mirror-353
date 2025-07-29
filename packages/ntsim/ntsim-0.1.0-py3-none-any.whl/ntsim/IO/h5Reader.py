import h5py
from ntsim.IO.gEvent import gEvent
from ntsim.IO.gPhotons import gPhotons
from ntsim.random import rng
import pandas as pd
import numpy as np
import logging
from collections import Counter
log = logging.getLogger('h5Reader')

class h5Reader:
    def __init__(self,n_photons_max=500000):
        self.n_photons_max = n_photons_max
        self.gEvent = gEvent()
        self.read_event_header_flag         = True
        self.read_event_photons_flag        = True
        self.read_event_hits_flag           = True
        self.read_event_tracks_flag         = True
        self.change_flag                    = False
        self.read_event_particles_flag      = True
        # pointers to read objects
        self.geometry     = None
        # folders with read objects
        self.evtHeader_folder = None
        self.gEvent.photons_folder   = None
        self.gEvent.particles_folder = None
        self.gEvent.tracks_folder    = None
        self.gEvent.hits_folder      = None
        # current uid counter
        self.uid_current = 0 # can be changed externaly

    def configure(self,opts):
        self.opts = opts

    def set_read_event_header(self,flag=True):
        self.read_event_header_flag = flag

    def set_read_event_photons(self,flag=True):
        self.read_event_photons_flag = flag

    def set_read_event_hits(self,flag=True):
        self.read_event_hits_flag = flag

    def set_read_event_tracks(self,flag=True):
        self.read_event_tracks_flag = flag

    def set_read_event_particles(self,flag=True):
        self.read_event_particles_flag = flag

    def open(self,filename):
        self.filename = filename
        self.h5_file =  h5py.File(filename, 'r')
        self.read_prod_header()
        self.make_uid()

    def make_uid(self):
        self.uid = {}
        for event in range(0,self.gEvent.prodHeader.n_events_original):
            event_folder = self.get_event_folder(event)
            hit_folder = event_folder['hits']
            if "all_hits" in hit_folder.keys():
                self.uid[event] = (event,None)
            else:
                for clone_id in range(self.gEvent.prodHeader.n_events_cloned):
                    uid = self.gEvent.prodHeader.n_events_cloned*event+clone_id
                    self.uid[uid] = (event,clone_id)
        self.uid_current = 0 # can be changed externaly

    # def make_uid(self):
    #     self.uid = {}
    #     for event in range(0,self.gEvent.prodHeader.n_events_original):
    #         if self.gEvent.prodHeader.n_events_cloned:
    #             for clone_id in range(self.gEvent.prodHeader.n_events_cloned):
    #                 uid = self.gEvent.prodHeader.n_events_cloned*event+clone_id
    #                 self.uid[uid] = (event,clone_id)
    #         else:
    #             self.uid[event] = (event,None)
    #     self.uid_current = 0 # can be changed externaly

    def next(self):
        if self.uid_current > self.gEvent.prodHeader.n_events_total-1:
            log.warning(f'attemp to read event {self.uid_current} with total = {self.gEvent.prodHeader.n_events_total}')
            return self.gEvent
        self.uid_current +=1
        self.change_flag = False
        return self.read_event()

    def change(self):
        if self.uid_current > self.gEvent.prodHeader.n_events_total-1:
            log.warning(f'attemp to read event {self.uid_current} with total = {self.gEvent.prodHeader.n_events_total}')
            return self.gEvent
        self.change_flag = True
        return self.read_event()

    def prev(self):
        if self.uid_current ==0:
            log.warning(f'attemp to read event {self.uid_current}')
            return self.gEvent
        self.uid_current -=1
        return self.read_event()


    def read_geometry(self):
        if 'geometry' in self.h5_file.keys():
            geometry = {}
            geometry_folder = self.h5_file['geometry']
            geometry['geom']                 = geometry_folder['geom'][:]
            geometry['bounding_box_subcluster'] = geometry_folder['bounding_box_subcluster'][:]
            geometry['bounding_box_cluster'] = geometry_folder['bounding_box_cluster'][:]
            geometry['det_normals']          = geometry_folder['det_normals'][:]
            self.geometry = geometry
            return self.geometry
        else:
            return None

    def print_event(self,event):
        self.gEvent.print_event(event)

    def read_prod_header(self):
        if 'ProductionHeader' in self.h5_file.keys():
            h5folder = self.h5_file['ProductionHeader']
            prod_header = self.gEvent.prodHeader
            prod_header.n_events_original = h5folder['n_events_original'][()]
            prod_header.n_events_cloned   = h5folder['n_events_cloned'][()]
            prod_header.n_events_total    = h5folder['n_events_total'][()]
            prod_header.primary_generator = '' # FIXME from here
            prod_header.primary_propagators = []
            prod_header.photon_propagator = ''
            prod_header.ray_tracer = ''
            prod_header.cloner = ''
            prod_header.photons_n_scatterings = 0
            prod_header.photons_wave_range = []
            prod_header.cloner_accumulate_hits = '' # FIXME to here (-1 was)
            prod_header.medium_scattering_model = h5folder['medium_scattering_model'][()].decode()
            prod_header.medium_anisotropy = h5folder['medium_anisotropy'][()]
            return self.gEvent.prodHeader
        else:
            return None

    def read_event_header(self,event_number):
        event_folder     = self.get_event_folder(event_number)
        evtHeader_folder = event_folder['event_header']
        # check if this evtHeader was read already
        if self.evtHeader_folder == evtHeader_folder:
            return self.gEvent.evtHeader

        if 'event_header' in event_folder.keys():
            event_header = self.gEvent.evtHeader
            event_header.photons_sampling_weight = evtHeader_folder['photons_sampling_weight'][()]
            event_header.om_area_weight          = evtHeader_folder['om_area_weight'][()]
            event_header.n_bunches               = evtHeader_folder['n_bunches'][()]
            event_header.n_photons_total         = evtHeader_folder['n_photons_total'][()]
            self.evtHeader_folder = evtHeader_folder
            return self.gEvent.evtHeader

    def get_event_folder(self,event_number):
        e = False
        node = f'event_{event_number}'
        #print('node', node, '\n',self.h5_file.keys() )
        if node in self.h5_file.keys():
            event_folder = self.h5_file[node]
            e = True
            return event_folder
        if not e:
            log.warning(f'read_event. node {node} does not exist. skip it')
            return None

    def read_event(self):
        event = self.event_current = self.uid[self.uid_current][0]
        clone = self.clone_current = self.uid[self.uid_current][1]
        log.info(f'reading event={self.event_current}, clone={self.clone_current}')

        if self.read_event_header_flag:
            self.read_event_header(event)
        if self.read_event_photons_flag:
            self.read_photons(event)
        if self.read_event_hits_flag:
            self.read_hits(event,clone)
        if self.read_event_tracks_flag:
            self.read_tracks(event)
        if self.read_event_particles_flag:
            self.read_particles(event)
        return self.gEvent

    def read_hits(self,event_number,clone_id=None):
        event_folder = self.get_event_folder(event_number)
        if 'hits' not in event_folder:
            log.info("no hits to read")
            return None
        hit_folder = event_folder['hits']
        #print('hit_folder',hit_folder.keys())
        if clone_id == None:
            self.current_clone =  -1
            if "all_hits" in hit_folder.keys():
                label = "all_hits"
            elif "clone_0" in hit_folder.keys(): ##FIXME
                label = "clone_0"
            else:
                label = list(hit_folder.keys())[0]
        else:
            label = f"clone_{clone_id}"
            self.current_clone = clone_id
        log.info(f"reading hits '{label}'")
        # check if hits are read already
        if self.gEvent.hits_folder == hit_folder[label]:
            return self.gEvent.hits
        # read hits here
        self.gEvent.hits_folder = hit_folder[label]
        data = self.gEvent.hits_folder[:]
        df = pd.DataFrame(data=data)
        h = df.to_records(index=False)
        hits = {}
        for uid in df.uid.unique():
            hits[uid] = h[h['uid'] == uid]
            self.gEvent.hits = hits
        return self.gEvent.hits


    def read_tracks(self,event_number):
        event_folder = self.get_event_folder(event_number)
        if 'tracks' not in event_folder.keys():
            log.info("no tracks to read")
            return None
        track_folder = event_folder['tracks']
        # check if tracks are read already
        if self.gEvent.tracks_folder == track_folder and self.change_flag != True:
            return self.gEvent.tracks

        self.gEvent.tracks_folder = track_folder
        tracks = {}
        for label in track_folder.keys():
            log.info(f"reading tracks '{label}'")
            init_track = track_folder[label][0]
            data = track_folder[label][:]
            data = data[ np.where(data['E_GeV'] > init_track[-1]*self.opts.min_energy_for_tracks) ]
            df = pd.DataFrame(data=data)
            h = df.to_records(index=False)
            for uid in df.uid.unique():
                tracks[uid] = h[h['uid'] == uid] #.to_numpy()
        self.gEvent.tracks = tracks
        return self.gEvent.tracks

    def read_particles(self,event_number):
        event_folder = self.get_event_folder(event_number)
        if 'particles' not in event_folder.keys():
            log.info("no particles to read")
            return None
        particle_folder = event_folder['particles']
        # check if tracks are read already
        if self.gEvent.particles_folder == particle_folder:
            return self.gEvent.particles

        self.gEvent.particles_folder = particle_folder

        type_of_particles = {}
        for label in particle_folder.keys():
            particles = {}
            log.info(f"reading particles '{label}'")
            data = particle_folder[label][:]
            df = pd.DataFrame(data=data)
            h = df.to_records(index=False)
            for uid in df:
                particles[uid] = h[uid] #.to_numpy()
            type_of_particles[label] = particles
#        self.gEvent.particles =  particles
        self.gEvent.particles = type_of_particles
        return self.gEvent.particles


    def read_photons(self,event_number):
        #  check existence
        event_folder    = self.get_event_folder(event_number)
        n_bunches       = event_folder['event_header/n_bunches'][()]
        n_photons_total = event_folder['event_header/n_photons_total'][()]
        photon_folder = event_folder['photons']
        # check if photons are read already
        if self.gEvent.photons_folder == photon_folder:
            return self.gEvent.photons

        self.gEvent.photons_folder = photon_folder
        photons = gPhotons()
        if n_photons_total>self.n_photons_max:
            fraction = np.float64(self.n_photons_max/n_photons_total)
            log.debug(f'fraction={fraction}')
        for bunch in range(n_bunches):
            weight     = photon_folder[f'photons_{bunch}/weight'][()]
            n_tracks   = photon_folder[f'photons_{bunch}/n_tracks'][()]
            n_steps    = photon_folder[f'photons_{bunch}/n_steps'][()]
            r          = photon_folder[f'photons_{bunch}/r'][:]
            t          = photon_folder[f'photons_{bunch}/t'][:]
            dir        = photon_folder[f'photons_{bunch}/dir'][:]
            wavelength = photon_folder[f'photons_{bunch}/wavelength'][:]
            progenitor = photon_folder[f'photons_{bunch}/progenitor'][:]
            ta         = photon_folder[f'photons_{bunch}/ta'][:]
            ts         = photon_folder[f'photons_{bunch}/ts'][:]
            #
            # if we want to show only a fraction of all photons
            if n_photons_total>self.n_photons_max:
                n_tracks       = photon_folder[f'photons_{bunch}/n_tracks'][()]
                tracks_to_read = np.int(n_tracks*fraction)
                log.debug(f'tracks_to_read={tracks_to_read}, n_tracks={n_tracks}')
                indices = rng.integers(0,n_tracks,size=tracks_to_read)
                indices = np.sort(indices)
                log.debug(f'indices={indices}')
                log.debug(f'indices: {np.all(indices[1:] >= indices[:-1], axis=0)}')
                r = r[:,indices,:]
                t = t[:,indices]
                dir = dir[:,indices,:]
                wavelength = wavelength[indices]
                ta = ta[indices]
                ts = ts[indices]
            #
            photons = photons.add_photons(n_tracks,n_steps,r,t,dir,wavelength,progenitor,ta,ts,weight)
        self.gEvent.photons = photons
        return self.gEvent.photons
