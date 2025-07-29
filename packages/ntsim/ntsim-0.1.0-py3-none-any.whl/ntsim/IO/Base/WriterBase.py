import abc
from ntsim.Base.BaseConfig import BaseConfig

class WriterBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name

        import logging
        self.log = logging.getLogger(name)
        self.log.info("Initialized Propagator")

    @abc.abstractmethod
    def open_file(self):
        pass

    @abc.abstractmethod
    def write_data(self, event):
        pass
    
    @abc.abstractmethod
    def close_file(self):
        pass