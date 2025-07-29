import abc
from ntsim.Base.BaseConfig import BaseConfig

class CherenkovBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name

        import logging
        self.logger_cherenkov = logging.getLogger(f'NTSim.{self.__class__.__name__}')
        self.logger_cherenkov.info("Initialized Cherenkov Generator")

    @abc.abstractmethod
    def generate(self, event):
        pass