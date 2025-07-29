import numpy as np
import logging
log = logging.getLogger('Hits')

class ShortHits():
    
    def __init__(self, label: str = '') -> None:
        self._label     = label
        
        self._unique_id = np.empty(shape=(0),dtype=int)
        self._time_ns   = np.empty(shape=(0),dtype=float)
        self._phe       = np.empty(shape=(0),dtype=float)
    
    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, new_label):
        self._label = new_label
    
    @property
    def unique_id(self):
        return self._unique_id
    
    @unique_id.setter
    def unique_id(self, new_unique_id):
        self._unique_id = new_unique_id
    
    @property
    def time_ns(self):
        return self._time_ns
    
    @time_ns.setter
    def time_ns(self, new_time_ns):
        self._time_ns = new_time_ns
    
    @property
    def phe(self):
        return self._phe
    
    @phe.setter
    def phe(self, new_phe):
        self._phe = new_phe
    
    def add_hits(self, new_uid: int, new_time_ns: float, new_phe: float) -> None:
        
        assert np.shape(new_uid) == np.shape(new_time_ns) == np.shape(new_phe)
        
        self.unique_id = np.append(self.unique_id,new_uid)
        self.time_ns   = np.append(self.time_ns,new_time_ns)
        self.phe       = np.append(self.phe,new_phe)
    
    def transform_uid_hits(self, new_uid: int, new_time_ns: float, new_phe: float) -> None:
        
        uids = set(new_uid)
        
        if len(uids) == 1:
            
            mask_uid = self.unique_id != uids
            
            self.unique_id = self.unique_id[mask_uid]
            self.time_ns   = self.time_ns[mask_uid]
            self.phe       = self.phe[mask_uid]
            
            self.unique_id = np.append(self.unique_id,new_uid)
            self.time_ns   = np.append(self.time_ns,new_time_ns)
            self.phe       = np.append(self.phe,new_phe)
        
        else:
            
            for uid in uids:
                mask_input_uid   = new_uid == uid
                mask_current_uid = self.unique_id != uid
                
                self.unique_id = self.unique_id[mask_current_uid]
                self.time_ns   = self.time_ns[mask_current_uid]
                self.phe       = self.phe[mask_current_uid]
                
                self.unique_id = np.append(self.unique_id,new_uid[mask_input_uid])
                self.time_ns   = np.append(self.time_ns,new_time_ns[mask_input_uid])
                self.phe       = np.append(self.phe,new_phe[mask_input_uid])
    
    def has_hits(self):
        return len(self._unique_id) > 0
    
    def get_named_data(self) -> np.ndarray:
        data_type  = [('uid',int),('time_ns',float),('phe',float)]
        data_list  = np.column_stack((self.unique_id,self.time_ns,self.phe))
        named_data = np.array([tuple(_) for _ in data_list],dtype=data_type)
        
        return named_data