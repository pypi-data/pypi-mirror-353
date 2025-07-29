from ntsim.Analysis.Base.AnalysisBase import AnalysisBase
from ntsim.IO.ShortHits import ShortHits
from ntsim.IO.gEvent import gEvent

class TriggerAnalysis(AnalysisBase):
    arg_dict = {
        'time_window': {'type': float, 'nargs': 2, 'default': [0.,1_000_000], 'help': ''}
    }
    
    def analysis(self, event: gEvent) -> None:
        
        for hits in event.hits:
        
            output_hits = ShortHits(hits.label)
            hits_data = hits.get_named_data()
            
            low_time_bound = self.time_window[0]
            top_time_bound = self.time_window[1]
            
            low_mask = hits_data['time_ns'] >= low_time_bound
            top_mask = hits_data['time_ns'] <= top_time_bound
            tot_mask = low_mask & top_mask
            
            hits_data = hits_data[tot_mask]
            
            output_hits.add_hits(new_uid     = hits_data['uid'],
                                 new_time_ns = hits_data['time_ns'],
                                 new_phe     = hits_data['phe'])
    
    def save_analysis(self):
        
        pass