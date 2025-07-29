import abc
from ntsim.Base.BaseConfig import BaseConfig

class CloneBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name

        import logging
        self.log = logging.getLogger(name)
        self.log.info("Initialized Clone Generator")

    @abc.abstractmethod
    def generate_cloned_photons(self, event):
        return 