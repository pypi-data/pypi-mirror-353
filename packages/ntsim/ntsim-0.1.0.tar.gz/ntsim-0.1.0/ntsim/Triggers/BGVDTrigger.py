import numpy as np

from ntsim.Triggers.Base.TriggerBase import TriggerBase
from ntsim.IO.ShortHits import ShortHits
from ntsim.IO.gHits import gHits

class BGVDTrigger(TriggerBase):
    arg_dict = {
        'transit_time_spread_ns': {'type': float, 'default': 3.4, 'help': ''},
        'trigger_time_window_ns': {'type': float, 'default': 100., 'help': ''},
        'analysis_time_window_ns': {'type': float, 'default': 5000., 'help': ''},
        'magnitude_low_high_hits': {'type': float, 'nargs': 2, 'default': [1.7,3.5], 'help': ''}
    }
    
    def transit_time_spread(self, event_hits: gHits):
        
        event_hits  = event_hits.convert2short()
        output_hits = ShortHits(event_hits.label)
        
        hits_data        = np.sort(event_hits.get_named_data(),order='time_ns')
        hitted_detectors = set(hits_data['uid'])
        
        for det_uid in hitted_detectors:
            mask_uid = hits_data['uid'] == det_uid
            
            hits_time_uid = hits_data['time_ns'][mask_uid]
            hits_phe_uid  = hits_data['phe'][mask_uid]
            
            diff_hits_time_uid = np.diff(hits_time_uid)
            
            mask_trans_time = np.argwhere(diff_hits_time_uid >= self.transit_time_spread_ns)
            
            trans_time_window = np.split(hits_time_uid,np.ravel(mask_trans_time+1))
            phe_window        = np.split(hits_phe_uid,np.ravel(mask_trans_time+1))
            
            for i in range(len(trans_time_window)):
                
                output_hits.add_hits(new_uid     = det_uid,
                                     new_time_ns = np.mean(trans_time_window[i]),
                                     new_phe     = np.sum(phe_window[i]))
        
        self.logger_trigger.info('Applied Transit Time Spread')
        return output_hits
    
    def trigger_one_cluster(self, event_hits: ShortHits):
        
        output_hits = ShortHits(event_hits.label)
        hits_data = np.sort(event_hits.get_named_data(),order='time_ns')
        
        hitted_detectors = hits_data['uid']
        
        n_clusters = set(hitted_detectors // 10000)
        
        for n_cluster in n_clusters:
            min_time = 0.
            
            cluster_hit = hits_data[hits_data['uid'] // 10000 == n_cluster]
            
            hits_low  = cluster_hit[cluster_hit['phe'] >= self.magnitude_low_high_hits[0]]
            
            n_string_sections = set(hitted_detectors // 100)
            
            for n_string_section in n_string_sections:
                string_section_hit = hits_low[hits_low['uid'] // 100 == n_string_section]
                
                if len(string_section_hit) <= 1: continue
                
                for i in range(len(string_section_hit)-1):
                    hit_om = string_section_hit[i]
                    another_oms = string_section_hit[i+1:]
                    
                    mask_om = np.abs(another_oms['uid'] - hit_om['uid']) == 1
                    mask_time = np.abs(another_oms['time_ns'] - hit_om['time_ns']) <= self.trigger_time_window_ns
                    
                    if hit_om['phe'] >= self.magnitude_low_high_hits[1]:
#                        mask_phe = np.full_like(mask_om,fill_value=True,dtype=bool)
                        mask_phe = [True]*len(mask_om)
                    else:
                        mask_phe = another_oms['phe'] >= self.magnitude_low_high_hits[1]
                    
                    mask_total = (mask_om & mask_time & mask_phe)
                    
                    another_oms = another_oms[mask_total]
                    
                    if not len(another_oms): continue
                    
                    if not min_time:
                        min_time = np.min([hit_om['time_ns'],*another_oms['time_ns']])
                        
                    tmp_min_time = np.min([hit_om['time_ns'],*another_oms['time_ns']])
                    
                    if tmp_min_time <= min_time:
                        min_time = tmp_min_time
            
            if not min_time: continue
#            cluster_hit['time_ns'] -= min_time
            mask_min = cluster_hit['time_ns'] >= min_time
            mask_max = cluster_hit['time_ns'] <= self.analysis_time_window_ns
            
            cluster_hit = cluster_hit[mask_min & mask_max]
            
            output_hits.add_hits(new_uid     = cluster_hit['uid'],
                                 new_time_ns = cluster_hit['time_ns'],
                                 new_phe     = cluster_hit['phe'])
            
        self.logger_trigger.info('Applied Trigger One Cluster')
        return output_hits
    
    def set_triggers(self) -> None:
        self.add_trigger(condition_function=self.transit_time_spread,
                         trigger_options=np.array([self.transit_time_spread_ns]))
        self.add_trigger(condition_function=self.trigger_one_cluster,
                         trigger_options=np.array([self.trigger_time_window_ns,
                                                   self.analysis_time_window_ns,
                                                   self.magnitude_low_high_hits[0],
                                                   self.magnitude_low_high_hits[1]]))
        
        self.logger_trigger.info('Setted Triggers')
        
        