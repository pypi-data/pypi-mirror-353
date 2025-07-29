import abc

from ntsim.Base.BaseConfig import BaseConfig
from ntsim.IO.ShortHits import ShortHits

class AnalysisBase(BaseConfig):
    
    def __init__(self, label: str):
        self._label = label
    
    @abc.abstractmethod
    def analysis(self, hits: ShortHits):
        pass
    
    @abc.abstractmethod
    def save_analysis(self):
        pass