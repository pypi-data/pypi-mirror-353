import numpy as np

from ntsim.IO import ShortHits
from ntsim.Triggers.Base.TriggerBase import TriggerBase
from ntsim.IO.ShortHits import ShortHits
from ntsim.IO.gHits import gHits

class BGVDTestTrigger(TriggerBase):
    arg_dict = {'time_resolution_ns': {'type': float, 'default': 1., 'help': ''},
                'phe_real_magnitude': {'type': float, 'default': 1., 'help': ''}
               }
    
    def time_resolution(self, event_hits: gHits):
        
        if not event_hits.has_hits():
            return gHits('no_event')
        
        output_hits = ShortHits(event_hits.label)
        
        hits_data        = np.sort(event_hits.get_named_data(),order='time_ns')
        hitted_detectors = set(hits_data['uid'])
        
        n_time_intervals = np.ceil(np.max(hits_data['time_ns'])/self.time_resolution_ns)+1
        time_bins = np.arange(n_time_intervals)*self.time_resolution_ns
        
        for det_uid in hitted_detectors:
            mask_uid = hits_data['uid'] == det_uid
            
            hits_time_uid = hits_data['time_ns'][mask_uid]
            hits_phe_uid  = hits_data['phe'][mask_uid]
            
            digitize_hits_values, digitize_time_edges = np.histogram(hits_time_uid,time_bins,weights=hits_phe_uid)
            
            digitize_hits_index = np.where(digitize_hits_values != 0)[0]
            
            digitize_hits_values = digitize_hits_values[digitize_hits_index]
            digitize_time_edges  = digitize_time_edges[1:][digitize_hits_index]
            
            for i in range(len(digitize_hits_values)):
                
                output_hits.add_hits(new_uid     = det_uid,
                                     new_time_ns = np.mean(digitize_time_edges[i]),
                                     new_phe     = np.sum(digitize_hits_values[i]))
        
        phe_real = np.random.poisson(lam=output_hits.phe, size=len(output_hits.phe))
        
        self.logger_trigger.info('Applied Time Resolution')
        
        if np.all(phe_real < self.phe_real_magnitude):
            return gHits('no_event')
        
        return event_hits
    
    def set_triggers(self) -> None:
        self.add_trigger(condition_function=self.time_resolution,
                         trigger_options=np.array([self.time_resolution_ns,
                                                   self.phe_real_magnitude]))
        
        self.logger_trigger.info('Setted Triggers')