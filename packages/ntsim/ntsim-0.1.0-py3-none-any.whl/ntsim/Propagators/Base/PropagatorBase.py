import abc
from ntsim.Base.BaseConfig import BaseConfig

class PropagatorBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name
        
        import logging
        self.logger_propagator = logging.getLogger(f'NTSim.{self.__class__.__name__}')
        self.logger_propagator.info(f'Initialized Propagagtor')

    @abc.abstractmethod
    def propagate(self, event):
        pass
