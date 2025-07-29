import numpy as np
import logging
log = logging.getLogger('Particles')

class gPhotons():
    def __init__(self, label: str = '') -> None:
        self._label         = label
        
        self._n_photons     = 0
        self._n_steps       = 0
        
        self._position_m    = np.empty(shape=(0,0,3),dtype=float)
        self._t_ns          = np.empty(shape=(0,0),dtype=float)
        self._direction     = np.empty(shape=(0,0,3),dtype=float)

        self._wavelength_nm = np.empty(shape=(0),dtype=float)
        self._progenitor    = np.empty(shape=(0),dtype=float)
        
        self._ta_ns         = np.empty(shape=(0),dtype=float)
        self._ts_ns         = np.empty(shape=(0),dtype=float)

        self._weight        = 0
    
    @property
    def label(self):
        return self._label
    
    @property
    def n_photons(self):
        return self._n_photons
    
    @n_photons.setter
    def n_photons(self, new_n_photons):
        self._n_photons = new_n_photons
    
    @property
    def scattering_steps(self):
        return self._n_steps
    
    @scattering_steps.setter
    def scattering_steps(self, new_n_steps):
        self._n_steps = new_n_steps
        self.position_m.resize(self._n_steps,self.n_photons,3)
        self.time_ns.resize(self._n_steps,self.n_photons)
        self.direction.resize(self._n_steps,self.n_photons,3)
    
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
    def wavelength_nm(self):
        return self._wavelength_nm
    
    @wavelength_nm.setter
    def wavelength_nm(self, new_wavelength_nm):
        self._wavelength_nm = new_wavelength_nm
    
    @property
    def progenitor(self):
        return self._progenitor
    
    @progenitor.setter
    def progenitor(self, new_progenitor):
        self._progenitor = new_progenitor
    
    @property
    def absorption_time_ns(self):
        return self._ta_ns
    
    @absorption_time_ns.setter
    def absorption_time_ns(self, new_ta_ns):
        self._ta_ns = new_ta_ns
    
    @property
    def scattering_time_ns(self):
        return self._ts_ns
    
    @scattering_time_ns.setter
    def scattering_time_ns(self, new_ts_ns):
        self._ts_ns = new_ts_ns
    
    @property
    def weight(self):
        return self._weight
    
    @weight.setter
    def weight(self, new_weight):
        self._weight = new_weight
    
    def add_photons(self, new_n_photons: int, new_n_steps: int, new_position_m: list, \
        new_t_ns: float, new_direction: list, new_wavelength_nm: list, new_progenitor: list, \
        new_ta: list = [], new_ts: list = [], *, new_weight: int) -> None:
        
        self.n_photons += new_n_photons
        
        if not self.scattering_steps: self.scattering_steps = new_n_steps
        assert self.scattering_steps == new_n_steps
        
        self.position_m[:,-new_n_photons:] = new_position_m
        self.time_ns[:,-new_n_photons:]    = new_t_ns
        self.direction[:,-new_n_photons:]  = new_direction
        
        self.wavelength_nm = np.concatenate((self.wavelength_nm,new_wavelength_nm),axis=0)
        self.progenitor    = np.concatenate((self.progenitor,new_progenitor),axis=0)
        
        if np.size(new_ta):
            self.absorption_time_ns = np.concatenate((self.absorption_time_ns,new_ta),axis=0)
        else:
            self.absorption_time_ns = np.zeros(shape=(self.n_photons))
        if np.size(new_ts):
            self.scattering_time_ns = np.concatenate((self.scattering_time_ns,new_ts),axis=0)
        else:
            self.scattering_time_ns = np.zeros(shape=(self.n_photons))
        
        self.weight = np.full(shape=(self.n_photons),fill_value=new_weight)
    
    def has_photons(self):
        return self.n_photons > 0