import numpy as np
import logging

from ntsim.IO.ShortHits import ShortHits

log = logging.getLogger('Hits')

class gHits():
    
    def __init__(self, label: str = '') -> None:
        self._label                = label
        
        self._n_hits               = 0
        self._unique_id            = np.empty(shape=(0),dtype=int)
        
        self._time_ns              = np.empty(shape=(0),dtype=int)
        self._position_m           = np.empty(shape=(0,3),dtype=int)
        
        self._weight_no_absorption = np.empty(shape=(0),dtype=int)
        
        self._photon_id            = np.empty(shape=(0),dtype=int)
        self._self_weight          = np.empty(shape=(0),dtype=int)
        
        self._effects              = np.empty(shape=(0,0),dtype=float)
        self._effects_names        = np.empty(shape=(0),dtype=str)
        
        self._phe                  = np.empty(shape=(0),dtype=float)
    
    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, new_label):
        self._label = new_label
    
    @property
    def n_hits(self):
        return self._n_hits
    
    @n_hits.setter
    def n_hits(self, new_n_hits):
        self._n_hits = new_n_hits
    
    @property
    def unique_id(self):
        return self._unique_id
    
    @unique_id.setter
    def unique_id(self, new_unique_id):
        self._unique_id = new_unique_id
    
    @property
    def cluster(self):
        return self._cluster
    
    @cluster.setter
    def cluster(self, new_cluster):
        self._cluster = new_cluster
    
    @property
    def id_per_cluster(self):
        return self._unique_id
    
    @id_per_cluster.setter
    def id_per_cluster(self, new_id_per_cluster):
        self._id_per_cluster = new_id_per_cluster
    
    @property
    def position_m(self):
        return self._position_m
    
    @position_m.setter
    def position_m(self, new_position_m):
        self._position_m = new_position_m
    
    @property
    def time_ns(self):
        return self._time_ns
    
    @time_ns.setter
    def time_ns(self, new_time_ns):
        self._time_ns = new_time_ns
    
    @property
    def weight_no_absorption(self):
        return self._weight_no_absorption
    
    @weight_no_absorption.setter
    def weight_no_absorption(self, new_weight_no_absorption):
        self._weight_no_absorption = new_weight_no_absorption
    
    @property
    def outside_mask(self):
        return self._outside_mask
    
    @outside_mask.setter
    def outside_mask(self, new_outside_mask):
        self._outside_mask = new_outside_mask
    
    @property
    def photon_id(self):
        return self._photon_id
    
    @photon_id.setter
    def photon_id(self, new_photon_id):
        self._photon_id = new_photon_id
    
    @property
    def step_number(self):
        return self._step_number
    
    @step_number.setter
    def step_number(self, new_step_number):
        self._step_number = new_step_number
    
    @property
    def self_weight(self):
        return self._self_weight
    
    @self_weight.setter
    def self_weight(self, new_self_weight):
        self._self_weight = new_self_weight
    
    @property
    def effects(self):
        return self._effects
    
    @effects.setter
    def effects(self, new_effects):
        self._effects.resize((self._effects.shape[0],np.shape(new_effects)[1]))
        self._effects = np.row_stack((self._effects,new_effects))
    
    @property
    def effects_names(self):
        return self._effects_names
    
    @effects_names.setter
    def effects_names(self, new_effects_names):
        self._effects_names = new_effects_names
    
    @property
    def phe(self):
        return self._phe
    
    @phe.setter
    def phe(self, new_phe):
        self._phe = new_phe
    
    def add_hits(self, new_uid: int, new_time_ns: float, x_m: float, y_m: float, z_m: float,
                 new_photon_id: int, new_w_noabs: float, new_self_weight: float,
                 *new_effects: float, new_effects_names: str) -> None:
        
        self.n_hits              += len(new_uid)
        self.unique_id            = np.append(self.unique_id,new_uid)
        
        self.time_ns              = np.append(self.time_ns,new_time_ns)
        
        self.position_m           = np.row_stack((self.position_m,np.row_stack((x_m,y_m,z_m)).T))
        
        self.weight_no_absorption = np.append(self.weight_no_absorption,new_w_noabs)
        
        self.photon_id            = np.append(self.photon_id,new_photon_id)
        self.self_weight          = np.append(self.self_weight,new_self_weight)
        
        self.effects              = list(map(list,zip(*new_effects)))
        self.effects_names        = new_effects_names
        
        # print(self.effects)
        # print(self.weight_no_absorption)
        # print(self.self_weight)
        self.phe                  = np.prod(self.effects,axis=1)*self.weight_no_absorption*self.self_weight
    
    def has_hits(self):
        return len(self._unique_id) > 0
    
    def get_named_data(self) -> np.ndarray:
        data_type  = [('uid',int),('time_ns',float),('x_m',float),('y_m',float),('z_m',float)] + \
                     [('photon_id',int),('w_noabs',float),('self_weight',float)] + \
                     [(name, float) for name in self.effects_names] + \
                     [('phe', float)]
        data_list  = np.column_stack((self.unique_id,self.time_ns,self.position_m,
                                      self.photon_id,self.weight_no_absorption,self.self_weight,
                                      self.effects,self.phe))
        named_data = np.array([tuple(_) for _ in data_list],dtype=data_type)
        
        return named_data
    
    def convert2short(self) -> ShortHits:
        short_hits = ShortHits(self.label)
        short_hits.add_hits(new_uid     = self.unique_id,
                            new_time_ns = self.time_ns,
                            new_phe     = self.phe)
        
        return short_hits