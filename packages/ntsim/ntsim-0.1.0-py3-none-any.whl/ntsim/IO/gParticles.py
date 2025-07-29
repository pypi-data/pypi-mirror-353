from types import NoneType
import numpy as np
import logging
logger = logging.getLogger('Particles')

class gParticles():
    def __init__(self, label: str = '') -> None:
        self._label            = label
        
        self._unique_id        = np.empty(shape=(0),dtype=int)
        self._parent_uid       = np.empty(shape=(0),dtype=int)
        self._pdgid            = np.empty(shape=(0),dtype=int)
        
        self._position_m       = np.empty(shape=(0,3),dtype=float)
        self._t_ns             = np.empty(shape=(0),dtype=float)
        self._direction        = np.empty(shape=(0,3),dtype=float)
        
        self._total_energy_GeV = np.empty(shape=(0),dtype=float)
        
        self._process_name     = np.empty(shape=(0),dtype=bytes)
        
        self._status           = np.empty(shape=(0),dtype=int)
    
    @property
    def label(self):
        return self._label
    
    @property
    def unique_id(self):
        if self._unique_id is None:
            raise ValueError("Unique ID has not been initialized!")
        return self._unique_id
    
    @unique_id.setter
    def unique_id(self, new_unique_id):
        self._unique_id = new_unique_id
    
    @property
    def parent_uid(self):
        return self._parent_uid
    
    @parent_uid.setter
    def parent_uid(self, new_parent_uid):
        self._parent_uid = new_parent_uid
    
    @property
    def pdgid(self):
        return self._pdgid
    
    @pdgid.setter
    def pdgid(self, new_pdgid):
        self._pdgid = new_pdgid
    
    @property
    def position_m(self):
        return self._position_m
    
    @position_m.setter
    def position_m(self, new_position_m):
        self._position_m = new_position_m

    @property
    def time_ns(self):
        return self._t_ns
    
    @time_ns.setter
    def time_ns(self, new_time_ns):
        self._t_ns = new_time_ns
    
    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, new_direction):
        self._direction = new_direction
    
    @property
    def total_energy_GeV(self):
        return self._total_energy_GeV
    
    @total_energy_GeV.setter
    def total_energy_GeV(self, new_total_energy_GeV):
        self._total_energy_GeV = new_total_energy_GeV
    
    @property
    def process_name(self):
        return self._process_name
    
    @process_name.setter
    def process_name(self, new_process_name):
        self._process_name = new_process_name
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, new_status):
        self._status = new_status
    
    def get_n_gun_particles(self):
        return len(self.status)
    
    def add_particles(self, new_uid: int, new_parent_uid: int, new_pdgid: int, \
                      new_position_m: list, new_t_ns: float, new_direction: list, new_E_tot_GeV: float, \
                      new_status: int = 0, new_process_name: bytes = None) -> None:
        
        self.unique_id  = np.append(self.unique_id,new_uid)
        self.parent_uid = np.append(self.parent_uid,new_parent_uid)
        self.pdgid      = np.append(self.pdgid,new_pdgid)
        
        self.position_m = np.row_stack((self.position_m,new_position_m))
        self.time_ns    = np.append(self.time_ns,new_t_ns)
        self.direction  = np.row_stack((self.direction,new_direction))
        
        self.total_energy_GeV = np.append(self.total_energy_GeV,new_E_tot_GeV)
        
        if type(new_process_name) != NoneType:
            self.process_name = np.append(self.process_name,new_process_name)
        
        self.status = np.append(self.status,new_status)
    
    def has_particles(self):
        return len(self.parent_uid) > 0
        
    def get_named_data(self) -> np.ndarray:
        
        data_type  = [('uid',int),('parent_uid',int),('pdgid',int),('x_m',float),('y_m',float),('z_m',float),('time_ns',float),
                      ('dir_x',float),('dir_y',float),('dir_z',float),('E_tot_GeV',float),('status',int)]
        data_list  = np.column_stack((self.unique_id,self.parent_uid,self.pdgid,self.position_m,
                                      self.time_ns,self.direction,self.total_energy_GeV,self.status))
        named_data = np.array([tuple(_) for _ in data_list],dtype=data_type)
        if len(self.process_name):
            data_type.append(('process_name','|S10'))
            tmp_named_data = np.empty(shape=named_data.size,dtype=data_type)
            tmp_named_data[['uid','parent_uid','pdgid',
                            'x_m','y_m','z_m','time_ns',
                            'dir_x','dir_y','dir_z',
                            'E_tot_GeV','status']] = named_data
            tmp_named_data['process_name'] = self.process_name
            named_data = tmp_named_data
            
        return named_data