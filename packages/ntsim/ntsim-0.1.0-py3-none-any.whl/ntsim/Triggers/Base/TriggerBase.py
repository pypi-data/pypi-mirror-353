import numpy as np
import logging
import abc

from ntsim.Base.BaseConfig import BaseConfig
from ntsim.IO.ShortHits import ShortHits
from ntsim.IO.gHits import gHits

class TriggerBase(BaseConfig):
    
    def __init__(self, label: str):
        self._label = label
        
        self._trigger_conditions = []
        self._trigger_options    = []
        self._trigger_hits       = None
        
        self.logger_trigger = logging.getLogger(f'NTSim.{self.__class__.__name__}')
        self.logger_trigger.info("Initialized Trigger")
    
    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, new_label):
        self._label = new_label
    
    @property
    def trigger_conditions(self):
        return self._trigger_conditions
    
    @trigger_conditions.setter
    def trigger_conditions(self, new_trigger_conditions):
        self._trigger_conditions.append(new_trigger_conditions)
    
    @property
    def trigger_options(self):
        return self._trigger_options
    
    @trigger_options.setter
    def trigger_options(self, new_trigger_options):
        self._trigger_options.append(new_trigger_options)
    
    @property
    def trigger_hits(self):
        return self._trigger_hits
    
    @trigger_hits.setter
    def trigger_hits(self, new_trigger_hits):
        self._trigger_hits = new_trigger_hits
    
    def add_trigger(self, condition_function, trigger_options):
        self.trigger_conditions = condition_function
        self.trigger_options    = trigger_options
    
    @abc.abstractmethod
    def set_triggers(self) -> None:
        pass
    
    def apply_trigger_conditions(self, ahits: gHits):
        
        for trigger in self.trigger_conditions:
            ahits = trigger(ahits)

        self.trigger_hits = ahits